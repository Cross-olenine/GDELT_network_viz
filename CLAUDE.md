# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

GDELT Network Viz — Streamlit app that visualises positive/negative
relationships between countries from GDELT 1.0 Events data. Countries
are nodes positioned on a world map; edges are aggregate scores
between two countries over a selected time range.

Stack: Python ingestion (asyncio + httpx + Polars) → Hive-partitioned
Parquet on disk → DuckDB read layer in the app → Streamlit UI with an
embedded Leaflet + D3 HTML component.

## Commands

- Run the ingestion pipeline (downloads GDELT daily ZIPs and writes one
  Parquet per month under `data/events/year=YYYY/month=MM/`):
  `python src/ingestion/pipeline.py`
  Idempotent — months already written are skipped without re-downloading.
  Date range is hardcoded in `__main__` at the bottom of `pipeline.py`.

- Run the Streamlit app (from repo root):
  `streamlit run src/app/app.py --server.port 8501`

- Run the full test suite (synchronous, no network):
  `pytest tests/`

- Run a single test:
  `pytest tests/test_pipeline.py::test_transform_edge_type_strict`

## Architecture

Three layers, in pipeline order:

1. **Ingestion** (`src/ingestion/pipeline.py`) — `run_pipeline()`
   schedules one asyncio task per calendar month; downloads share a
   single semaphore (`MAX_CONCURRENT_DOWNLOADS = 5`). Each day's ZIP is
   parsed as **all-string** (`infer_schema_length=0`) to preserve
   leading zeros in `EventCode` / `EventBaseCode` / `EventRootCode`,
   then `transform()` applies the data contract: filters rows with no
   usable actor info, casts numerics, derives `goldstein_category`,
   `is_internal`, `edge_type`, `year`, `month`. Output is written
   atomically via `.tmp` → rename.

2. **Storage** — `data/events/year=YYYY/month=MM/events.parquet`,
   zstd-compressed. This directory is gitignored; data is reproducible
   from the pipeline.

3. **App** (`src/app/`) — `app.py` is the Streamlit entry point;
   `data.py` queries the Parquet partitions with DuckDB
   (`read_parquet([...])` over the selected month range) and returns
   aggregated edges (`SUM(LN(1+NumMentions)*GoldsteinScale) / SUM(...)`).
   The map itself is `src/app/components/network_map.html`
   (Leaflet + D3, self-contained), loaded as raw HTML; `app.py`
   injects the edge list and CAMEO country-name lookup
   (`docs/cameo_countries.json`) by appending a `<script>` that
   dispatches a `message` event before mounting via
   `st.components.v1.html`.

## Non-obvious rules and gotchas

- **CAMEO country codes are not pure ISO 3166.** 27 regional codes
  (AFR, MEA, EUR, LAM, SEA, BLK, …) are valid in source data but must
  be excluded from `edge_type='strict'`. Full list lives in
  `_CAMEO_REGIONAL` in `pipeline.py`; the app query filters on
  `edge_type = 'strict'`.

- **Empty actor fields are `""`, never `NaN`.** All exclusion logic in
  `transform()` tests `== ""` — do not switch to null checks.

- **EventCode-family columns must stay strings end to end.** Casting
  to int silently drops the leading zero (`"042"` → `42`). The all-string
  CSV read is what guarantees this.

- **Polars is used in ingestion, but not in the app query layer.** The
  dev CPU lacks AVX2/FMA and Polars crashes at startup there. The app
  uses DuckDB instead (see `docs/research-log.md` for the decision).

- **`goldstein_category = "neutre"` (GoldsteinScale == 0) is a real
  category**, counted in the global score but excluded from
  positive/negative scores. The Streamlit "Neutre" filter selects it.

## Branch model (from README.md)

- `main` — source of truth for `docs/`
- `dev` — active development
- `recette` — pre-prod validation
- `prod` — stable
- `exploration` — never merges to main

## Domain context

@docs/intent.md
@docs/data-contracts.md
@docs/domain-glossary.md
