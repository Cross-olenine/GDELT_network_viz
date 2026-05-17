"""Streamlit entry point — GDELT Network Viz POC."""

import json
from pathlib import Path

import streamlit as st

from data import load_edges_range, list_available_months, ym_label, GoldsteinFilter

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

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filtres")

    if len(available) >= 2:
        idx_min, idx_max = st.select_slider(
            "Période",
            options=list(range(len(available))),
            value=(0, len(available) - 1),
            format_func=lambda i: ym_label(*available[i]),
        )
    else:
        idx_min, idx_max = 0, max(0, len(available) - 1)

    from_ym = available[idx_min]
    to_ym   = available[idx_max]

    goldstein_filter: GoldsteinFilter = st.radio(  # type: ignore[assignment]
        "Goldstein category",
        options=["Tous", "Positif", "Négatif", "Neutre"],
        index=0,
    )
    st.markdown("---")
    n_months = idx_max - idx_min + 1
    st.caption(f"{n_months} mois sélectionné(s) sur {len(available)} disponibles")

# ── Data ──────────────────────────────────────────────────────────────────
edges = load_edges_range(from_ym, to_ym, goldstein_filter)

with open(_CAMEO_JSON, encoding="utf-8") as f:
    country_names: dict[str, str] = json.load(f)

date_range_label = f"{ym_label(*from_ym)} → {ym_label(*to_ym)}"
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
