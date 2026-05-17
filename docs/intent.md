# Intent — GDELT Network Viz

## Intention initiale
Développer une application web Streamlit visualisant les relations
positives/négatives entre pays à partir des données GDELT.
Les pays sont des nœuds positionnés géographiquement sur une carte,
les relations entre deux pays constituent les edges du réseau.

## Cas d'usage cible
[x] Visualisation
[ ] Business Intelligence
[ ] Machine Learning
[ ] Deep Learning

## Architecture applicative
- Ingestion CSV GDELT bulk → DuckDB
- Transformations DuckDB natif (SQL)
- Restitution Streamlit

## Décisions prises
- Source : fichiers CSV GDELT bulk (pas d'API temps réel — trop instable)
- Dataset : GDELT 1.0 Events (GKG et Mentions non requis en phase 1)
- Base de données : DuckDB
- Traitement : DuckDB natif SQL (Polars incompatible CPU — absence AVX2/FMA)
- Frontend : Streamlit
- Les nœuds du réseau sont les pays, positionnés géographiquement sur une carte
- Les edges représentent la relation positive/négative entre deux pays
- Métrique principale : GoldsteinScale (100% rempli, borné -10/+10, stable)
  AvgTone en complémentaire (r=0,31 avec GoldsteinScale — apport contextuel NLP)
- Granularité temporelle : **au jour près**, plage librement choisie par
  l'utilisateur via un range slider de dates couvrant l'historique
  disponible (cf. section "Évolution — filtre temporel au jour" ci-dessous)
- Agrégation : 4 scores par paire de pays, moyenne pondérée GoldsteinScale
  par log1p(NumMentions) : score_positif (GS>0), score_negatif (GS<0),
  score_neutre (GS=0), score_global (tous les événements)
- GoldsteinScale = 0 : catégorie neutre explicite — exclu de score_positif
  et score_negatif, inclus dans score_global
- Filtre NumMentions : aucun — tous les événements conservés
  (la pondération log1p gère l'asymétrie)
- Définition d'un edge : événement avec Actor1CountryCode ET Actor2CountryCode
  non vides, tous deux correspondant à des États (codes CAMEO 3 lettres
  ISO-compatibles, hors codes régionaux custom). Les événements état→organisation
  sont taggés avec un type d'edge distinct pour permettre un filtrage UI.

## Évolution — filtre temporel au jour (2026-05-17)

### Besoin
Remplacer le slicer mensuel (1 cran = 1 fichier Parquet) par un range
slider de dates au jour près couvrant tout l'historique ingéré.

### Problèmes à résoudre
- **Décorrélation Parquet ↔ SQLDATE** : un fichier `year=Y/month=M` peut
  contenir des événements dont le `SQLDATE` est antérieur (rajouts tardifs
  côté GDELT). Le filtrage doit donc se faire sur la colonne `SQLDATE`,
  pas sur l'arborescence Parquet — il faut accepter de scanner tous les
  fichiers et filtrer par valeur.
- **Fluidité du slider** : recalculer la moyenne pondérée
  `Σ log1p(NumMentions)·GoldsteinScale / Σ log1p(NumMentions)` sur
  plusieurs millions de lignes à chaque déplacement du slider serait
  trop lent. Il faut une stratégie d'agrégation et de cache.
- **Équivalence numérique** : la nouvelle stratégie doit produire des
  scores strictement identiques à l'agrégation SQL d'origine (la moyenne
  pondérée est compositionnelle — sommer les poids et les
  numérateurs par sous-période préserve l'exactitude).

### Solution retenue
Pré-agrégation au grain **(jour × actor1 × actor2 × goldstein_category)**
exécutée une seule fois par session (`@st.cache_data`) sur l'ensemble
des Parquet ; chaque mouvement du slider devient une opération `pandas`
en mémoire (filtre + groupby) sur cette table cachée. Les bornes
min/max du slider sont dérivées dynamiquement du min/max de `SQLDATE`
dans la table cachée.

## Décisions bloquées — nécessitent une exploration dédiée

- Comment représenter techniquement le réseau superposé à la carte ?
  (package Python à choisir après phase d'exploration visualisation)

## Questions prioritaires à résoudre en Phase 1
1. Quels champs GDELT encodent les deux pays d'un événement ?
   → Resolue : Actor1CountryCode et Actor2CountryCode (codes CAMEO 3 lettres)
2. Quelle est la distribution réelle du GoldsteinScale et du TONE sur
   un échantillon ?
   → Resolue : GoldsteinScale [-10,+10] 32 valeurs discrètes 100% rempli ;
     AvgTone [-12,5 ; +11,2] 100% rempli ; corrélation r=0,31
3. Quelle est la volumétrie typique sur une fenêtre d'un mois ?
   → Estimée : ~136 855 événements/jour, ~6% utilisables (deux codes pays
     non vides) — volumétrie réelle sur un mois entier à confirmer
4. Les codes pays GDELT sont-ils en ISO 3166 ou un format custom ?
   → Resolue : format CAMEO hybride — 249 codes ISO 3166-1 alpha-3 +
     27 codes régionaux custom à exclure pour les edges État-État
