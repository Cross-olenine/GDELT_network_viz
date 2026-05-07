"""
Point d'entrée de l'application Streamlit GDELT Knowledge Graph.
Lancement : streamlit run app/main.py
"""
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from app.components import filters, graph

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

_KG_COLUMNS = [
    "Actor1CountryCode",
    "Actor2CountryCode",
    "nb_interactions",
    "avg_tone",
    "avg_goldstein",
]


@st.cache_data(show_spinner="Chargement des données…")
def load_relations(mois: tuple) -> pd.DataFrame:
    """
    Charge et agrège les fichiers parquet des mois sélectionnés via DuckDB.
    Résultat mis en cache — recalculé uniquement si la sélection de mois change.
    """
    if not mois:
        return pd.DataFrame(columns=_KG_COLUMNS)

    fichiers = [PROCESSED_DIR / f"gdelt_kg_{m}.parquet" for m in mois]
    fichiers_sql = ", ".join(f"'{f.as_posix()}'" for f in fichiers)

    try:
        conn = duckdb.connect()
        relations = conn.execute(
            f"SELECT "
            f"  Actor1CountryCode, "
            f"  Actor2CountryCode, "
            f"  SUM(nb_interactions) AS nb_interactions, "
            f"  AVG(avg_tone)        AS avg_tone, "
            f"  AVG(avg_goldstein)   AS avg_goldstein "
            f"FROM read_parquet([{fichiers_sql}]) "
            f"GROUP BY Actor1CountryCode, Actor2CountryCode"
        ).df()
    except Exception as exc:
        st.error(f"Erreur lors du chargement DuckDB : {exc}")
        return pd.DataFrame(columns=_KG_COLUMNS)

    return relations


def main() -> None:
    st.set_page_config(
        page_title="GDELT Knowledge Graph",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("🌐 Knowledge Graph Diplomatique GDELT")

    params = filters.render(PROCESSED_DIR)

    if not params["mois"]:
        st.info("Sélectionnez au moins un mois dans le panneau de gauche.")
        return

    relations = load_relations(tuple(params["mois"]))

    # Filtrage sur les paramètres sidebar
    mask = (
        (relations["nb_interactions"] >= params["seuil_interactions"])
        & (relations["avg_tone"] >= params["tone_min"])
        & (relations["avg_tone"] <= params["tone_max"])
    )
    relations_filtrees = relations.loc[mask].reset_index(drop=True)

    nb_pays = pd.concat([
        relations_filtrees["Actor1CountryCode"],
        relations_filtrees["Actor2CountryCode"],
    ]).nunique()
    st.caption(
        f"**{len(relations_filtrees):,}** relations · **{nb_pays}** pays"
    )

    graph.render(relations_filtrees)


if __name__ == "__main__":
    main()
