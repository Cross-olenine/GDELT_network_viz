"""Streamlit entry point — GDELT Network Viz POC."""

import json
from pathlib import Path

import streamlit as st

from data import available_date_bounds, load_edges_range, GoldsteinFilter

_ROOT = Path(__file__).parent.parent.parent
_COMPONENT = Path(__file__).parent / "components" / "network_map.html"
_CAMEO_JSON = _ROOT / "docs" / "cameo_countries.json"

st.set_page_config(
    page_title="GDELT Network Viz",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Date bounds (cached) ──────────────────────────────────────────────────
bounds = available_date_bounds()
if bounds is None:
    st.warning("Aucune donnée disponible — exécute le pipeline d'ingestion d'abord.")
    st.stop()
min_date, max_date = bounds

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filtres")

    from_date, to_date = st.slider(
        "Période",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="DD/MM/YYYY",
    )

    goldstein_filter: GoldsteinFilter = st.radio(  # type: ignore[assignment]
        "Goldstein category",
        options=["Tous", "Positif", "Négatif", "Neutre"],
        index=0,
    )
    st.markdown("---")
    n_days = (to_date - from_date).days + 1
    total_days = (max_date - min_date).days + 1
    st.caption(f"{n_days} jour(s) sélectionné(s) sur {total_days} disponibles")

# ── Data ──────────────────────────────────────────────────────────────────
edges = load_edges_range(from_date, to_date, goldstein_filter)

with open(_CAMEO_JSON, encoding="utf-8") as f:
    country_names: dict[str, str] = json.load(f)

date_range_label = f"{from_date:%d/%m/%Y} → {to_date:%d/%m/%Y}"
st.markdown(f"**{len(edges)} edge(s)** — {date_range_label} — filtre : *{goldstein_filter}*")

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
