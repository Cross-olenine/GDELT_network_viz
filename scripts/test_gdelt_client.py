import sys
from pathlib import Path

# Ajoute la racine du projet au path pour pouvoir importer src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gdelt_client import collect_articles

df = collect_articles(keyword="diplomacy", timespan="7days", num_records=5)

print(f"Shape    : {df.shape}")
print(f"Colonnes : {df.columns.tolist()}")
print("\nTitres récupérés :")
for i, title in enumerate(df["title"], start=1):
    print(f"  {i}. {title}")
