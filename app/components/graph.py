"""
Rendu du knowledge graph diplomatique via Vis.js.
Génère un HTML autonome injecté dans Streamlit via st.components.v1.html.
Utilise pyvis avec cdn_resources="in_line" pour bundler vis-network.min.js
directement dans le HTML — contourne le blocage CDN des iframes Streamlit
(origine nulle du srcdoc empêche le chargement de scripts externes).
"""
import json
import math

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

try:
    import pycountry as _pycountry

    def _country_name(code: str) -> str:
        """Retourne le nom complet d'un pays depuis son code ISO alpha-3."""
        c = _pycountry.countries.get(alpha_3=code)
        return c.name if c else code

except ImportError:
    def _country_name(code: str) -> str:
        """Retourne le code tel quel si pycountry est indisponible."""
        return code


def _tone_to_color(tone: float) -> str:
    """Interpole rouge → jaune → vert selon AvgTone (plage -5 à +5)."""
    t = max(-5.0, min(5.0, float(tone)))
    ratio = (t + 5.0) / 10.0  # 0 = rouge, 1 = vert
    r = int(231 * (1 - ratio) + 39 * ratio)
    g = int(76 * (1 - ratio) + 174 * ratio)
    b = int(60 * (1 - ratio) + 96 * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


def _edge_width(nb: int, max_nb: int) -> float:
    """Normalise l'épaisseur d'arête (1-10) par log sur nb_interactions."""
    if max_nb <= 1:
        return 1.0
    return 1.0 + 9.0 * math.log1p(nb) / math.log1p(max_nb)


def render(relations: pd.DataFrame, height: int = 900) -> None:
    """
    Construit et affiche le graph Vis.js à partir des relations filtrées.

    Args:
        relations: DataFrame avec colonnes Actor1CountryCode, Actor2CountryCode,
                   nb_interactions, avg_tone, avg_goldstein.
        height: Hauteur du canvas Vis.js en pixels.
    """
    if relations.empty:
        st.warning("Aucune relation à afficher avec les filtres actuels.")
        return

    max_nb = int(relations["nb_interactions"].max())

    # Degré de chaque pays (nombre d'arêtes) — vectorisé
    degree: dict = (
        pd.concat([relations["Actor1CountryCode"], relations["Actor2CountryCode"]])
        .value_counts()
        .to_dict()
    )

    net = Network(
        height=f"{height}px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        notebook=False,
        cdn_resources="in_line",
    )

    # Noeuds
    countries = set(relations["Actor1CountryCode"]) | set(relations["Actor2CountryCode"])
    for code in countries:
        name = _country_name(code)
        size = 10 + min(degree.get(code, 1) * 2, 40)
        net.add_node(
            code,
            label=code,
            title=f"<b>{name}</b><br>Connexions : {degree.get(code, 0)}",
            size=size,
        )

    # Arêtes
    for row in relations.itertuples(index=False):
        nb = int(row.nb_interactions)
        tone = float(row.avg_tone)
        goldstein = float(row.avg_goldstein)
        a1, a2 = row.Actor1CountryCode, row.Actor2CountryCode
        net.add_edge(
            a1,
            a2,
            title=(
                f"<b>{a1} ↔ {a2}</b>"
                f"<br>Interactions : {nb}"
                f"<br>AvgTone : {tone:.2f}"
                f"<br>Goldstein : {goldstein:.2f}"
            ),
            width=_edge_width(nb, max_nb),
            color=_tone_to_color(tone),
        )

    net.set_options(
        json.dumps(
            {
                "physics": {
                    "enabled": True,
                    "stabilization": {"iterations": 500, "fit": True},
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "springLength": 250,
                        "damping": 0.09,
                    },
                },
                "edges": {"smooth": {"type": "continuous"}},
                "nodes": {"shape": "dot", "borderWidth": 1},
                "interaction": {
                    "hover": True,
                    "tooltipDelay": 100,
                    "navigationButtons": True,
                },
            }
        )
    )

    html = net.generate_html(notebook=False)

    # Injecte le listener avant return network; pour couper la physique
    # dès la fin de la stabilisation — le drag ne propage plus aux voisins.
    listener_js = (
        "network.on('stabilizationIterationsDone', function() {\n"
        "    network.setOptions({ physics: { enabled: false } });\n"
        "});\n"
    )
    html = html.replace("return network;", listener_js + "return network;", 1)

    components.html(html, height=height + 10, scrolling=False)
