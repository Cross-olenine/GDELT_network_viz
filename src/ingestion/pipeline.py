"""GDELT Events 1.0 ingestion pipeline → Hive-partitioned Parquet.

Fetches daily GDELT export ZIP files (tab-delimited, no header, 58 columns),
transforms them according to docs/data-contracts.md, and writes one
compressed Parquet file per month under:

    data/events/year=YYYY/month=MM/events.parquet

Key behaviours
--------------
- Idempotent: months already written are skipped without re-downloading.
- Parallel downloads: asyncio + httpx with a semaphore capped at
  MAX_CONCURRENT_DOWNLOADS across all concurrent month tasks.
- Atomic writes: DataFrame written to a sibling .tmp file, then renamed;
  a stale .tmp from a previous interrupted run is safely overwritten.
- Resilient: HTTP errors or corrupt ZIPs are logged and skipped; the
  pipeline continues with the remaining days and months.
"""

from __future__ import annotations

import asyncio
import io
import logging
import zipfile
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator

import httpx
import polars as pl
from tqdm.asyncio import tqdm_asyncio

# ── Configuration (override at top of file) ────────────────────────────────────
MAX_CONCURRENT_DOWNLOADS: int = 5
DATA_DIR: Path = Path("data/events")
TMP_DIR: Path = Path("data/tmp")

_ROOT = Path(__file__).parent.parent.parent
_GDELT_BASE = "http://data.gdeltproject.org/events"

# ── GDELT raw schema — 58 columns, tab-delimited, no header ───────────────────
GDELT_COLUMNS: list[str] = [
    "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode",
    "Actor1KnownGroupCode", "Actor1EthnicCode",
    "Actor1Religion1Code", "Actor1Religion2Code",
    "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode",
    "Actor2KnownGroupCode", "Actor2EthnicCode",
    "Actor2Religion1Code", "Actor2Religion2Code",
    "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
    "QuadClass", "GoldsteinScale", "NumMentions", "NumSources", "NumArticles",
    "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code", "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code", "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL",
]

# Columns retained in the output Parquet
KEEP_COLUMNS: list[str] = [
    "GLOBALEVENTID", "SQLDATE",
    "Actor1CountryCode", "Actor2CountryCode",
    "Actor1Name", "Actor2Name",
    "Actor1Type1Code", "Actor2Type1Code",
    "EventCode", "QuadClass", "GoldsteinScale", "NumMentions", "AvgTone",
]

# CAMEO regional codes — not ISO-compatible; excluded from edge_type='strict'.
# Source: user spec + data-contracts.md + cameo_countries.json inspection.
_CAMEO_REGIONAL: frozenset[str] = frozenset({
    "AFR", "MEA", "EUR", "LAM", "NMR", "SEA",
    "BLK", "CAU", "ASA", "SCA", "MDE", "WST", "EEU", "FSU",
    "ASM", "CAF", "CAS", "CEU", "CFR", "EAF", "NAF",
    "SAF", "SAM", "SAS", "WAF", "ZAF",
    "CRB", "EIN", "MDT", "PGS", "SCN",
})

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)


# ── Path helpers ───────────────────────────────────────────────────────────────

def parquet_path(year: int, month: int) -> Path:
    """Return the Hive-partitioned output path for the given year/month.

    Args:
        year:  Four-digit year.
        month: One-based month (1–12).

    Returns:
        Path of the form DATA_DIR/year=YYYY/month=MM/events.parquet.
    """
    return DATA_DIR / f"year={year}" / f"month={month:02d}" / "events.parquet"


def is_done(year: int, month: int) -> bool:
    """Return True if the Parquet for this month already exists on disk."""
    return parquet_path(year, month).exists()


# ── Date iteration ─────────────────────────────────────────────────────────────

def iter_months(start_date: str, end_date: str) -> Iterator[tuple[int, int]]:
    """Yield (year, month) integer tuples from start_date to end_date inclusive.

    Args:
        start_date: ISO date string, e.g. '2024-01-01'.
        end_date:   ISO date string, e.g. '2026-04-30'.

    Yields:
        (year, month) tuples in ascending chronological order.
    """
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        month += 1
        if month > 12:
            month = 1
            year += 1


def iter_days(year: int, month: int) -> Iterator[str]:
    """Yield YYYYMMDD date strings for every calendar day in the given month.

    Args:
        year:  Four-digit year.
        month: One-based month (1–12).

    Yields:
        Date strings formatted as 'YYYYMMDD'.
    """
    d = date(year, month, 1)
    while d.month == month:
        yield d.strftime("%Y%m%d")
        d += timedelta(days=1)


