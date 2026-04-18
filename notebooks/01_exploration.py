import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    # ── Imports ──
    import time
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from pathlib import Path
    from gdeltdoc import GdeltDoc, Filters

    return Filters, GdeltDoc, Path, mo, pd, px, time


@app.cell
def _(Path):
    # ── Configuration ──
    KEYWORD = "diplomatic sanctions bilateral"
    TIMESPAN = "7days"
    NUM_RECORDS = 25
    DATA_RAW = Path("data/raw")
    return DATA_RAW, KEYWORD, NUM_RECORDS, TIMESPAN


@app.cell
def _(mo):
    # ── Collecte API ──
    run_button = mo.ui.run_button(label="Lancer la collecte GDELT")
    run_button
    return (run_button,)


@app.cell
def _(
    Filters,
    GdeltDoc,
    KEYWORD,
    NUM_RECORDS,
    TIMESPAN,
    mo,
    pd,
    run_button,
    time,
):
    # ── Exécution collecte ──
    mo.stop(not run_button.value)

    _error_msg = None
    try:
        _gd = GdeltDoc()
        _filters = Filters(
            keyword=KEYWORD,
            timespan=TIMESPAN,
            num_records=NUM_RECORDS,
        )
        time.sleep(10)
        articles_df = _gd.article_search(_filters)
        print("Shape:", articles_df.shape)
        print("Colonnes:", articles_df.columns.tolist())
    except Exception as _e:
        articles_df = pd.DataFrame()
        _error_msg = str(_e)
        print("ERREUR:", _e)

    mo.stop(
        _error_msg is not None,
        mo.callout(mo.md(f"Erreur : {_error_msg}"), kind="warn"),
    )
    mo.stop(
        articles_df.empty,
        mo.callout(mo.md("Aucun article retourné."), kind="warn"),
    )
    return (articles_df,)


@app.cell
def _(articles_df, mo):
    # ── Validation du DataFrame brut ──
    _expected_cols = [
        "url", "url_mobile", "title", "seendate",
        "socialimage", "domain", "language", "sourcecountry",
    ]
    _missing_cols = [c for c in _expected_cols if c not in articles_df.columns]

    # Arrêt si des colonnes critiques manquent — les cellules aval en dépendent
    mo.stop(
        len(_missing_cols) > 0,
        mo.callout(
            mo.md(f"Colonnes manquantes dans le DataFrame : `{_missing_cols}`. Pipeline interrompu."),
            kind="warn",
        ),
    )

    # Validation active des dtypes critiques
    _dtype_issues = []
    if articles_df["seendate"].dtype != object:
        _dtype_issues.append("`seendate` : attendu `object` (string), obtenu `{}`".format(articles_df["seendate"].dtype))
    if articles_df["url"].dtype != object:
        _dtype_issues.append("`url` : attendu `object` (string), obtenu `{}`".format(articles_df["url"].dtype))

    _output = mo.vstack([
        mo.md(f"**Shape :** `{articles_df.shape}`"),
        mo.md(f"**Types (dtypes) :**\n```\n{articles_df.dtypes.to_string()}\n```"),
        mo.callout(mo.md("Problèmes de types : " + " | ".join(_dtype_issues)), kind="warn")
        if _dtype_issues else mo.md("**Types critiques :** OK ✓"),
        mo.ui.table(articles_df.head()),
    ])
    return


@app.cell
def _(articles_df, px):
    # ── Distribution par pays source ──
    _counts = (
        articles_df["sourcecountry"]
        .value_counts()
        .reset_index()
        .rename(columns={"sourcecountry": "Pays", "count": "Nombre d'articles"})
    )
    _fig = px.bar(
        _counts,
        x="Nombre d'articles",
        y="Pays",
        orientation="h",
        title="Distribution des articles par pays source",
        labels={"Pays": "Pays source", "Nombre d'articles": "Nombre d'articles"},
    )
    return


@app.cell
def _(articles_df, px):
    # ── Distribution par langue ──
    _counts = (
        articles_df["language"]
        .value_counts()
        .reset_index()
        .rename(columns={"language": "Langue", "count": "Nombre d'articles"})
    )
    _fig = px.bar(
        _counts,
        x="Nombre d'articles",
        y="Langue",
        orientation="h",
        title="Distribution des articles par langue",
        labels={"Langue": "Langue", "Nombre d'articles": "Nombre d'articles"},
    )
    return


@app.cell
def _(articles_df, mo, pd, px):
    # ── Distribution temporelle ──
    _df_time = articles_df.copy()
    _df_time["date"] = pd.to_datetime(
        _df_time["seendate"], format="%Y%m%dT%H%M%SZ", errors="coerce"
    )
    # Avertissement si des dates n'ont pas pu être parsées
    _nat_count = _df_time["date"].isna().sum()
    _nat_ratio = _nat_count / len(_df_time)
    _df_time = _df_time.dropna(subset=["date"])
    _df_time["jour"] = _df_time["date"].dt.date
    _counts = _df_time.groupby("jour").size().reset_index(name="Nombre d'articles")
    _fig = px.line(
        _counts,
        x="jour",
        y="Nombre d'articles",
        title="Nombre d'articles par jour",
        labels={"jour": "Date", "Nombre d'articles": "Nombre d'articles"},
        markers=True,
    )
    _warning = mo.callout(
        mo.md(f"{_nat_count} dates non parseables ignorées ({_nat_ratio:.0%} des lignes)."),
        kind="warn",
    ) if _nat_ratio > 0.1 else None
    return


@app.cell
def _():
    # ── Aperçu des titres ──
    return


@app.cell
def _(DATA_RAW, articles_df):
    # ── Sauvegarde ──
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    _output_path = DATA_RAW / "articles_raw.csv"
    articles_df.to_csv(_output_path, index=False)
    return


if __name__ == "__main__":
    app.run()
