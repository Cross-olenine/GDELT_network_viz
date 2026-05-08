"""
Panel de filtres Streamlit (sidebar gauche).
Retourne un dict de paramètres utilisés par main.py pour filtrer les données.
"""
from pathlib import Path
import streamlit as st


def render(parquet_dir: Path) -> dict:
    """
    Affiche la sidebar de filtres et retourne les paramètres sélectionnés.

    Args:
        parquet_dir: Dossier contenant les fichiers gdelt_kg_YYYYMM.parquet.

    Returns:
        dict avec clés : mois (list[str]), seuil_interactions (int),
        tone_min (float), tone_max (float).
    """
    st.sidebar.title("Filtres")

    # --- Sélection des mois disponibles ---
    if not parquet_dir.exists():
        st.sidebar.error(f"Dossier données introuvable : {parquet_dir}")
        return {"mois": [], "seuil_interactions": 10, "tone_min": -10.0, "tone_max": 10.0}

    fichiers = sorted(parquet_dir.glob("gdelt_kg_*.parquet"))
    mois_disponibles = [f.stem.replace("gdelt_kg_", "") for f in fichiers]

    mois_selectionnes = st.sidebar.multiselect(
        "Mois",
        options=mois_disponibles,
        default=mois_disponibles[-1:] if mois_disponibles else [],
        format_func=lambda m: f"{m[:4]}-{m[4:]}",
    )

    st.sidebar.markdown("---")

    # --- Seuil minimum d'interactions ---
    seuil_interactions = st.sidebar.slider(
        "Interactions minimum",
        min_value=1,
        max_value=500,
        value=10,
        step=1,
        help="Masque les relations avec moins d'interactions que ce seuil",
    )

    # --- Plage AvgTone ---
    tone_range = st.sidebar.slider(
        "Plage AvgTone",
        min_value=-10.0,
        max_value=10.0,
        value=(-10.0, 10.0),
        step=0.1,
        help="Sentiment médiatique moyen (négatif = conflictuel, positif = coopératif)",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "**Couleur des nœuds — Continent**\n\n"
        "🟠 Afrique\n\n"
        "🔵 Europe\n\n"
        "🔴 Asie\n\n"
        "🟢 Amériques\n\n"
        "🟣 Océanie\n\n"
        "⚫ Inconnu\n\n"
        "---\n\n"
        "**Couleur des arêtes — Ton médiatique**\n\n"
        "🔴 Négatif (conflictuel)\n\n"
        "🟡 Neutre\n\n"
        "🟢 Positif (coopératif)\n\n"
        "Épaisseur = nb d'interactions"
    )

    return {
        "mois": mois_selectionnes,
        "seuil_interactions": seuil_interactions,
        "tone_min": tone_range[0],
        "tone_max": tone_range[1],
    }
