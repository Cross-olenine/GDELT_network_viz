"""Tests for src/ingestion/pipeline.py — all tests are synchronous and local (no network)."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import polars as pl
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "ingestion"))

import pipeline


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_raw_row(**overrides) -> dict[str, str]:
    """Return a dict of 58 all-string GDELT columns with sensible defaults."""
    row: dict[str, str] = {col: "" for col in pipeline.GDELT_COLUMNS}
    row.update({
        "GLOBALEVENTID": "1000000",
        "SQLDATE": "20250401",
        "MonthYear": "202504",
        "Year": "2025",
        "FractionDate": "2025.249",
        "Actor1CountryCode": "USA",
        "Actor1Name": "UNITED STATES",
        "Actor2CountryCode": "RUS",
        "Actor2Name": "RUSSIA",
        "IsRootEvent": "1",
        "EventCode": "042",
        "EventBaseCode": "042",
        "EventRootCode": "04",
        "QuadClass": "1",
        "GoldsteinScale": "1.9",
        "NumMentions": "10",
        "NumSources": "3",
        "NumArticles": "10",
        "AvgTone": "-1.5",
        "Actor1Geo_Type": "0",
        "Actor2Geo_Type": "0",
        "ActionGeo_Type": "0",
        "DATEADDED": "20250401",
        "SOURCEURL": "https://example.com/article",
    })
    row.update(overrides)
    return row


def _make_raw_df(*rows_overrides: dict) -> pl.DataFrame:
    """Build an all-string DataFrame with the full 58-column GDELT schema."""
    if not rows_overrides:
        rows_overrides = ({},)
    rows = [_make_raw_row(**ov) for ov in rows_overrides]
    return pl.DataFrame(rows, schema={col: pl.Utf8 for col in pipeline.GDELT_COLUMNS})


def _make_zip(date_str: str, df: pl.DataFrame) -> bytes:
    """Pack a DataFrame as a tab-delimited CSV (no header) inside a ZIP."""
    csv_bytes = df.write_csv(separator="\t", include_header=False).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{date_str}.export.CSV", csv_bytes)
    return buf.getvalue()


# ── iter_months ────────────────────────────────────────────────────────────────

def test_iter_months_single():
    assert list(pipeline.iter_months("2025-01-01", "2025-01-31")) == [(2025, 1)]


def test_iter_months_cross_year():
    result = list(pipeline.iter_months("2024-11-01", "2025-02-28"))
    assert result == [(2024, 11), (2024, 12), (2025, 1), (2025, 2)]


def test_iter_months_same_month():
    result = list(pipeline.iter_months("2025-03-15", "2025-03-20"))
    assert result == [(2025, 3)]


# ── iter_days ──────────────────────────────────────────────────────────────────

def test_iter_days_february_non_leap():
    days = list(pipeline.iter_days(2025, 2))
    assert len(days) == 28
    assert days[0] == "20250201"
    assert days[-1] == "20250228"


def test_iter_days_january():
    days = list(pipeline.iter_days(2025, 1))
    assert len(days) == 31
    assert days[0] == "20250101"
    assert days[-1] == "20250131"


# ── parquet_path / is_done ─────────────────────────────────────────────────────

def test_parquet_path_format():
    p = pipeline.parquet_path(2025, 4)
    assert str(p).endswith("year=2025/month=04/events.parquet".replace("/", "\\") if "\\" in str(p) else "year=2025/month=04/events.parquet")
    assert "year=2025" in str(p)
    assert "month=04" in str(p)


def test_is_done_false_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "DATA_DIR", tmp_path / "events")
    assert pipeline.is_done(2025, 4) is False


def test_is_done_true_when_present(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "DATA_DIR", tmp_path / "events")
    p = pipeline.parquet_path(2025, 4)
    p.parent.mkdir(parents=True)
    p.touch()
    assert pipeline.is_done(2025, 4) is True


# ── parse_gdelt_zip ────────────────────────────────────────────────────────────

def test_parse_gdelt_zip_returns_58_columns():
    raw = _make_raw_df()
    zip_bytes = _make_zip("20250401", raw)
    result = pipeline.parse_gdelt_zip(zip_bytes, "20250401")
    assert result is not None
    assert result.shape[1] == 58


def test_parse_gdelt_zip_event_code_str():
    """EventCode "042" must not be parsed as int — leading zero must be preserved."""
    raw = _make_raw_df({"EventCode": "042", "EventBaseCode": "042", "EventRootCode": "04"})
    zip_bytes = _make_zip("20250401", raw)
    result = pipeline.parse_gdelt_zip(zip_bytes, "20250401")
    assert result is not None
    assert result["EventCode"][0] == "042"
    assert result["EventBaseCode"][0] == "042"


def test_parse_gdelt_zip_bad_zip_returns_none():
    result = pipeline.parse_gdelt_zip(b"not a zip", "20250401")
    assert result is None


def test_parse_gdelt_zip_empty_zip_returns_none():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w"):
        pass
    result = pipeline.parse_gdelt_zip(buf.getvalue(), "20250401")
    assert result is None


# ── transform — exclusion ──────────────────────────────────────────────────────

def test_transform_excludes_all_empty_actor_rows():
    """Row with all four actor fields empty is excluded."""
    row_no_actor = _make_raw_row(
        Actor1CountryCode="", Actor2CountryCode="",
        Actor1Name="", Actor2Name="",
    )
    row_ok = _make_raw_row()
    df = pl.DataFrame([row_no_actor, row_ok], schema={col: pl.Utf8 for col in pipeline.GDELT_COLUMNS})
    result = pipeline.transform(df)
    assert len(result) == 1
    assert result["GLOBALEVENTID"][0] == "1000000"


def test_transform_keeps_row_with_only_actor2_country():
    """Row with Actor2CountryCode filled (Actor1 empty) is kept."""
    row = _make_raw_row(Actor1CountryCode="", Actor1Name="", Actor2CountryCode="RUS")
    df = pl.DataFrame([row], schema={col: pl.Utf8 for col in pipeline.GDELT_COLUMNS})
    result = pipeline.transform(df)
    assert len(result) == 1


# ── transform — derived columns ────────────────────────────────────────────────

def test_transform_goldstein_category_positif():
    df = _make_raw_df({"GoldsteinScale": "3.4"})
    result = pipeline.transform(df)
    assert result["goldstein_category"][0] == "positif"


def test_transform_goldstein_category_negatif():
    df = _make_raw_df({"GoldsteinScale": "-5.0"})
    result = pipeline.transform(df)
    assert result["goldstein_category"][0] == "negatif"


def test_transform_goldstein_category_neutre():
    df = _make_raw_df({"GoldsteinScale": "0.0"})
    result = pipeline.transform(df)
    assert result["goldstein_category"][0] == "neutre"


def test_transform_edge_type_strict():
    """Two ISO country codes → edge_type = 'strict'."""
    df = _make_raw_df({"Actor1CountryCode": "USA", "Actor2CountryCode": "RUS"})
    result = pipeline.transform(df)
    assert result["edge_type"][0] == "strict"


def test_transform_edge_type_extended_regional():
    """Regional CAMEO code → edge_type = 'extended'."""
    df = _make_raw_df({"Actor1CountryCode": "AFR", "Actor2CountryCode": "USA"})
    result = pipeline.transform(df)
    assert result["edge_type"][0] == "extended"


def test_transform_edge_type_extended_missing_actor1():
    """Actor1CountryCode empty → edge_type = 'extended'."""
    df = _make_raw_df({"Actor1CountryCode": "", "Actor2CountryCode": "USA"})
    result = pipeline.transform(df)
    assert result["edge_type"][0] == "extended"


def test_transform_is_internal_false_cross_country():
    df = _make_raw_df({"Actor1CountryCode": "USA", "Actor2CountryCode": "RUS"})
    result = pipeline.transform(df)
    assert result["is_internal"][0] is False


def test_transform_is_internal_true_same_country():
    df = _make_raw_df({"Actor1CountryCode": "USA", "Actor2CountryCode": "USA"})
    result = pipeline.transform(df)
    assert result["is_internal"][0] is True


def test_transform_is_internal_true_actor1_empty():
    """Actor1CountryCode empty + Actor2CountryCode set → is_internal = True."""
    df = _make_raw_df({"Actor1CountryCode": "", "Actor2CountryCode": "RUS"})
    result = pipeline.transform(df)
    assert result["is_internal"][0] is True


def test_transform_year_month_derived():
    df = _make_raw_df({"SQLDATE": "20250401"})
    result = pipeline.transform(df)
    assert result["year"][0] == "2025"
    assert result["month"][0] == "04"


def test_transform_event_code_preserved_as_str():
    """EventCode leading zeros survive the full transform pipeline."""
    df = _make_raw_df({"EventCode": "042"})
    result = pipeline.transform(df)
    assert result["EventCode"][0] == "042"


def test_transform_output_column_count():
    """Output must have exactly 18 columns (13 source + 5 derived)."""
    df = _make_raw_df()
    result = pipeline.transform(df)
    assert result.shape[1] == 18


# ── _write_parquet_atomic ──────────────────────────────────────────────────────

def test_write_parquet_atomic_creates_file(tmp_path):
    df = _make_raw_df()
    out = tmp_path / "year=2025" / "month=04" / "events.parquet"
    pipeline._write_parquet_atomic(pipeline.transform(df), out)
    assert out.exists()


def test_write_parquet_atomic_stale_tmp_overwritten(tmp_path):
    """A stale .tmp from an interrupted previous run must not block the write."""
    df = pipeline.transform(_make_raw_df())
    out = tmp_path / "events.parquet"
    stale_tmp = out.with_name(out.stem + ".tmp")
    out.parent.mkdir(parents=True, exist_ok=True)
    stale_tmp.write_bytes(b"stale garbage")
    pipeline._write_parquet_atomic(df, out)
    assert out.exists()
    assert not stale_tmp.exists()


def test_write_parquet_atomic_readable(tmp_path):
    """Written Parquet must be readable by Polars and have correct row count."""
    df = pipeline.transform(_make_raw_df({}, {}))  # 2 rows
    out = tmp_path / "events.parquet"
    pipeline._write_parquet_atomic(df, out)
    read_back = pl.read_parquet(out)
    assert len(read_back) == 2


# ── idempotence ────────────────────────────────────────────────────────────────

def test_is_done_idempotence(tmp_path, monkeypatch):
    """Once a Parquet is written, is_done() returns True and the month is skipped."""
    monkeypatch.setattr(pipeline, "DATA_DIR", tmp_path / "events")
    df = pipeline.transform(_make_raw_df())
    out = pipeline.parquet_path(2025, 4)
    pipeline._write_parquet_atomic(df, out)
    assert pipeline.is_done(2025, 4) is True
