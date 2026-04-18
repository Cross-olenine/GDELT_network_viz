# gdelt-knowledge-graph

Knowledge graph des relations diplomatiques internationales construit à partir des données GDELT.

## Stack

| Rôle | Bibliothèque | Version |
|---|---|---|
| Collecte GDELT | `gdeltdoc` | 1.3.0 |
| Traitement des données | `pandas` | 2.2.3 |
| Requêtes HTTP | `requests` | 2.32.3 |
| Graphe | `networkx` | 3.4.2 |
| Notebooks interactifs | `marimo` | 0.10.12 |
| Visualisation graphe | `pyvis` | 0.3.2 |
| Visualisation données | `plotly` | 5.24.1 |

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```
