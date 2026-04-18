import time

from gdeltdoc import Filters, GdeltDoc

# Paramètres de test
KEYWORD = "diplomacy"
TIMESPAN = "7days"
NUM_RECORDS = 5

print(f"Requête GDELT : keyword='{KEYWORD}', timespan='{TIMESPAN}', num_records={NUM_RECORDS}")
print("Attente 15 secondes (rate limit)...")
time.sleep(15)

try:
    gd = GdeltDoc()
    filters = Filters(keyword=KEYWORD, timespan=TIMESPAN, num_records=NUM_RECORDS)
    df = gd.article_search(filters)
except Exception as e:
    print(f"ERREUR : {e}")
    raise SystemExit(1)

print(f"\nShape     : {df.shape}")
print(f"Colonnes  : {df.columns.tolist()}")
print("\nTitres récupérés :")
for i, title in enumerate(df["title"], start=1):
    print(f"  {i}. {title}")
