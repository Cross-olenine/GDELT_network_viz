# [3] Transformation et agrégation KG diplomatique
import argparse
import logging
import sys
from pathlib import Path

import polars as pl

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DATA_PARQUET = ROOT / "data" / "parquet"
DATA_PROCESSED = ROOT / "data" / "processed"

DIPLOMATIC_ROOT_CODES = ["03", "04", "05", "06", "07", "08"]


def transform(month: str) -> None:
    """Lit le Parquet brut GDELT du mois, filtre et agrège les paires pays diplomatiques.

    Args:
        month: Mois au format YYYYMM (ex: 202603).

    Raises:
        ValueError: Si le format du mois est invalide.
        FileNotFoundError: Si le fichier Parquet source est absent.
    """
    if not month.isdigit() or len(month) != 6:
        raise ValueError(f"Format YYYYMM invalide : {month!r}")

    year = month[:4]
    source_path = DATA_PARQUET / f"gdelt_events_{month}.parquet"
    output_path = DATA_PROCESSED / f"gdelt_kg_{month}.parquet"

    if not source_path.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {source_path}")

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    events_lf = pl.scan_parquet(source_path)

    # Comptage source avant filtre (collect avec select pour éviter de tout charger)
    nb_source = events_lf.select(pl.len()).collect().item()
    logger.info("Source : %s — %d lignes", source_path.name, nb_source)

    filtered_lf = (
        events_lf
        .filter(pl.col("Year").cast(pl.Utf8) == year)
        .filter(pl.col("Actor1CountryCode").is_not_null())
        .filter(pl.col("Actor2CountryCode").is_not_null())
        .filter(pl.col("Actor1CountryCode") != pl.col("Actor2CountryCode"))
        .filter(pl.col("EventRootCode").is_in(DIPLOMATIC_ROOT_CODES))
    )

    nb_filtered = filtered_lf.select(pl.len()).collect().item()
    if nb_filtered == 0:
        logger.warning("Aucune ligne après filtres — vérifier Year=%s et EventRootCode", year)
    logger.info("Après filtres diplomatiques : %d lignes (%.1f%%)", nb_filtered, 100 * nb_filtered / nb_source if nb_source else 0)

    kg_df = (
        filtered_lf
        .group_by(["Actor1CountryCode", "Actor2CountryCode"])
        .agg([
            pl.len().alias("nb_interactions"),
            pl.col("AvgTone").cast(pl.Float64).mean().round(2).alias("avg_tone"),
            pl.col("GoldsteinScale").cast(pl.Float64).mean().round(2).alias("avg_goldstein"),
        ])
        .sort(["Actor1CountryCode", "Actor2CountryCode"])
        .collect()
    )

    nb_pairs = len(kg_df)
    logger.info("Paires agrégées : %d", nb_pairs)

    kg_df.write_parquet(output_path, compression="zstd")
    output_size_mb = output_path.stat().st_size / 1_048_576
    logger.info("KG écrit : %s (%.1f MB)", output_path.name, output_size_mb)


def _parse_args() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Transforme le Parquet brut GDELT en dataset KG diplomatique agrégé."
    )
    parser.add_argument(
        "month",
        metavar="YYYYMM",
        help="Mois à transformer, ex: 202603",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        transform(args.month)
    except (ValueError, FileNotFoundError) as exc:
        logger.error("%s", exc)
        sys.exit(1)
