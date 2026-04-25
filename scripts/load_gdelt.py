"""
ETL GDELT 2.0 — Téléchargement incrémental des Events (mars 2026)
Usage  : python scripts/load_gdelt_raw.py
Output : data/raw/gdelt_events_2026_03.csv
         data/raw/gdelt_events_2026_03.checkpoint
"""

import io
import logging
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

# ── Configuration ────────────────────────────────────────────────────────────
MASTERFILE_URL  = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
TARGET_PREFIX   = "2026_03"          # mois cible dans les noms de fichiers
FILTER_MONTH    = "202603"           # préfixe dans l'URL GDELT (YYYYMM)
OUTPUT_CSV      = Path("data/raw/gdelt_events_202603.csv")
CHECKPOINT_FILE = Path("data/raw/gdelt_events_202603.checkpoint")
LOG_FILE        = Path("data/raw/gdelt_events_202603.log")
BATCH_SIZE      = 10                 # fichiers traités avant flush sur disque
SLEEP_BETWEEN   = 1                  # secondes entre deux téléchargements
REQUEST_TIMEOUT = 30                 # secondes

# Colonnes GDELT 2.0 Events (61 colonnes, tab-délimité, pas de header)
GDELT_COLUMNS = [
    "GlobalEventID", "Day", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode",
    "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code",
    "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
    "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code",
    "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
    "QuadClass", "GoldsteinScale", "NumMentions", "NumSources",
    "NumArticles", "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat",
    "Actor1Geo_Long", "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat",
    "Actor2Geo_Long", "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat",
    "ActionGeo_Long", "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL",
]

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ── Fonctions ─────────────────────────────────────────────────────────────────

def fetch_export_urls(month_prefix: str) -> list[str]:
    """Télécharge le masterfilelist et filtre les URLs export du mois cible."""
    log.info("Téléchargement du masterfilelist...")
    r = requests.get(MASTERFILE_URL, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    urls = []
    for line in r.text.splitlines():
        parts = line.strip().split(" ")
        if len(parts) != 3:
            continue
        url = parts[2]
        if f"/{month_prefix}" in url and url.endswith(".export.CSV.zip"):
            urls.append(url)
    urls.sort()
    log.info(f"{len(urls)} fichiers export trouvés pour {month_prefix}")
    return urls


def load_checkpoint() -> set[str]:
    """Charge la liste des URLs déjà traitées."""
    if not CHECKPOINT_FILE.exists():
        return set()
    with open(CHECKPOINT_FILE, encoding="utf-8") as f:
        done = {line.strip() for line in f if line.strip()}
    log.info(f"Checkpoint : {len(done)} fichiers déjà traités")
    return done


def save_checkpoint(url: str) -> None:
    """Ajoute une URL au checkpoint."""
    with open(CHECKPOINT_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def download_and_parse(url: str) -> pd.DataFrame | None:
    """Télécharge un ZIP, décompresse en mémoire, retourne un DataFrame."""
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                df = pd.read_csv(
                    f,
                    sep="\t",
                    header=None,
                    names=GDELT_COLUMNS,
                    dtype=str,       # tout en string pour éviter les erreurs de parsing
                    low_memory=False,
                )
        return df
    except Exception as e:
        log.error(f"Erreur sur {url} : {type(e).__name__}: {e}")
        return None


def append_to_csv(df: pd.DataFrame, first_write: bool) -> None:
    """Appende le DataFrame au CSV de sortie."""
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        OUTPUT_CSV,
        mode="w" if first_write else "a",
        header=first_write,
        index=False,
        encoding="utf-8",
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log.info("=== ETL GDELT Events démarré ===")
    log.info(f"Mois cible : {FILTER_MONTH}")
    log.info(f"Output     : {OUTPUT_CSV}")

    # 1. Récupérer toutes les URLs du mois
    all_urls = fetch_export_urls(FILTER_MONTH)
    if not all_urls:
        log.error("Aucune URL trouvée — vérifier FILTER_MONTH")
        return

    # 2. Charger le checkpoint
    done_urls = load_checkpoint()
    remaining = [u for u in all_urls if u not in done_urls]
    log.info(f"À traiter : {len(remaining)} / {len(all_urls)} fichiers")

    if not remaining:
        log.info("Tout est déjà traité.")
        return

    # 3. Traitement par batch
    first_write = not OUTPUT_CSV.exists()
    batch_buffer = []
    total_rows = 0

    for i, url in enumerate(remaining, start=1):
        log.info(f"[{i}/{len(remaining)}] {url.split('/')[-1]}")

        df = download_and_parse(url)
        if df is not None:
            batch_buffer.append(df)
            total_rows += len(df)

        # Flush sur disque tous les BATCH_SIZE fichiers
        if len(batch_buffer) >= BATCH_SIZE or i == len(remaining):
            if batch_buffer:
                batch_df = pd.concat(batch_buffer, ignore_index=True)
                append_to_csv(batch_df, first_write=first_write)
                log.info(f"  → Flush : {len(batch_df)} lignes écrites")
                first_write = False
                batch_buffer = []

        # Checkpoint après chaque fichier réussi
        if df is not None:
            save_checkpoint(url)

        # Rate limit
        time.sleep(SLEEP_BETWEEN)

    log.info(f"=== ETL terminé — {total_rows} lignes au total ===")
    log.info(f"Fichier final : {OUTPUT_CSV}")


if __name__ == "__main__":
    main()