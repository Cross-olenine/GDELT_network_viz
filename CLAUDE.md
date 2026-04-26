# CLAUDE.md — GDELT Knowledge Graph

## Vision du projet

Application interactive de visualisation des relations diplomatiques internationales
construite sur les données brutes GDELT 2.0 (Global Database of Events, Language and Tone).

L'utilisateur final peut explorer un knowledge graph des interactions entre pays,
filtrer par type de relation (coopération / conflit), par période, par intensité,
et comprendre la géopolitique mondiale à travers la donnée.

## Architecture fonctionnelle
GDELT Raw CSV (masterfilelist.txt)
↓
[1] EXTRACTION         scripts/load_gdelt_raw.py
Télécharge les fichiers CSV bruts GDELT par mois
Checkpoint pour reprise en cas d'interruption
Output : data/raw/gdelt_events_YYYYMM.csv
↓
[2] CONVERSION         scripts/convert_to_parquet.py  (à créer)
Convertit CSV → Parquet (5x plus petit, 7-10x plus rapide)
Output : data/parquet/gdelt_events_YYYYMM.parquet
↓
[3] TRANSFORMATION     scripts/transform_kg.py  (à créer)
Filtre les événements diplomatiques
Applique les règles qualité
Agrège par paire de pays (nb_interactions, avg_tone, avg_goldstein)
Output : data/processed/gdelt_kg_YYYYMM.parquet
↓
[4] ORCHESTRATION      pipeline/  (à créer)
Prefect flow mensuel automatisant les étapes 1-3
Schedulé le 1er de chaque mois pour le mois précédent
↓
[5] APPLICATION        app/
Streamlit + Vis.js
Lecture des fichiers processed/gdelt_kg_*.parquet via DuckDB
Knowledge graph interactif avec filtres

## Stack technique

| Couche | Outil | Rôle |
|---|---|---|
| Stockage | Parquet | Format colonnaire, 5x plus compact que CSV |
| SQL / EDA | DuckDB | Requêtes analytiques sur CSV et Parquet |
| ETL | Polars lazy | Transformations scalables (200GB+) |
| Orchestration | Prefect | Pipeline mensuel automatisé |
| Graph | NetworkX | Construction et analyse du knowledge graph |
| App | Streamlit | Interface interactive |
| Viz graph | Vis.js | Rendu interactif du knowledge graph |
| Notebooks | Marimo | EDA et exploration uniquement |
| Viz notebooks | Pyvis | Export HTML du graph (exploration) |

## Structure du projet
gdelt-knowledge-graph/
│
├── CLAUDE.md                        ← ce fichier
├── requirements.txt                 ← toutes les dépendances versionnées
├── start.ps1                        ← script de démarrage Windows
│
├── data/
│   ├── raw/                         ← CSV bruts GDELT (non versionnés, lourds)
│   │   └── gdelt_events_YYYYMM.csv
│   ├── parquet/                     ← CSV convertis en Parquet (non versionnés)
│   │   └── gdelt_events_YYYYMM.parquet
│   └── processed/                   ← datasets transformés pour l'app (non versionnés)
│       └── gdelt_kg_YYYYMM.parquet
│
├── app/                             ← Application Streamlit
│   ├── main.py                      ← point d'entrée : streamlit run app/main.py
│   ├── init.py
│   └── components/
│       ├── init.py
│       ├── filters.py               ← panel gauche (filtres interactifs)
│       └── graph.py                 ← rendu Vis.js via st.components.v1.html
│
├── pipeline/                        ← Orchestration Prefect (à créer)
│   ├── init.py
│   └── gdelt_flow.py                ← flow mensuel Prefect
│
├── scripts/                         ← Scripts ETL standalone
│   ├── load_gdelt_raw.py            ← [1] téléchargement CSV bruts
│   ├── convert_to_parquet.py        ← [2] conversion CSV → Parquet (à créer)
│   └── transform_kg.py              ← [3] transformation et agrégation KG (à créer)
│
├── src/                             ← Modules Python réutilisables
│   ├── init.py
│   ├── gdelt_client.py              ← client DOC API GDELT (obsolète, référence)
│   └── graph_builder.py             ← build_graph(relations) → nx.Graph
│
├── notebooks/                       ← Exploration uniquement (Marimo)
│   ├── 01_exploration.py            ← EDA DuckDB + profiling
│   └── 02_graph_viz.py              ← Construction graph + viz Pyvis
│
├── docs/                            ← Documentation
│   └── data_dictionary.md           ← dictionnaire des 61 colonnes GDELT 2.0
│
└── .claude/                         ← Agents Claude Code
    ├── commands/                    ← slash commands (compatibilité)
    └── skills/                      ← agents avec auto-invocation
        ├── review-code/SKILL.md
        ├── review-data-quality/SKILL.md
        └── review-notebook/SKILL.md

## Données GDELT

### Format brut (data/raw/)
- Source : fichiers CSV GDELT 2.0 via masterfilelist.txt
- Fréquence : un fichier toutes les 15 minutes, consolidé par mois
- Format : CSV tab-délimité, 61 colonnes, pas de header natif
- Volume mars 2026 : 3 508 491 lignes, 1.37 GB

