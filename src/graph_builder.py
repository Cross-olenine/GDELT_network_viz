"""
Construction du Knowledge Graph diplomatique GDELT
Input  : requête DuckDB sur events
Output : src/graph_builder.py — fonction build_graph()
"""
import networkx as nx
import pandas as pd


def build_graph(relations: pd.DataFrame) -> nx.Graph:
    """
    Construit un graphe non orienté à partir des relations diplomatiques.
    
    Args:
        relations : DataFrame avec colonnes Actor1CountryCode, 
                    Actor2CountryCode, nb_interactions
    Returns:
        G : graphe NetworkX avec noeuds = pays, arêtes = relations
    """
    G = nx.Graph()

    for _, row in relations.iterrows():
        country1 = row["Actor1CountryCode"]
        country2 = row["Actor2CountryCode"]
        weight   = row["nb_interactions"]

        # Si l'arête existe déjà (A→B et B→A), on additionne les poids
        if G.has_edge(country1, country2):
            G[country1][country2]["weight"] += weight
        else:
            G.add_edge(country1, country2, weight=weight)

    return G