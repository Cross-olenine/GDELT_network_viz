"""Streamlit entry point — GDELT Network Viz POC.

Architecture
------------
The Streamlit sidebar is gone. All filter UI lives inside the iframe
(`components/index.html`) via a custom slide-in panel. The iframe is
registered as a Streamlit component (`declare_component`), so it can
push filter changes back via the Streamlit message protocol
(`streamlit:setComponentValue`). On reception, Python recomputes the
filtered edges and re-renders the component with the new payload.
"""

import json
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from data import available_date_bounds, load_edges_range

_ROOT = Path(__file__).parent.parent.parent
_COMPONENTS_DIR = Path(__file__).parent / "components"
_CAMEO_JSON = _ROOT / "docs" / "cameo_countries.json"

# Custom component — Streamlit serves index.html from this directory
_network_map = components.declare_component(
    "gdelt_network_map", path=str(_COMPONENTS_DIR)
)

st.set_page_config(
    page_title="GDELT Network Viz",
    layout="wide",
    page_icon="🌍",
    initial_sidebar_state="collapsed",
)

# Strip every pixel of Streamlit chrome so the iframe owns the viewport.
st.markdown(
    """
    <style>
      .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
      .stApp { overflow: hidden; }
      header { display: none !important; }
      footer { display: none !important; }
      [data-testid="stSidebar"]  { display: none !important; }
      [data-testid="stHeader"]   { display: none !important; }
      [data-testid="stToolbar"]  { display: none !important; }
      [data-testid="stDecoration"] { display: none !important; }
      section[data-testid="stAppViewContainer"] > div { padding: 0 !important; }
      iframe { border: none !important; display: block; width: 100vw !important; height: 100vh !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Date bounds (cached) ──────────────────────────────────────────────────
bounds = available_date_bounds()
if bounds is None:
    st.warning("Aucune donnée disponible — exécute le pipeline d'ingestion d'abord.")
    st.stop()
min_date, max_date = bounds

DEFAULT_FILTER = {
    "from_date": min_date.isoformat(),
    "to_date":   max_date.isoformat(),
    "goldstein_filter": "Tous",
}

if "filter_state" not in st.session_state:
    st.session_state.filter_state = DEFAULT_FILTER.copy()

fs = st.session_state.filter_state

# ── Edges for the current filter state ────────────────────────────────────
edges = load_edges_range(
    date.fromisoformat(fs["from_date"]),
    date.fromisoformat(fs["to_date"]),
    fs["goldstein_filter"],
)

with open(_CAMEO_JSON, encoding="utf-8") as f:
    country_names: dict[str, str] = json.load(f)

# ── Render the component ──────────────────────────────────────────────────
component_value = _network_map(
    edges=edges,
    country_names=country_names,
    bounds={"min": min_date.isoformat(), "max": max_date.isoformat()},
    filter_state=fs,
    default=None,
    key="network_map",
)

# Component pushed a new filter → persist and rerun so Python recomputes edges
if isinstance(component_value, dict) and component_value != fs:
    required = {"from_date", "to_date", "goldstein_filter"}
    if required.issubset(component_value.keys()):
        st.session_state.filter_state = component_value
        st.rerun()
