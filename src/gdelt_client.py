from datetime import datetime

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
    "tone",
]


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

    print(f"[{datetime.now().isoformat()}] Requete GDELT : keyword='{keyword}', {start_date} -> {end_date}, num_records={num_records}")

    try:
        gdelt_client = GdeltDoc()
        filters = Filters(
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            num_records=num_records,
            language="English",
        )
        articles_df = gdelt_client.article_search(filters)
    except Exception as e:
        print(f"[gdelt_client] Erreur lors de l'appel API : {e}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    if articles_df.empty:
        print("[gdelt_client] Aucun article retourné pour cette période.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Validation des colonnes retournées
    missing = [col for col in EXPECTED_COLUMNS if col not in articles_df.columns]
    if missing:
        print(f"[gdelt_client] Colonnes manquantes dans la réponse : {missing}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Validation des dtypes et valeurs nulles critiques
    null_counts = articles_df[["url", "title", "seendate"]].isnull().sum()
    if null_counts.any():
        print(f"[gdelt_client] Valeurs nulles détectées : {null_counts[null_counts > 0].to_dict()}")

    articles_df["seendate"] = pd.to_datetime(
        articles_df["seendate"], format="%Y%m%dT%H%M%SZ", errors="coerce"
    )

    return articles_df
