import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime

import pandas as pd
from gdeltdoc import Filters, GdeltDoc
from gdeltdoc.errors import RateLimitError

# Colonnes garanties par la DOC API GDELT
EXPECTED_COLUMNS = [
    "url",
    "url_mobile",
    "title",
    "seendate",
    "socialimage",
    "domain",
    "language",
    "sourcecountry",
]

_RETRY_DELAYS = [10, 30, 60]
_REQUEST_TIMEOUT = 30  # secondes


def collect_articles(
    keyword: str,
    start_date: str,
    end_date: str,
    num_records: int = 250,
) -> pd.DataFrame:
    """Collecte des articles depuis la DOC API GDELT.

    Args:
        keyword: Mot-clé de recherche plein texte.
        start_date: Date de début au format "YYYY-MM-DD".
        end_date: Date de fin au format "YYYY-MM-DD".
        num_records: Nombre maximum d'articles à retourner (max 250).

    Returns:
        DataFrame pandas avec les colonnes GDELT standard.
        Retourne un DataFrame vide si l'appel échoue ou si l'API ne renvoie rien.
    """
    num_records = min(num_records, 250)
    print(
        f"[{datetime.now().isoformat()}] Requete GDELT : "
        f"keyword='{keyword}', {start_date} -> {end_date}, num_records={num_records}"
    )

    gdelt_client = GdeltDoc()
    filters = Filters(
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        num_records=num_records,
        language="English",
    )

    articles_df = None
    for attempt, delay in enumerate([0] + _RETRY_DELAYS, start=1):
        if delay:
            print(
                f"[gdelt_client] Rate limit atteint - attente {delay}s "
                f"(tentative {attempt}/{1 + len(_RETRY_DELAYS)})..."
            )
            time.sleep(delay)
        try:
            # gdeltdoc v1.12+ n'expose pas de session requests : timeout via thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(gdelt_client.article_search, filters)
                articles_df = future.result(timeout=_REQUEST_TIMEOUT)
            break
        except FuturesTimeoutError:
            print(f"[gdelt_client] Timeout apres {_REQUEST_TIMEOUT}s — abandon.")
            return pd.DataFrame(columns=EXPECTED_COLUMNS)
        except RateLimitError:
            if attempt > len(_RETRY_DELAYS):
                print("[gdelt_client] Rate limit persistant apres toutes les tentatives.")
                return pd.DataFrame(columns=EXPECTED_COLUMNS)
        except Exception as e:
            print(f"[gdelt_client] Erreur lors de l'appel API : {type(e).__name__}: {e}")
            return pd.DataFrame(columns=EXPECTED_COLUMNS)

    if articles_df is None or articles_df.empty:
        print("[gdelt_client] Aucun article retourne pour cette periode.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Validation des colonnes retournees
    missing = [col for col in EXPECTED_COLUMNS if col not in articles_df.columns]
    if missing:
        print(f"[gdelt_client] Colonnes manquantes dans la reponse : {missing}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Validation des valeurs nulles critiques
    null_counts = articles_df[["url", "title", "seendate"]].isnull().sum()
    if null_counts.any():
        print(f"[gdelt_client] Valeurs nulles detectees : {null_counts[null_counts > 0].to_dict()}")

    # Parsing de la date
    articles_df["seendate"] = pd.to_datetime(
        articles_df["seendate"], format="%Y%m%dT%H%M%SZ", errors="coerce"
    )

    return articles_df