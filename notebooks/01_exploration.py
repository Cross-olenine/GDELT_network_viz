import marimo

__generated_with = "0.23.3"
app = marimo.App(width="medium")


@app.cell
def _():
    # ── Imports ──
    import marimo as mo
    import duckdb
    import plotly.express as px
    from pathlib import Path

    return Path, duckdb, mo


@app.cell
def _(Path):
    # ── Chemins ──
    DATA_RAW       = Path("data/raw/gdelt_events_202603.csv")
    DATA_PROCESSED = Path("data/processed")
    return (DATA_RAW,)


@app.cell
def _(DATA_RAW, duckdb, mo):
    # ── Connexion DuckDB + vue sur le fichier ──
    con = duckdb.connect()
    con.execute(f"""
        CREATE VIEW events AS 
        SELECT * FROM read_csv_auto('{DATA_RAW}', ignore_errors=true)
    """)
    _count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    mo.callout(mo.md(f"Dataset chargé : **{_count:,} lignes**"), kind="success")
    return (con,)


@app.cell
def _(con):
    df = con.execute("""


        SELECT *
        FROM events
        LIMIT 1



    """).df()
    df
    return


@app.cell
def _(con):
    df1 = con.execute("""

        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'events'
        ORDER BY ordinal_position

    """).df()
    df1
    return


@app.cell
def _(con):
    # ── Étape 1 : récupérer les colonnes et leurs types ──
    # information_schema nous donne les métadonnées du schéma
    meta = con.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'events'
        ORDER BY ordinal_position
    """).df()

    cols = meta["column_name"].tolist()

    # Colonnes numériques uniquement (pour min, max, moyenne etc.)
    numeric_types = ["BIGINT", "INTEGER", "DOUBLE", "FLOAT", "HUGEINT"]
    cols_numeric = meta[meta["data_type"].isin(numeric_types)]["column_name"].tolist()
    cols_string  = meta[~meta["data_type"].isin(numeric_types)]["column_name"].tolist()

    # ── Étape 2 : % de nulls pour toutes les colonnes ──
    null_exprs = [
        f"ROUND(100.0 * COUNT(*) FILTER (WHERE \"{c}\" IS NULL) / COUNT(*), 2) AS \"{c}\""
        for c in cols
    ]
    nulls_wide = con.execute(f"SELECT {', '.join(null_exprs)} FROM events").df()
    nulls = nulls_wide.melt(var_name="colonne", value_name="pct_null")

    # ── Étape 3 : cardinalité (valeurs uniques) pour toutes les colonnes ──
    card_exprs = [
        f"COUNT(DISTINCT \"{c}\") AS \"{c}\""
        for c in cols
    ]
    card_wide = con.execute(f"SELECT {', '.join(card_exprs)} FROM events").df()
    card = card_wide.melt(var_name="colonne", value_name="nb_valeurs_uniques")

    # ── Étape 4 : % de zéros pour les colonnes numériques uniquement ──
    zero_exprs = [
        f"ROUND(100.0 * COUNT(*) FILTER (WHERE \"{c}\" = 0) / COUNT(*), 2) AS \"{c}\""
        for c in cols_numeric
    ]
    zeros_wide = con.execute(f"SELECT {', '.join(zero_exprs)} FROM events").df()
    zeros = zeros_wide.melt(var_name="colonne", value_name="pct_zeros")

    # ── Étape 5 : statistiques descriptives pour les colonnes numériques ──
    stats_exprs = [
        f"ROUND(MIN(\"{c}\")::DOUBLE, 2)    AS \"{c}_min\","
        f"ROUND(MAX(\"{c}\")::DOUBLE, 2)    AS \"{c}_max\","
        f"ROUND(AVG(\"{c}\"), 2)            AS \"{c}_mean\","
        f"ROUND(MEDIAN(\"{c}\"), 2)         AS \"{c}_median\","
        f"ROUND(STDDEV(\"{c}\"), 2)         AS \"{c}_stddev\""
        for c in cols_numeric
    ]
    stats_wide = con.execute(f"SELECT {', '.join(stats_exprs)} FROM events").df()

    # On pivote en format long
    import pandas as pd

    stats_long = []
    for c in cols_numeric:
        stats_long.append({
            "colonne":    c,
            "min":        stats_wide[f"{c}_min"].iloc[0],
            "max":        stats_wide[f"{c}_max"].iloc[0],
            "moyenne":    stats_wide[f"{c}_mean"].iloc[0],
            "mediane":    stats_wide[f"{c}_median"].iloc[0],
            "ecart_type": stats_wide[f"{c}_stddev"].iloc[0],
        })
    stats = pd.DataFrame(stats_long)

    # ── Étape 6 : assemblage final ──
    # On part des nulls (toutes les colonnes) et on joint les autres métriques
    profiling = (
        nulls
        .merge(meta.rename(columns={"column_name": "colonne", "data_type": "type"}), on="colonne")
        .merge(card,  on="colonne")
        .merge(zeros, on="colonne", how="left")   # left join car uniquement numériques
        .merge(stats, on="colonne", how="left")   # left join car uniquement numériques
        [["colonne", "type", "pct_null", "nb_valeurs_uniques",
          "pct_zeros", "min", "max", "moyenne", "mediane", "ecart_type"]]
        .sort_values("pct_null", ascending=False)
        .reset_index(drop=True)
    )

    profiling
    return


@app.cell
def _(Path, con):
    dataset_kg = con.execute("""
        SELECT 
            GlobalEventID,
            Day,
            Actor1Name,
            Actor1CountryCode,
            Actor1Type1Code,
            Actor2Name,
            Actor2CountryCode,
            Actor2Type1Code,
            EventCode,
            EventBaseCode,
            EventRootCode,
            QuadClass,
            GoldsteinScale,
            NumMentions,
            AvgTone,
            ActionGeo_CountryCode,
            ActionGeo_FullName,
            ActionGeo_Lat,
            ActionGeo_Long,
            SOURCEURL
        FROM events
        WHERE Year = 2026
          AND Actor1CountryCode IS NOT NULL
          AND Actor2CountryCode IS NOT NULL
          AND EventRootCode IN ('03','04','05','06','07','08')
    """).df()

    print(f"Shape : {dataset_kg.shape}")
    dataset_kg.head()


    output_path = Path("data/processed/gdelt_kg_202603.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_kg.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Sauvegardé : {output_path}")
    print(f"Shape : {dataset_kg.shape}")
    print(f"Taille : {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
