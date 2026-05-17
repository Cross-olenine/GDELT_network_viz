# Research Log — GDELT Network Viz

## 2026-05-14 — Initialisation du pipeline de données (doc-scraper, connection-tester, field-profiler)

### Contexte
Session de démarrage du projet. L'objectif était de passer de zéro à un
contrat de données stabilisé : documenter la structure GDELT, valider la
connexion à la source, profiler un échantillon réel et trancher les
décisions bloquées listées dans intent.md.

### Ce qui a été tenté

**1. doc-scraper — Documentation de l'API GDELT**
Scraping de la documentation officielle GDELT 1.0 Events pour extraire
le schéma complet des 58 colonnes, les URLs de téléchargement bulk et
les contraintes techniques. Résultat consigné dans docs/api-map.md.

**2. connection-tester — Validation de la connexion**
Test de connexion sur le fichier daily du 1er avril 2025
(20150401.export.CSV). Téléchargement, décompression et extraction d'un
échantillon de 500 lignes. Résultat consigné dans docs/connection-report.md
et exploration/data/raw/sample_raw.csv.

**3. field-profiler — Profiling de l'échantillon**
Profiling des champs pertinents pour le pipeline (Actor1CountryCode,
Actor2CountryCode, GoldsteinScale, AvgTone, NumMentions, EventCode) sur
les 500 lignes de l'échantillon. Résultat consigné dans docs/data-contracts.md.

### Résultats clés

- Schéma GDELT 1.0 Events : 58 colonnes documentées dans docs/api-map.md
- Problème TLS : data.gdeltproject.org invalide en HTTPS — HTTP obligatoire
- Connexion HTTP validée : 200 OK, 1 325 ms, 8,8 Mo compressé
- Volumétrie fichier daily 1er avril 2025 : 136 855 événements
- Condition edge (Actor1CountryCode ET Actor2CountryCode non vides) :
  seulement 6% des événements — filtrage massif attendu en production
- Actor1CountryCode rempli à 20,2%, Actor2CountryCode à 51,8% sur 500 lignes
- GoldsteinScale : 100% rempli, borné [-10, +10], 32 valeurs discrètes
  (assignation statique par type d'événement CAMEO — pas un calcul NLP)
- AvgTone : 100% rempli, plage observée [-12,5 ; +11,2]
- Corrélation GoldsteinScale / AvgTone : r = 0,31 (complémentaires,
  non redondants — justifie de conserver les deux)
- Codes pays : système CAMEO hybride — 249 codes ISO 3166-1 alpha-3 +
  27 codes régionaux custom (AFR, MEA, EUR, LAM, SEA, BLK, CAU...)
- Actor1Geo_CountryCode utilise le format FIPS 10-4 2 lettres (différent
  des codes Actor — ne pas mélanger)
- EventCode : zéros de tête présents — dtype=str obligatoire à la lecture
- Incompatibilité critique : Polars crash sur ce CPU (absence AVX2/FMA)

### Décisions prises

**D1 — Dataset GDELT**
GDELT 1.0 Events retenu en priorité. GKG et Mentions non requis en phase 1.
Justification : Events contient GoldsteinScale et les codes pays acteurs,
qui suffisent à construire le réseau relationnel.

**D2 — Métriques relationnelles**
GoldsteinScale en priorité (100% rempli, borné -10/+10, stable, assignation
statique par type d'événement), AvgTone en complémentaire (r=0,31 avec
GoldsteinScale — apporte une dimension contextuelle NLP distincte).

**D3 — Granularité temporelle du MVP**
Fenêtre d'un mois — avril 2026. Un slicer temporel est prévu comme feature
ultérieure pour permettre à l'utilisateur de choisir la période.

**D4 — Agrégation des edges**
4 scores distincts par paire de pays, tous calculés en moyenne pondérée
du GoldsteinScale par log1p(NumMentions) :
- score_positif : moyenne pondérée sur événements avec GoldsteinScale > 0
- score_negatif : moyenne pondérée sur événements avec GoldsteinScale < 0
- score_neutre : moyenne pondérée sur événements avec GoldsteinScale = 0
- score_global : moyenne pondérée sur tous les événements de la paire

La pondération log1p compresse la distribution très asymétrique de
NumMentions (médiane=10, max=1 530 sur l'échantillon) pour éviter qu'un
seul événement très médiatisé écrase les autres.

**D5 — GoldsteinScale = 0**
Catégorie neutre explicite. Comptabilisé dans score_global uniquement.
Exclu de score_positif et score_negatif.

**D6 — Filtre NumMentions**
Aucun filtre appliqué. Tous les événements sont conservés.
La pondération log1p gère l'asymétrie sans nécessiter d'exclusion.

**D7 — Définition d'un edge**
Un edge existe si et seulement si Actor1CountryCode ET Actor2CountryCode
sont tous les deux non vides et correspondent à des États (codes CAMEO à
3 lettres ISO-compatibles, hors codes régionaux custom). Les événements
impliquant des organisations d'un autre pays (état→organisation) sont
conservés mais taggés avec un type d'edge distinct (état→état,
état→org, etc.) pour permettre un filtrage ultérieur dans l'interface.

**D8 — Remplacement de Polars par DuckDB**
Polars est incompatible avec le CPU de développement (absence AVX2/FMA —
crash au démarrage). Décision : DuckDB natif (SQL) pour toutes les
transformations. CLAUDE.md et intent.md sont à mettre à jour en
conséquence.

### Reste ouvert

- Package Python de visualisation réseau superposé à une carte géographique :
  décision non prise — nécessite une phase d'exploration dédiée
- Définition exacte du filtre "code CAMEO = État" : la liste des 27 codes
  régionaux à exclure est à constituer et à intégrer dans data-contracts.md
- Volumétrie réelle sur un mois complet (avril 2026) : non mesurée —
  l'estimation à partir du fichier daily (136 855 × 30 = ~4,1 M événements,
  ~6% utilisables = ~245 000 edges bruts) reste à confirmer
- AvgTone : décision de l'intégrer dans les scores finaux non tranchée —
  sa complémentarité est établie (r=0,31) mais son rôle exact dans
  l'affichage reste ouvert

## 2026-05-17 — POC fonctionnel — diagnostic pays manquants sur la carte

### Corrections appliquées
- Labels trigrammes supprimés des silhouettes SVG
- Tooltips hover fonctionnels : nom complet en français au survol
- Range slider de dates implémenté
- Fond de carte light_nolabels actif

### État actuel
Le POC Streamlit est fonctionnel : la carte s'affiche avec le réseau de relations entre pays, les tooltips hover et le slider temporel sont opérationnels. Certains pays présents dans les données GDELT n'apparaissent pas sur la carte.

### Problèmes identifiés
- Pays absents de la carte malgré leur présence dans les données GDELT : cause non encore diagnostiquée (mismatch de codes pays, absence de géolocalisation, filtre non intentionnel, ou silhouette SVG manquante).

### Prochaine étape
Diagnostiquer et corriger l'absence de certains pays sur la carte.
