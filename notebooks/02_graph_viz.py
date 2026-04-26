import marimo

__generated_with = "0.23.3"
app = marimo.App(width="full")


@app.cell
def _():
    # ── Imports ──
    import sys
    import marimo as mo
    import duckdb
    from pathlib import Path
    from pyvis.network import Network
    sys.path.insert(0, str(Path("..").resolve()))
    from src.graph_builder import build_graph

    return Network, Path, build_graph, duckdb, mo


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
            ROUND(AVG(GoldsteinScale), 2) as avg_goldstein
        FROM events
        WHERE Year = 2026
          AND Actor1CountryCode IS NOT NULL
          AND Actor2CountryCode IS NOT NULL
          AND Actor1CountryCode != Actor2CountryCode
          AND EventRootCode IN ('03','04','05','06','07','08')
        GROUP BY Actor1CountryCode, Actor2CountryCode
        ORDER BY nb_interactions DESC
    """).df()
    return (relations,)


@app.cell
def _(build_graph, relations):
    # ── Construction du graph ──
    G = build_graph(relations)
    return (G,)


@app.cell
def _(G, Network, Path, mo):
    # ── Visualisation Pyvis ──
    _seuil = 500
    _output = Path("data/processed/graph_diplomatique.html")

    _net = Network(height="750px", width="100%", bgcolor="#1a1a2e", font_color="white")
    _net.barnes_hut()

    _degrees = dict(G.degree(weight="weight"))
    _max_deg = max(_degrees.values())

    for _node in G.nodes():
        _size = 10 + 40 * (_degrees[_node] / _max_deg)
        _net.add_node(_node, label=_node, size=_size,
                      title=f"{_node} : {_degrees[_node]:,} interactions")

    for _u, _v, _data in G.edges(data=True):
        if _data["weight"] >= _seuil:
            _width = 1 + 8 * (_data["weight"] / _max_deg)
            _net.add_edge(_u, _v, value=_data["weight"], width=_width,
                          title=f"{_u} ↔ {_v} : {_data['weight']:,} interactions")

    _output.parent.mkdir(parents=True, exist_ok=True)
    _net.save_graph(str(_output))

    with open(_output, "r", encoding="utf-8") as f:
        _html = f.read()

    mo.Html(_html)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
