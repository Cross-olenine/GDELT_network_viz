import time

import pandas as pd
from gdeltdoc import Filters, GdeltDoc

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

# Délai minimal entre deux appels (rate limit GDELT)
RATE_LIMIT_SECONDS = 6


def collect_articles(keyword: str, timespan: str, num_records: int) -> pd.DataFrame:
    """Collecte des articles depuis la DOC API GDELT.

    Args:
        keyword: Mot-clé de recherche plein texte.
        timespan: Fenêtre temporelle (ex : "7days", "24h").
        num_records: Nombre maximum d'articles à retourner (max 250).

    Returns:
        DataFrame pandas avec les colonnes GDELT standard.
        Retourne un DataFrame vide si l'appel échoue ou si l'API ne renvoie rien.
    """
    # Respect de la limite de l'API GDELT
    num_records = min(num_records, 250)
    time.sleep(RATE_LIMIT_SECONDS)

    try:
        gd = GdeltDoc()
        filters = Filters(keyword=keyword, timespan=timespan, num_records=num_records)
        df = gd.article_search(filters)
    except Exception as e:
        print(f"[gdelt_client] Erreur lors de l'appel API : {e}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Validation des colonnes retournées
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        print(f"[gdelt_client] Colonnes manquantes dans la réponse : {missing}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    return df