# ── Download ───────────────────────────────────────────────────────────────────

async def download_day(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    date_str: str,
) -> bytes | None:
    """Download the GDELT daily export ZIP for a given date.

    Acquires the shared semaphore before issuing the HTTP request to cap
    overall concurrency across all parallel month tasks.

    Args:
        client:    Shared httpx async client.
        semaphore: Concurrency limiter (MAX_CONCURRENT_DOWNLOADS slots).
        date_str:  Date in 'YYYYMMDD' format.

    Returns:
        Raw ZIP bytes on success, None on HTTP error or network failure.
    """
    url = f"{_GDELT_BASE}/{date_str}.export.CSV.zip"
    async with semaphore:
        log.info("GET  %s", url)
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            log.info("OK   %s — %.0f KB", date_str, len(resp.content) / 1024)
            return resp.content
        except httpx.HTTPStatusError as exc:
            log.error("HTTP %s — %s", exc.response.status_code, url)
        except Exception as exc:
            log.error("Download failed %s: %s", url, exc)
    return None


# ── Parsing ────────────────────────────────────────────────────────────────────

def parse_gdelt_zip(zip_bytes: bytes, date_str: str) -> pl.DataFrame | None:
    """Extract and parse one GDELT daily ZIP into a raw Polars DataFrame.

    All 58 columns are read as strings to preserve leading zeros in event
    codes (EventCode, EventBaseCode, EventRootCode) and avoid numeric
    inference on empty actor-code columns.

    Args:
        zip_bytes: Raw bytes of the GDELT daily ZIP archive.
        date_str:  Date label used in error messages.

    Returns:
        58-column all-string DataFrame, or None if the archive is corrupt
        or the CSV is unparseable.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            names = zf.namelist()
            if not names:
                log.error("Empty ZIP for %s", date_str)
                return None
            with zf.open(names[0]) as csv_file:
                csv_bytes = csv_file.read()
    except zipfile.BadZipFile as exc:
        log.error("Bad ZIP for %s: %s", date_str, exc)
        return None

    try:
        df = pl.read_csv(
            io.BytesIO(csv_bytes),
            separator="\t",
            has_header=False,
            new_columns=GDELT_COLUMNS,
            infer_schema_length=0,  # read all columns as Utf8
        )
        log.info("Parsed %s: %d rows", date_str, len(df))
        return df
    except Exception as exc:
        log.error("CSV parse error for %s: %s", date_str, exc)
        return None


# ── Transformation ─────────────────────────────────────────────────────────────

def transform(df: pl.DataFrame) -> pl.DataFrame:
    """Apply GDELT data contracts: filter, cast, select, and derive columns.

    Steps performed in order:
    1. Exclude rows with no usable actor information.
    2. Cast numeric columns from string.
    3. Select the 13 columns required for the network graph.
    4. Derive goldstein_category, is_internal, edge_type, year, month.

    Args:
        df: Raw 58-column DataFrame with all-string schema produced by
            parse_gdelt_zip. Empty fields are empty strings, not nulls.

    Returns:
        Processed DataFrame with 18 columns (13 source + 5 derived).
        Output schema: actor codes and EventCode remain strings.
    """
    # 1. Exclude rows with zero actor information
    no_info = (
        (pl.col("Actor1CountryCode") == "")
        & (pl.col("Actor2CountryCode") == "")
        & (pl.col("Actor1Name") == "")
        & (pl.col("Actor2Name") == "")
    )
    df = df.filter(~no_info)

    # 2. Cast numeric columns (strict=False converts parse errors to null)
    df = df.with_columns([
        pl.col("GoldsteinScale").cast(pl.Float64, strict=False),
        pl.col("NumMentions").cast(pl.Int64, strict=False),
        pl.col("QuadClass").cast(pl.Int64, strict=False),
        pl.col("AvgTone").cast(pl.Float64, strict=False),
    ])

    # 3. Select target columns
    df = df.select(KEEP_COLUMNS)

    # 4. Derived columns
    regional = list(_CAMEO_REGIONAL)

    df = df.with_columns([
        pl.when(pl.col("GoldsteinScale") > 0).then(pl.lit("positif"))
          .when(pl.col("GoldsteinScale") < 0).then(pl.lit("negatif"))
          .otherwise(pl.lit("neutre"))
          .alias("goldstein_category"),

        (
            ((pl.col("Actor1CountryCode") == "") & (pl.col("Actor2CountryCode") != ""))
            | (
                (pl.col("Actor1CountryCode") != "")
                & (pl.col("Actor2CountryCode") != "")
                & (pl.col("Actor1CountryCode") == pl.col("Actor2CountryCode"))
            )
        ).alias("is_internal"),

        pl.when(
            (pl.col("Actor1CountryCode") != "")
            & (pl.col("Actor2CountryCode") != "")
            & (~pl.col("Actor1CountryCode").is_in(regional))
            & (~pl.col("Actor2CountryCode").is_in(regional))
        ).then(pl.lit("strict"))
        .otherwise(pl.lit("extended"))
        .alias("edge_type"),

        pl.col("SQLDATE").str.slice(0, 4).alias("year"),
        pl.col("SQLDATE").str.slice(4, 2).alias("month"),
    ])

    return df


# ── Atomic write ───────────────────────────────────────────────────────────────

def _write_parquet_atomic(df: pl.DataFrame, path: Path) -> None:
    """Write a DataFrame to a Parquet file atomically via a sibling .tmp file.

    Creates parent directories if they do not exist. A pre-existing stale
    .tmp from an interrupted previous run is safely overwritten.

    Args:
        df:   DataFrame to persist.
        path: Target .parquet path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.stem + ".tmp")
    df.write_parquet(tmp, compression="zstd")
    tmp.replace(path)  # Path.replace() calls os.replace() — atomic on POSIX,
                       # near-atomic on Windows (same-volume rename)
    log.info("Written %s (%d rows)", path, len(df))


