import marimo

__generated_with = "0.23.3"
app = marimo.App(width="full")


@app.cell
def _():
    # ── Imports ──
    import sys
    import marimo as mo
    import duckdb
    import pycountry
    from pathlib import Path
    from pyvis.network import Network
    sys.path.insert(0, str(Path("..").resolve()))
    from src.graph_builder import build_graph

    return Network, Path, build_graph, duckdb, mo, pycountry


@app.cell
def _(Path, duckdb):
    # ── Données ──
    _data_raw = Path("data/raw/gdelt_events_202603.csv")
    con = duckdb.connect()
    con.execute(f"CREATE VIEW events AS SELECT * FROM read_csv_auto('{_data_raw}', ignore_errors=true)")

    relations = con.execute("""
        SELECT 
            Actor1CountryCode,
            Actor2CountryCode,
            COUNT(*) as nb_interactions,
            ROUND(AVG(CAST(GoldsteinScale AS DOUBLE)), 2) as avg_goldstein
        FROM events
        WHERE Year = 2026
          AND Actor1CountryCode IS NOT NULL
          AND Actor2CountryCode IS NOT NULL
          AND Actor1CountryCode != Actor2CountryCode
          AND EventRootCode IN ('03','04','05','06','07','08')
        GROUP BY Actor1CountryCode, Actor2CountryCode
        ORDER BY nb_interactions DESC
    """).df()
    return con, relations


@app.cell
def _(build_graph, relations):
    # ── Construction du graph ──
    G = build_graph(relations)
    return (G,)


@app.cell
def _(G, Network, Path, mo, pycountry, relations):
    # ── Visualisation Pyvis ──

    def _country_name(code):
        try:
            return pycountry.countries.get(alpha_3=code).name
        except:
            return code

    def _goldstein_to_color(score):
        _normalized = max(0, min(1, (score + 10) / 20))
        _r = int(255 * (1 - _normalized))
        _g = int(255 * _normalized)
        return f"#{_r:02x}{_g:02x}00"

    _SEUIL = 10
    _OUTPUT = Path("data/processed/graph_diplomatique.html")

    _net = Network(height="100vh", width="100%", bgcolor="#1a1a2e", font_color="white")
    _net.barnes_hut()

    _degrees = dict(G.degree(weight="weight"))
    _max_deg = max(_degrees.values())

    # Noeuds actifs uniquement (avec au moins une arête au-dessus du seuil)
    _active_nodes = set()
    for _u, _v, _data in G.edges(data=True):
        if _data["weight"] >= _SEUIL:
            _active_nodes.add(_u)
            _active_nodes.add(_v)

    for _node in _active_nodes:
        _size = 10 + 40 * (_degrees[_node] / _max_deg)
        _net.add_node(
            _node,
            label=_node,
            title=f"{_country_name(_node)}<br>Interactions : {_degrees[_node]:,}",
            size=_size
        )

    # Map GoldsteinScale par paire de pays
    _goldstein_map = {
        (_row["Actor1CountryCode"], _row["Actor2CountryCode"]): _row["avg_goldstein"]
        for _, _row in relations.iterrows()
    }

    for _u, _v, _data in G.edges(data=True):
        if _data["weight"] >= _SEUIL:
            _g1 = _goldstein_map.get((_u, _v), 0)
            _g2 = _goldstein_map.get((_v, _u), 0)
            _avg_g = (_g1 + _g2) / 2
            _net.add_edge(
                _u, _v,
                value=_data["weight"],
                width=1 + 8 * (_data["weight"] / _max_deg),
                color=_goldstein_to_color(_avg_g),
                title=(
                    f"{_country_name(_u)} ↔ {_country_name(_v)}<br>"
                    f"Interactions : {_data['weight']:,}<br>"
                    f"GoldsteinScale moyen : {_avg_g:.2f}"
                )
            )

    _net.set_options("""
    {
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -8000,
                "springLength": 200
            }
        },
        "edges": { "smooth": { "type": "continuous" } }
    }
    """)

    _OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _net.save_graph(str(_OUTPUT))

    with open(_OUTPUT, "r", encoding="utf-8") as f:
        _html = f.read()

    _html = _html.replace(
        "<body>",
        "<body style='margin:0;padding:0;overflow:hidden;background:#1a1a2e;'>"
    )

    mo.Html(_html)
    return


@app.cell
def _(con):
    diagnostic = con.execute("""
        SELECT 
            MIN(CAST(GoldsteinScale AS DOUBLE)) as min_g,
            MAX(CAST(GoldsteinScale AS DOUBLE)) as max_g,
            AVG(CAST(GoldsteinScale AS DOUBLE)) as avg_g,
            COUNT(*) FILTER (WHERE CAST(GoldsteinScale AS DOUBLE) > 0) as positifs,
            COUNT(*) FILTER (WHERE CAST(GoldsteinScale AS DOUBLE) < 0) as negatifs,
            COUNT(*) FILTER (WHERE CAST(GoldsteinScale AS DOUBLE) = 0) as zeros
        FROM events
        WHERE Year = 2026
          AND EventRootCode IN ('03','04','05','06','07','08')
    """).df()
    diagnostic
    return


if __name__ == "__main__":
    app.run()
