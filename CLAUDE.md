# CLAUDE.md — gdelt-knowledge-graph

## Description du projet

Knowledge graph des relations diplomatiques internationales construit à partir des données GDELT (Global Database of Events, Language, and Tone). Le projet collecte des événements géopolitiques, les structure en triplets sémantiques et les visualise sous forme de graphe interactif.

## Stack technique

| Rôle | Bibliothèque |
|---|---|
| Collecte GDELT | `gdeltdoc` |
| Traitement des données | `pandas` |
| Graphe | `networkx` |
| Notebooks interactifs | `marimo` |
| Visualisation graphe | `pyvis` |
| Visualisation données | `plotly` |

## Modèle de données cible

Chaque relation est représentée comme un triplet :

```
(sujet, prédicat, objet)
```

Avec les métadonnées associées :

| Champ | Description |
|---|---|
| `date` | Date de l'événement |
| `source` | Source de l'article |
| `tone` | Ton de l'article (score GDELT) |
| `url` | URL de l'article source |

## Codes CAMEO prioritaires

| Code | Prédicat |
|---|---|
| 036 | coopère_avec |
| 040 | consulte |
| 046 | coopération_diplomatique |
| 057 | signe_accord_avec |
| 061 | coopère_économiquement_avec |
| 100 | exige_de |
| 112 | critique |
| 120 | rejette |
| 163 | impose_sanctions_à |
| 172 | conflit_militaire_avec |

## Conventions de code

- **Langue** : code en anglais, commentaires en français
- **Chemins** : utiliser `pathlib.Path` (jamais `os.path`)
- **Réseau** : toujours entourer les appels réseau d'un `try/except`
- **DataFrames** : valider le contenu du DataFrame après chargement (colonnes attendues, types, valeurs nulles)

## État d'avancement

- Structure du projet initialisée (`src/`, `notebooks/`, `scripts/`, `.claude/`)
- API GDELT validée et fonctionnelle en local
- `gdelt_client.py` opérationnel avec retry backoff et timeout 30s
- Notebook EDA `01_exploration.py` en cours de validation

## Décisions techniques prises

- `gdeltdoc==1.12.0` obligatoire — la 1.3.0 est incompatible avec `start_date`/`end_date`
- Utiliser `start_date`/`end_date` plutôt que `timespan` (plus stable)
- La colonne `tone` n'est **pas** retournée par `article_search` — elle appartient au GKG
- Le filtre `language="English"` est appliqué par défaut dans `collect_articles`
- Retry backoff `[10s, 30s, 60s]` pour gérer le rate limit GDELT
- Timeout de 30s sur les appels HTTP via `ThreadPoolExecutor` (`GdeltDoc` v1.12+ n'expose pas de session `requests`)
- Branche `develop` pour le travail quotidien, `main` pour le code validé

## Limites connues de l'API confirmées en pratique

- Rate limit strict : attendre entre les appels successifs
- `ConnectTimeout` possible sur les grosses requêtes (>100 records, >1 semaine)
- Commencer par des petites fenêtres (7 jours, 25 records) pour valider

## Prochaines étapes

- Valider le notebook EDA `01_exploration.py` end-to-end
- Construire `src/graph_builder.py`
- Créer le notebook de visualisation `02_graph_viz.py`

## Règle de mise à jour

À la fin de chaque session, mettre à jour `CLAUDE.md` avec l'état d'avancement, les décisions prises et les prochaines étapes.

## Règles d'invocation automatique

Ces règles sont obligatoires et s'appliquent systématiquement pendant toute la session, sans exception et sans attendre une demande explicite.

1. **Après chaque création ou modification d'un fichier `.py` dans `src/` ou `notebooks/`** — invoquer immédiatement `/review-code` sur ce fichier avant de continuer.

2. **Après chaque appel à l'API GDELT ou chaque chargement d'un fichier depuis `data/`** — invoquer immédiatement `/review-data-quality` sur le DataFrame résultant avant toute transformation.

3. **Après chaque création ou modification d'un fichier `.py` dans `notebooks/`** — invoquer `/review-notebook` sur ce fichier en complément de `/review-code` (les deux revues sont cumulatives).
