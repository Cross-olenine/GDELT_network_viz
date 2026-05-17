"""Streamlit entry point — GDELT Network Viz POC."""

import json
from pathlib import Path

import streamlit as st

from data import load_edges, list_available_months, GoldsteinFilter

_ROOT = Path(__file__).parent.parent.parent
_COMPONENT = Path(__file__).parent / "components" / "network_map.html"
_CAMEO_JSON = _ROOT / "docs" / "cameo_countries.json"

st.set_page_config(
    page_title="GDELT Network Viz",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Available months ──────────────────────────────────────────────────────
available = list_available_months()
month_labels = {(y, m): f"{y}-{m:02d}" for y, m in available}

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filtres")

    selected_label = st.selectbox(
        "Période",
        options=list(month_labels.values()),
        index=len(month_labels) - 1,  # default: last available month
    )
    selected_ym = next(ym for ym, lbl in month_labels.items() if lbl == selected_label)
    sel_year, sel_month = selected_ym

    goldstein_filter: GoldsteinFilter = st.radio(  # type: ignore[assignment]
        "Goldstein category",
        options=["Tous", "Positif", "Négatif", "Neutre"],
        index=0,
    )
    st.markdown("---")
    st.caption(f"Source : Parquet {selected_label} ({len(available)} mois disponibles)")

# ── Data ──────────────────────────────────────────────────────────────────
edges = load_edges(sel_year, sel_month, goldstein_filter)

with open(_CAMEO_JSON, encoding="utf-8") as f:
    country_names: dict[str, str] = json.load(f)

st.markdown(f"**{len(edges)} edge(s)** — {selected_label} — filtre : *{goldstein_filter}*")

# ── Network map component ─────────────────────────────────────────────────
html_source = _COMPONENT.read_text(encoding="utf-8")

payload = json.dumps({"type": "gdelt_data", "edges": edges, "country_names": country_names})
injection = f"""
<script>
(function() {{
  window.addEventListener("load", function() {{
    const msg = {payload};
    window.dispatchEvent(new MessageEvent("message", {{ data: msg }}));
  }});
}})();
</script>
"""
html_with_data = html_source.replace("</body>", injection + "\n</body>")

st.components.v1.html(html_with_data, height=620, scrolling=False)
