"""Read GDELT Parquet partitions with DuckDB, aggregate edges for the viz.

Strategy: pre-aggregate every event at the (day × actor1 × actor2 ×
category) grain **once per Streamlit session** (cached via
`@st.cache_data`). Every slider movement then becomes an in-memory
pandas filter + groupby on that cached frame, which keeps the UI
responsive regardless of the requested date range.

The math is strictly equivalent to the previous SQL aggregation:
weighted average = SUM(ln(1+NM)·GS) / SUM(ln(1+NM)) decomposes by
sub-period — we just keep the numerator and denominator separately at
the day grain, and sum them back over the chosen range.
"""

from datetime import date
from pathlib import Path
from typing import Literal

import duckdb
import pandas as pd
import streamlit as st

_ROOT = Path(__file__).parent.parent.parent
_EVENTS_DIR = _ROOT / "data" / "events"

GoldsteinFilter = Literal["Tous", "Positif", "Négatif", "Neutre"]
_CATEGORY_MAP = {"Positif": "positif", "Négatif": "negatif", "Neutre": "neutre"}


def _all_parquet_paths() -> list[str]:
    """Return forward-slashed, SQL-safe paths of every Parquet partition on disk.

    Apostrophes are doubled because they delimit string literals in DuckDB —
    the project root contains a real apostrophe ("Cas d'usages").
    """
    return [
        str(p).replace("\\", "/").replace("'", "''")
        for p in sorted(_EVENTS_DIR.glob("year=*/month=*/events.parquet"))
    ]


@st.cache_data(show_spinner="Pré-agrégation des événements (1 fois par session)…")
def load_day_level_edges() -> pd.DataFrame:
    """Aggregate every event to the (day × actor1 × actor2 × category) grain.

    Reads ALL available Parquet partitions in one DuckDB pass. The
    weighted-average score is split into its two compositional pieces
    (weighted_sum, weight_sum) so any sub-range can be re-aggregated
    exactly in-memory without re-reading the Parquet files.
    """
    paths = _all_parquet_paths()
    if not paths:
        return pd.DataFrame(columns=[
            "sqldate", "actor1_code", "actor2_code", "goldstein_category",
            "weighted_sum", "weight_sum", "num_mentions", "event_count",
        ])
    path_list = ", ".join(f"'{p}'" for p in paths)
    query = f"""
    SELECT
        CAST(strptime(SQLDATE, '%Y%m%d') AS DATE) AS sqldate,
        Actor1CountryCode                          AS actor1_code,
        Actor2CountryCode                          AS actor2_code,
        goldstein_category,
        SUM(LN(1 + NumMentions) * GoldsteinScale)  AS weighted_sum,
        SUM(LN(1 + NumMentions))                   AS weight_sum,
        SUM(NumMentions)                           AS num_mentions,
        COUNT(*)                                   AS event_count
    FROM read_parquet([{path_list}])
    WHERE Actor1CountryCode != Actor2CountryCode
      AND edge_type = 'strict'
    GROUP BY sqldate, actor1_code, actor2_code, goldstein_category
    """
    con = duckdb.connect()
    df = con.execute(query).df()
    df["sqldate"] = pd.to_datetime(df["sqldate"])
    return df


@st.cache_data(show_spinner=False)
def available_date_bounds() -> tuple[date, date] | None:
    """Return (min_date, max_date) of SQLDATE across all partitions, or None."""
    df = load_day_level_edges()
    if df.empty:
        return None
    return df["sqldate"].min().date(), df["sqldate"].max().date()


def load_edges_range(
    from_date: date,
    to_date: date,
    goldstein_filter: GoldsteinFilter = "Tous",
) -> list[dict]:
    """Filter the cached day-level frame and re-aggregate over [from_date, to_date].

    The returned per-pair score is the SUM(weighted_sum) / SUM(weight_sum)
    over the requested days — mathematically identical to running the
    original SQL aggregation directly on the raw events of that range.
    """
    df = load_day_level_edges()
    if df.empty:
        return []
    start = pd.Timestamp(from_date)
    end   = pd.Timestamp(to_date)
    mask = (df["sqldate"] >= start) & (df["sqldate"] <= end)
    if goldstein_filter != "Tous":
        mask &= df["goldstein_category"] == _CATEGORY_MAP[goldstein_filter]
    sub = df.loc[mask]
    if sub.empty:
        return []
    agg = sub.groupby(
        ["actor1_code", "actor2_code", "goldstein_category"], as_index=False
    ).agg(
        weighted_sum=("weighted_sum", "sum"),
        weight_sum=("weight_sum", "sum"),
        num_mentions=("num_mentions", "sum"),
        count=("event_count", "sum"),
    )
    agg = agg[agg["weight_sum"] > 0].copy()
    agg["goldstein_scale"] = agg["weighted_sum"] / agg["weight_sum"]
    agg["num_mentions"] = agg["num_mentions"].astype(int)
    agg["count"] = agg["count"].astype(int)
    return agg[[
        "actor1_code", "actor2_code", "goldstein_category",
        "goldstein_scale", "num_mentions", "count",
    ]].to_dict(orient="records")
