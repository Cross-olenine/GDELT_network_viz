from datetime import datetime
from gdeltdoc import Filters, GdeltDoc

KEYWORD = "diplomacy"
START_DATE = "2024-03-01"
END_DATE = "2024-03-02"
NUM_RECORDS = 5

print(f"[{datetime.now().isoformat()}] Lancement requête GDELT")

try:
    gdelt_client = GdeltDoc()
    filters = Filters(
        keyword=KEYWORD,
        start_date=START_DATE,
        end_date=END_DATE,
        num_records=NUM_RECORDS,
    )
    df = gdelt_client.article_search(filters)
except Exception as e:
    print(f"ERREUR API : {e}")
    raise SystemExit(1)

if df.empty:
    print("AVERTISSEMENT : aucun article retourné.")
    raise SystemExit(0)

print(f"Shape     : {df.shape}")
print(f"Colonnes  : {df.columns.tolist()}")
print("\nTitres récupérés :")
for i, title in enumerate(df["title"], start=1):
    print(f"  {i}. {title}")