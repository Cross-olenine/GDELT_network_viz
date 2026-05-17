"""Read GDELT Parquet partitions with DuckDB, aggregate edges for the viz."""

from pathlib import Path
from typing import Literal

import duckdb

_ROOT = Path(__file__).parent.parent.parent
_EVENTS_DIR = _ROOT / "data" / "events"

GoldsteinFilter = Literal["Tous", "Positif", "Négatif", "Neutre"]

_CATEGORY_MAP = {"Positif": "positif", "Négatif": "negatif", "Neutre": "neutre"}


def list_available_months() -> list[tuple[int, int]]:
    """Return sorted (year, month) tuples for which a Parquet partition exists."""
    months = []
    for p in sorted(_EVENTS_DIR.glob("year=*/month=*/events.parquet")):
        year = int(p.parent.parent.name.split("=")[1])
        month = int(p.parent.name.split("=")[1])
        months.append((year, month))
    return months


def load_edges(year: int, month: int, goldstein_filter: GoldsteinFilter = "Tous") -> list[dict]:
    """Aggregate all strict state-to-state GDELT edges from one month of Parquet data.

    Reads the Hive partition for the given year/month, keeps only strict
    state-to-state edges (edge_type='strict'), and aggregates by
    (actor1_code, actor2_code, goldstein_category) using a log1p(NumMentions)-
    weighted average of GoldsteinScale.

    Args:
        year:             Four-digit year.
        month:            One-based month (1–12).
        goldstein_filter: One of "Tous", "Positif", "Négatif", "Neutre".

    Returns:
        List of dicts with keys: actor1_code, actor2_code,
        goldstein_category, goldstein_scale, num_mentions.
    """
    parquet = _EVENTS_DIR / f"year={year}" / f"month={month:02d}" / "events.parquet"

    cat_clause = ""
    if goldstein_filter != "Tous":
        cat = _CATEGORY_MAP[goldstein_filter]
        cat_clause = f"AND goldstein_category = '{cat}'"

    query = f"""
    SELECT
        Actor1CountryCode AS actor1_code,
        Actor2CountryCode AS actor2_code,
        goldstein_category,
        SUM(LN(1 + NumMentions) * GoldsteinScale)
            / NULLIF(SUM(LN(1 + NumMentions)), 0)  AS goldstein_scale,
        SUM(NumMentions)                             AS num_mentions
    FROM read_parquet('{str(parquet).replace(chr(92), "/").replace("'", "''")}')
    WHERE
        Actor1CountryCode != Actor2CountryCode
        AND edge_type = 'strict'
        {cat_clause}
    GROUP BY actor1_code, actor2_code, goldstein_category
    ORDER BY actor1_code, actor2_code, goldstein_category
    """

    con = duckdb.connect()
    rows = con.execute(query).fetchall()
    cols = ["actor1_code", "actor2_code", "goldstein_category", "goldstein_scale", "num_mentions"]
    return [dict(zip(cols, row)) for row in rows]