# ── Monthly ingestion task ─────────────────────────────────────────────────────

async def ingest_month(
    year: int,
    month: int,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
) -> None:
    """Download, transform, and write one calendar month of GDELT data.

    Idempotent: if the output Parquet for this month already exists on disk,
    this coroutine returns immediately without issuing any HTTP requests.

    Days within the month are downloaded concurrently (bounded by the shared
    semaphore); Polars concat and write happen synchronously afterwards.

    Args:
        year:      Four-digit calendar year.
        month:     One-based month (1–12).
        client:    Shared httpx async client.
        semaphore: Download concurrency limiter.
    """
    out = parquet_path(year, month)
    if out.exists():
        log.info("Skip %d-%02d (already done)", year, month)
        return

    log.info("Start %d-%02d", year, month)
    days = list(iter_days(year, month))

    download_tasks = [download_day(client, semaphore, d) for d in days]
    zip_results: list[bytes | None] = await asyncio.gather(*download_tasks)

    frames: list[pl.DataFrame] = []
    for day_str, zip_bytes in zip(days, zip_results):
        if zip_bytes is None:
            continue
        raw = parse_gdelt_zip(zip_bytes, day_str)
        if raw is None:
            continue
        frames.append(transform(raw))

    if not frames:
        log.warning("No usable data for %d-%02d — skipping write", year, month)
        return

    combined = pl.concat(frames)
    _write_parquet_atomic(combined, out)
    log.info("Done  %d-%02d: %d rows total", year, month, len(combined))


# ── Pipeline entry point ───────────────────────────────────────────────────────

async def run_pipeline(start_date: str, end_date: str) -> None:
    """Run the full GDELT ingestion pipeline for a date range.

    Schedules one asyncio task per calendar month. HTTP downloads across all
    concurrent tasks share a single semaphore capped at MAX_CONCURRENT_DOWNLOADS.

    Args:
        start_date: First date to ingest, ISO format ('YYYY-MM-DD').
        end_date:   Last date to ingest, inclusive, ISO format.
    """
    months = list(iter_months(start_date, end_date))
    pending = [(y, m) for y, m in months if not is_done(y, m)]

    log.info(
        "Pipeline: %d months in range, %d already done, %d to process",
        len(months),
        len(months) - len(pending),
        len(pending),
    )

    if not pending:
        log.info("Nothing to do.")
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=10.0),
        follow_redirects=True,
    ) as client:
        tasks = [ingest_month(y, m, client, semaphore) for y, m in pending]
        await tqdm_asyncio.gather(*tasks, desc="Months", unit="month")


if __name__ == "__main__":
    asyncio.run(run_pipeline(
        start_date="2024-01-01",
        end_date="2026-04-30",
    ))
