"""Read GDELT Parquet partitions with DuckDB, aggregate edges for the viz."""

from pathlib import Path
from typing import Literal

import duckdb

_ROOT = Path(__file__).parent.parent.parent
_EVENTS_DIR = _ROOT / "data" / "events"

GoldsteinFilter = Literal["Tous", "Positif", "Négatif", "Neutre"]

_CATEGORY_MAP = {"Positif": "positif", "Négatif": "negatif", "Neutre": "neutre"}

_FR_MONTHS = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


def list_available_months() -> list[tuple[int, int]]:
    """Return sorted (year, month) tuples for which a Parquet partition exists."""
    months = []
    for p in sorted(_EVENTS_DIR.glob("year=*/month=*/events.parquet")):
        year = int(p.parent.parent.name.split("=")[1])
        month = int(p.parent.name.split("=")[1])
        months.append((year, month))
    return months


def ym_label(year: int, month: int) -> str:
    """Human-readable month label: 'Janvier 2024'."""
    return f"{_FR_MONTHS[month]} {year}"


def load_edges_range(
    from_ym: tuple[int, int],
    to_ym: tuple[int, int],
    goldstein_filter: GoldsteinFilter = "Tous",
) -> list[dict]:
    """Aggregate strict state-to-state edges over a range of months.

    Reads all Hive partitions in [from_ym, to_ym] inclusive via DuckDB
    hive_partitioning, aggregates by (actor1_code, actor2_code,
    goldstein_category) using log1p(NumMentions)-weighted GoldsteinScale.

    Returns list of dicts: actor1_code, actor2_code, goldstein_category,
    goldstein_scale, num_mentions.
    """
    available = list_available_months()
    selected = [
        (y, m) for y, m in available
        if from_ym <= (y, m) <= to_ym
    ]
    if not selected:
        return []

    # Build list of parquet paths covering the requested range
    paths = [
        str(_EVENTS_DIR / f"year={y}" / f"month={m:02d}" / "events.parquet")
        .replace("\\", "/")
        .replace("'", "''")
        for y, m in selected
    ]
    path_list = ", ".join(f"'{p}'" for p in paths)

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
    FROM read_parquet([{path_list}])
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