### Format Parquet (data/parquet/)
- Conversion depuis CSV brut via DuckDB
- Volume estimé : ~270 MB par mois (5x compression)
- Requêtes 7-10x plus rapides qu'en CSV

### Dataset KG (data/processed/)
- Filtres appliqués :
  - Year = année du mois traité (exclut réindexations)
  - Actor1CountryCode IS NOT NULL
  - Actor2CountryCode IS NOT NULL
  - Actor1CountryCode != Actor2CountryCode
  - EventRootCode IN ('03','04','05','06','07','08')
- Agrégation par paire (Actor1CountryCode, Actor2CountryCode)
- Colonnes : nb_interactions, avg_tone, avg_goldstein, top_event_codes
- Volume mars 2026 : 475 830 lignes, 105 MB (CSV) → ~20 MB (Parquet)

### Qualité des données (résultats profiling mars 2026)
- Actor1CountryCode : 41% nulls → filtrés
- Actor2CountryCode : 53% nulls → filtrés
- GoldsteinScale : 0% nulls, range 1.0-10.0 sur codes diplomatiques
- AvgTone : 0% nulls, moyenne -2.33 (couverture globalement négative)
- Colonnes inutilisables (>99% nulls) : Actor1/2Type3Code, Actor1/2Religion2Code

## Codes CAMEO

### Codes utilisés pour le KG diplomatique
| Code | Label lisible | QuadClass |
|---|---|---|
| 03 | Exprimer intention de coopérer | Coopération verbale |
| 04 | Consulter | Coopération verbale |
| 05 | Engager diplomatiquement | Coopération verbale |
| 06 | Coopérer matériellement | Coopération matérielle |
| 07 | Apporter aide | Coopération matérielle |
| 08 | Céder | Coopération matérielle |

### Métriques clés
- GoldsteinScale : impact théorique de l'acte (-10 à +10), fixe par type CAMEO
- AvgTone : sentiment médiatique moyen (-33 à +28), variable selon contexte
- NumMentions : nombre de citations dans les médias, proxy de l'importance

## Application Streamlit

### Fonctionnalités prévues
- Knowledge graph Vis.js interactif (drag noeud sans bouger les voisins)
- Panel gauche : filtres par type de relation, AvgTone, seuil d'interactions, période
- Coloration arêtes : AvgTone (rouge = conflictuel, vert = coopératif)
- Épaisseur arêtes : nb_interactions
- Tooltip au survol : nom complet du pays, nb_interactions, avg_tone, avg_goldstein
- Sélection arête → tableau des événements associés exportable

### Source de données app
- Lecture DuckDB sur data/processed/gdelt_kg_*.parquet
- Multi-mois : concat à la volée selon la période sélectionnée
- Chargement en mémoire au démarrage pour les requêtes rapides

## Workflow Git

### Branches
| Branche | Rôle |
|---|---|
| master | Code en production, stable |
| preprod | Validation avant mise en production |
| test | Tests automatisés |
| develop | Intégration continue, branche de travail principale |
| feature/* | Une branche par fonctionnalité |

### Convention de travail
- Toute nouvelle fonctionnalité → créer feature/nom-de-la-feature depuis develop
- Merge feature → develop après review
- develop → test → preprod → master via PR
- Ne jamais committer directement sur master ou preprod

### Convention commits
| Préfixe | Usage |
|---|---|
| feat: | Nouvelle fonctionnalité |
| fix: | Correction de bug |
| chore: | Configuration, dépendances |
| docs: | Documentation |
| refactor: | Refactoring sans changement fonctionnel |
| test: | Ajout ou modification de tests |

## Conventions de code

- Langue : code en anglais, commentaires en français
- Chemins : toujours pathlib.Path, jamais de strings brutes
- Variables Marimo locales : préfixe _
- Variables Marimo exportées : sans préfixe
- Nommage DataFrames : nom descriptif du contenu (jamais df, df2, tmp)
- Appels réseau : toujours dans un try/except
- Validation DataFrames : vérifier shape et colonnes après chargement

## Agents Claude Code

### Invocation automatique
- Après création/modification fichier .py dans src/ ou scripts/ → /review-code
- Après collecte ou transformation de données → /review-data-quality
- Après modification d'un notebook Marimo → /review-notebook
- En fin de session → mettre à jour ce CLAUDE.md

### Ce que vérifie /review-code
- Imports présents dans requirements.txt
- Chemins avec pathlib.Path
- Appels réseau dans try/except
- DataFrames validés après chargement
- Conventions Marimo (_ prefix) respectées
- DuckDB utilisé pour l'EDA (pas pandas sur gros volumes)
- Polars lazy pour les transformations ETL

### Ce que vérifie /review-data-quality
- Source : data/parquet/gdelt_events_YYYYMM.parquet (brut)
- Source KG : data/processed/gdelt_kg_YYYYMM.parquet (transformé)
- Schéma 61 colonnes pour le brut, 20 colonnes pour le KG
- Taux de nulls cohérents avec le profiling de référence (mars 2026)
- Pas de doublons sur GlobalEventID
- Pas d'auto-relations (Actor1 != Actor2)
- Distribution temporelle cohérente (pas de trous ni pics suspects)
