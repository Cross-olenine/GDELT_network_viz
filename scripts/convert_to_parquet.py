# [2] Conversion CSV bruts → Parquet
import argparse
import logging
import sys
from pathlib import Path

import duckdb

# Noms des 61 colonnes GDELT 2.0 Events (pas de header dans les CSV bruts)
GDELT_COLUMNS = [
    "GlobalEventID", "Day", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode",
    "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code",
    "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
    "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code",
    "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass",
    "GoldsteinScale", "NumMentions", "NumSources", "NumArticles", "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat", "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat", "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL",
]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PARQUET = ROOT / "data" / "parquet"


def convert(month: str) -> None:
    """Convertit le fichier CSV GDELT brut du mois donné en Parquet (compression zstd).

    Args:
        month: Mois au format YYYYMM (ex: 202603).

    Raises:
        ValueError: Si le format du mois est invalide.
        FileNotFoundError: Si le fichier CSV source est absent.
        duckdb.Error: Si la conversion DuckDB échoue.
    """
    if not month.isdigit() or len(month) != 6:
        raise ValueError(f"Format YYYYMM invalide : {month!r}")

    csv_path = DATA_RAW / f"gdelt_events_{month}.csv"
    parquet_path = DATA_PARQUET / f"gdelt_events_{month}.parquet"

    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {csv_path}")

    DATA_PARQUET.mkdir(parents=True, exist_ok=True)

    csv_size_mb = csv_path.stat().st_size / 1_048_576
    logger.info("Source : %s (%.1f MB)", csv_path.name, csv_size_mb)

    query = f"""
        COPY (
            SELECT * FROM read_csv(
                '{csv_path.as_posix()}',
                delim='\\t',
                header=false,
                names={GDELT_COLUMNS!r},
                auto_detect=false
            )
        )
        TO '{parquet_path.as_posix()}'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """

    try:
        logger.info("Conversion en cours...")
        duckdb.execute(query)
    except duckdb.Error as exc:
        logger.error("Échec de la conversion DuckDB : %s", exc)
        raise

    parquet_size_mb = parquet_path.stat().st_size / 1_048_576
    ratio = csv_size_mb / parquet_size_mb if parquet_size_mb > 0 else 0
    logger.info(
        "Parquet écrit : %s (%.1f MB) — compression %.1fx",
        parquet_path.name,
        parquet_size_mb,
        ratio,
    )


def _parse_args() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Convertit un fichier CSV GDELT brut en Parquet (zstd)."
    )
    parser.add_argument(
        "month",
        metavar="YYYYMM",
        help="Mois à convertir, ex: 202603",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        convert(args.month)
    except (ValueError, FileNotFoundError) as exc:
        logger.error("%s", exc)
        sys.exit(1)
    except duckdb.Error:
        sys.exit(1)
