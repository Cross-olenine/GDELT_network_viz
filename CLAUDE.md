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

## Règles d'invocation automatique

Ces règles sont obligatoires et s'appliquent systématiquement pendant toute la session, sans exception et sans attendre une demande explicite.

1. **Après chaque création ou modification d'un fichier `.py` dans `src/` ou `notebooks/`** — invoquer immédiatement `/review-code` sur ce fichier avant de continuer.

2. **Après chaque appel à l'API GDELT ou chaque chargement d'un fichier depuis `data/`** — invoquer immédiatement `/review-data-quality` sur le DataFrame résultant avant toute transformation.

3. **Après chaque création ou modification d'un fichier `.py` dans `notebooks/`** — invoquer `/review-notebook` sur ce fichier en complément de `/review-code` (les deux revues sont cumulatives).
