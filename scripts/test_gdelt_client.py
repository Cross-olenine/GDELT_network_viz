import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gdelt_client import collect_articles

articles_df = collect_articles(
    keyword="diplomatic sanctions",
    start_date="2024-03-01",
    end_date="2024-03-03",
    num_records=10,
)

if articles_df.empty:
    print("\nAucun article retourné pour cette période.")
    sys.exit(0)

print(f"\nShape     : {articles_df.shape}")
print(f"Colonnes  : {articles_df.columns.tolist()}")
print("\nTitres récupérés :")
for i, title in enumerate(articles_df["title"], start=1):
    print(f"  {i}. {title}")
