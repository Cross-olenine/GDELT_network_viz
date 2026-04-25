import pandas as pd

df = pd.read_csv(
    "data/raw/gdelt_events_202603.csv",
    dtype=str,
    nrows=5
)
print("Shape aperçu :", df.shape)
print("Colonnes :", df.columns.tolist())
print("\nPremières lignes :")
print(df.head())