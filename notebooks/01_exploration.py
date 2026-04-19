import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    # ── Imports ──
    import sys
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.gdelt_client import collect_articles
    return Path, collect_articles, mo, pd, px


@app.cell
def _(Path):
    # ── Parametres de collecte ──
    KEYWORD = "sanctions diplomat"
    START_DATE = "2024-01-01"
    END_DATE = "2024-01-31"
    NUM_RECORDS = 250
    DATA_RAW = Path(__file__).parent.parent / "data" / "raw"
    return DATA_RAW, END_DATE, KEYWORD, NUM_RECORDS, START_DATE


@app.cell
def _(mo):
    # ── Bouton de collecte ──
    run_button = mo.ui.run_button(label="Lancer la collecte GDELT")
    run_button
    return (run_button,)


@app.cell
def _(END_DATE, KEYWORD, NUM_RECORDS, START_DATE, collect_articles, mo, run_button):
    # ── Collecte conditionnelle au clic du bouton ──
    mo.stop(not run_button.value)
    articles_df = collect_articles(
        keyword=KEYWORD,
        start_date=START_DATE,
        end_date=END_DATE,
        num_records=NUM_RECORDS,
    )
    mo.stop(
        articles_df.empty,
        mo.callout(mo.md("Aucun article retourne pour cette periode."), kind="warn"),
    )
    return (articles_df,)


@app.cell
def _(articles_df, mo):
    # ── Validation : shape, colonnes, valeurs manquantes ──
    _null_counts = articles_df[["url", "title", "seendate"]].isnull().sum()
    return mo.vstack([
        mo.md(f"**Shape :** `{articles_df.shape}`"),
        mo.md(f"**Colonnes :** `{articles_df.columns.tolist()}`"),
        mo.md(f"**Valeurs manquantes :**\n```\n{_null_counts.to_string()}\n```"),
    ])


@app.cell
def _(articles_df, px):
    # ── Distribution par langue ──
    _counts = (
        articles_df["language"]
        .value_counts()
        .reset_index()
        .rename(columns={"language": "Langue", "count": "Nombre d'articles"})
    )
    return px.bar(
        _counts,
        x="Nombre d'articles",
        y="Langue",
        orientation="h",
        title="Distribution des articles par langue",
        height=max(400, len(_counts) * 25),
    )


@app.cell
def _(articles_df, px):
    # ── Distribution par pays source ──
    _counts = (
        articles_df["sourcecountry"]
        .value_counts()
        .reset_index()
        .rename(columns={"sourcecountry": "Pays", "count": "Nombre d'articles"})
    )
    return px.bar(
        _counts,
        x="Nombre d'articles",
        y="Pays",
        orientation="h",
        title="Distribution des articles par pays source",
        height=max(400, len(_counts) * 25),
    )


@app.cell
def _(articles_df, px):
    # ── Distribution temporelle par jour ──
    _df = articles_df.dropna(subset=["seendate"]).copy()
    _df["jour"] = _df["seendate"].dt.date
    _counts = _df.groupby("jour").size().reset_index(name="Nombre d'articles")
    return px.line(
        _counts,
        x="jour",
        y="Nombre d'articles",
        title="Nombre d'articles par jour",
        markers=True,
    )


@app.cell
def _(articles_df, px):
    # ── Top 20 domaines de presse ──
    _counts = (
        articles_df["domain"]
        .value_counts()
        .head(20)
        .reset_index()
        .rename(columns={"domain": "Domaine", "count": "Nombre d'articles"})
    )
    return px.bar(
        _counts,
        x="Nombre d'articles",
        y="Domaine",
        orientation="h",
        title="Top 20 domaines de presse",
        height=max(400, len(_counts) * 25),
    )


@app.cell
def _(articles_df, mo):
    # ── Apercu des titres ──
    return mo.ui.table(
        articles_df[["title", "domain", "seendate", "sourcecountry"]]
    )


@app.cell
def _(DATA_RAW, articles_df, mo):
    # ── Sauvegarde en data/raw/articles_eda.csv ──
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    _output_path = DATA_RAW / "articles_eda.csv"
    articles_df.to_csv(_output_path, index=False)
    return mo.md(f"Fichier sauvegarde : `{_output_path}` ({len(articles_df)} lignes)")


if __name__ == "__main__":
    app.run()
