# Data Contracts — GDELT Events 1.0
Généré le : 2026-05-14
Source : exploration/data/raw/sample_raw.csv (500 lignes, fichier du 1er avril 2025)
Profiling produit par : field-profiler

---

## Vue d'ensemble

- Lignes : 500
- Colonnes : 58
- Encodage : UTF-8 sans BOM (confirmé)
- Délimiteur dans le fichier sample : virgule (le fichier brut GDELT est tab-délimité — la conversion a été faite lors de l'extraction)
- En-tête : présente dans sample_raw.csv (absente dans les fichiers bruts GDELT)
- DATEADDED : toutes les lignes portent la date 20250401 — l'échantillon provient intégralement du fichier journalier du 1er avril 2025
- SQLDATE : 4 dates distinctes présentes (voir section SQLDATE)
- Taux de remplissage global : très hétérogène selon les colonnes — les champs d'identification acteur (codes pays, noms, types, ethnies, religions) sont majoritairement vides ; les champs d'événement et scores sont complets à 100%

---

## Schéma — GDELT Events 1.0

| # | Champ | Type documenté (api-map.md) | Type réel observé | Description | Écart |
|---|-------|----------------------------|-------------------|-------------|-------|
| 1 | GLOBALEVENTID | bigint | int64 | Identifiant unique global de l'événement | Conforme. 500 valeurs distinctes, consécutives |
| 2 | SQLDATE | int | int64 | Date événement, format YYYYMMDD | Conforme |
| 3 | MonthYear | char(6) | int64 | Mois-année, format YYYYMM | Ecart : documenté char(6), lu int64 par pandas. Valeurs numériques pures (ex : 202404) — aucune perte de données mais parsing requis |
| 4 | Year | char(4) | int64 | Année, format YYYY | Même écart que MonthYear — int64 en pratique |
| 5 | FractionDate | double | float64 | Date décimale (ex : 2024.2493) | Conforme |
| 6 | Actor1Code | char(3) | str | Code CAMEO complet acteur 1 | Conforme. 33.6% de remplissage |
| 7 | Actor1Name | char(255) | str | Nom acteur 1, texte libre majuscules ASCII | Conforme. 33.6% de remplissage |
| 8 | Actor1CountryCode | char(3) | str | Code pays CAMEO acteur 1 | Conforme. 20.2% de remplissage — vide quand l'acteur n'est pas un État |
| 9 | Actor1KnownGroupCode | char(3) | str | Code groupe connu acteur 1 | Conforme. 0.2% de remplissage (quasi absent) |
| 10 | Actor1EthnicCode | char(3) | float64 | Code ethnique acteur 1 | Ecart : documenté char(3), lu float64 (toutes valeurs vides — pandas infère NaN) |
| 11 | Actor1Religion1Code | char(3) | float64 | Code religion principale acteur 1 | Même écart — 0% de remplissage sur cet échantillon |
| 12 | Actor1Religion2Code | char(3) | float64 | Code religion secondaire acteur 1 | Même écart — 0% de remplissage |
| 13 | Actor1Type1Code | char(3) | str | Code type principal acteur 1 | Conforme. 16.4% de remplissage |
| 14 | Actor1Type2Code | char(3) | str | Code type secondaire acteur 1 | Conforme. 0.4% de remplissage |
| 15 | Actor1Type3Code | char(3) | float64 | Code type tertiaire acteur 1 | Ecart : documenté char(3), lu float64 (0% de remplissage) |
| 16 | Actor2Code | char(3) | str | Code CAMEO complet acteur 2 | Conforme. 84.4% de remplissage |
| 17 | Actor2Name | char(255) | str | Nom acteur 2, texte libre majuscules ASCII | Conforme. 84.4% de remplissage |
| 18 | Actor2CountryCode | char(3) | str | Code pays CAMEO acteur 2 | Conforme. 51.8% de remplissage |
| 19 | Actor2KnownGroupCode | char(3) | str | Code groupe connu acteur 2 | Conforme. 0.6% de remplissage |
| 20 | Actor2EthnicCode | char(3) | str | Code ethnique acteur 2 | Conforme (str). 0.6% de remplissage |
| 21 | Actor2Religion1Code | char(3) | str | Code religion principale acteur 2 | Conforme. 0.4% de remplissage |
| 22 | Actor2Religion2Code | char(3) | str | Code religion secondaire acteur 2 | Conforme. 0.2% de remplissage |
| 23 | Actor2Type1Code | char(3) | str | Code type principal acteur 2 | Conforme. 35.4% de remplissage |
| 24 | Actor2Type2Code | char(3) | str | Code type secondaire acteur 2 | Conforme. 1.4% de remplissage |
| 25 | Actor2Type3Code | char(3) | float64 | Code type tertiaire acteur 2 | Ecart : documenté char(3), lu float64 (0% de remplissage) |
| 26 | IsRootEvent | int | int64 | 1 si événement racine, 0 sinon | Conforme. Valeurs : {1: 332, 0: 168} |
| 27 | EventCode | char(4) | int64 | Code CAMEO de l'événement | Ecart critique : documenté char(4), lu int64 par pandas — supprime les zéros de tête (ex : "080" lu comme 80). Nécessite lecture en str |
| 28 | EventBaseCode | char(4) | int64 | Code CAMEO niveau 2 | Même écart critique que EventCode — zéros tête perdus |
| 29 | EventRootCode | char(4) | int64 | Code CAMEO niveau 1 (racine) | Même écart critique |
| 30 | QuadClass | int | int64 | 1=Coop verbale, 2=Coop mat., 3=Conflit verbal, 4=Conflit mat. | Conforme |
| 31 | GoldsteinScale | double | float64 | Score Goldstein -10 à +10 | Conforme. 100% rempli, plage observée [-10.0 ; +10.0] |
| 32 | NumMentions | int | int64 | Nombre total de mentions | Conforme |
| 33 | NumSources | int | int64 | Nombre de domaines sources distincts | Conforme |
| 34 | NumArticles | int | int64 | Nombre d'articles distincts | Conforme |
| 35 | AvgTone | double | float64 | Ton émotionnel moyen des articles sources | Conforme. Plage observée [-12.5 ; +11.2] — bien inférieure à la plage théorique -100/+100 |
| 36 | Actor1Geo_Type | int | int64 | 0=inconnu, 1=pays, 2=US état, 3=US ville, 4=monde ville, 5=lac | Conforme. 100% rempli (0 quand géo inconnue) |
| 37 | Actor1Geo_FullName | char(255) | str | Nom géographique complet acteur 1 | Conforme. 31.0% de remplissage |
| 38 | Actor1Geo_CountryCode | char(2) | str | Code pays FIPS 10-4 acteur 1 (2 lettres) | Conforme. 31.0% de remplissage |
| 39 | Actor1Geo_ADM1Code | char(4) | str | Code région administrative niveau 1 acteur 1 | Conforme. 31.0% de remplissage |
| 40 | Actor1Geo_Lat | float | float64 | Latitude acteur 1 | Conforme. 31.0% de remplissage |
| 41 | Actor1Geo_Long | float | float64 | Longitude acteur 1 | Conforme. 31.0% de remplissage |
| 42 | Actor1Geo_FeatureID | int | str | Identifiant GNS/GNIS feature géo acteur 1 | Ecart : documenté int, lu str (contient des valeurs négatives et identifiants mixtes) |
| 43 | Actor2Geo_Type | int | int64 | Mêmes valeurs que Actor1Geo_Type | Conforme. 100% rempli |
| 44 | Actor2Geo_FullName | char(255) | str | Nom géographique complet acteur 2 | Conforme. 77.4% de remplissage |
| 45 | Actor2Geo_CountryCode | char(2) | str | Code pays FIPS 10-4 acteur 2 (2 lettres) | Conforme. 77.8% de remplissage |
| 46 | Actor2Geo_ADM1Code | char(4) | str | Code région administrative niveau 1 acteur 2 | Conforme. 77.8% de remplissage |
| 47 | Actor2Geo_Lat | float | float64 | Latitude acteur 2 | Conforme. 77.4% de remplissage |
| 48 | Actor2Geo_Long | float | float64 | Longitude acteur 2 | Conforme. 77.4% de remplissage |
| 49 | Actor2Geo_FeatureID | int | str | Identifiant GNS/GNIS feature géo acteur 2 | Ecart : documenté int, lu str |
| 50 | ActionGeo_Type | int | int64 | Mêmes valeurs que Actor1Geo_Type | Conforme. 100% rempli |
| 51 | ActionGeo_FullName | char(255) | str | Nom géographique complet de l'action | Conforme. 92.0% de remplissage |
| 52 | ActionGeo_CountryCode | char(2) | str | Code pays FIPS 10-4 de l'action | Conforme. 92.4% de remplissage |
| 53 | ActionGeo_ADM1Code | char(4) | str | Code région administrative niveau 1 action | Conforme. 92.4% de remplissage |
| 54 | ActionGeo_Lat | float | float64 | Latitude de l'action | Conforme. 92.0% de remplissage |
| 55 | ActionGeo_Long | float | float64 | Longitude de l'action | Conforme. 92.0% de remplissage |
| 56 | ActionGeo_FeatureID | int | str | Identifiant GNS/GNIS feature géo action | Ecart : documenté int, lu str |
| 57 | DATEADDED | int | int64 | Date d'ajout dans la base, format YYYYMMDD | Conforme. Valeur unique : 20250401 (échantillon mono-journée) |
| 58 | SOURCEURL | char(255) | str | URL de l'article source principal | Conforme. 100% rempli, longueurs 31–222 caractères |

### Récapitulatif des écarts schéma

| Champ | Écart |
|-------|-------|
| MonthYear, Year | Documentés char — pandas infère int64. Sans impact sémantique mais parsing requis si traitement comme chaîne |
| EventCode, EventBaseCode, EventRootCode | Documentés char(4) — pandas infère int64 et supprime les zéros de tête. Ecart critique : "080" devient 80. Lire obligatoirement en str |
| Actor1EthnicCode, Actor1Religion1Code, Actor1Religion2Code, Actor1Type3Code, Actor2Type3Code | Documentés char(3) — pandas infère float64 (colonnes 100% vides sur cet échantillon). Comportement correct sur données réelles si remplis |
| Actor1Geo_FeatureID, Actor2Geo_FeatureID, ActionGeo_FeatureID | Documentés int — lu str (valeurs négatives observées) |

---

## Métriques synthétiques

| Champ | Remplissage | Valeurs uniques | Min | Max | Moyenne | Médiane | Notes |
|-------|-------------|-----------------|-----|-----|---------|---------|-------|
| GLOBALEVENTID | 100% | 500 | 1235399190 | 1235399689 | - | - | IDs consécutifs, séquence sans trou |
| SQLDATE | 100% | 4 | 20240401 | 20250401 | - | - | 4 dates distinctes dans l'échantillon |
| MonthYear | 100% | 3 | 202404 | 202504 | - | - | - |
| Year | 100% | 2 | 2024 | 2025 | - | - | - |
| FractionDate | 100% | 4 | 2024.249 | 2025.249 | - | - | - |
| Actor1Code | 33.6% | 52 | - | - | - | - | Chaîne vide si absent |
| Actor1Name | 33.6% | 47 | len=4 | len=25 | len~10 | - | Majuscules ASCII, texte libre |
| Actor1CountryCode | 20.2% | 14 | - | - | - | - | 1 code régional CAMEO (AFR) sur 101 valeurs renseignées |
| Actor1KnownGroupCode | 0.2% | 1 | - | - | - | - | Seule valeur : TAL (Taliban) |
| Actor1EthnicCode | 0.0% | 0 | - | - | - | - | 100% vide sur cet échantillon |
| Actor1Religion1Code | 0.0% | 0 | - | - | - | - | 100% vide |
| Actor1Religion2Code | 0.0% | 0 | - | - | - | - | 100% vide |
| Actor1Type1Code | 16.4% | 7 | - | - | - | - | Types : GOV, BUS, MIL, LAB, etc. |
| Actor1Type2Code | 0.4% | 2 | - | - | - | - | Quasi absent |
| Actor1Type3Code | 0.0% | 0 | - | - | - | - | 100% vide |
| Actor2Code | 84.4% | 97 | - | - | - | - | Plus rempli que Actor1Code |
| Actor2Name | 84.4% | 145 | len=3 | len=40 | len~12 | - | Majuscules ASCII |
| Actor2CountryCode | 51.8% | 34 | - | - | - | - | 0 code régional CAMEO sur 259 valeurs |
| Actor2KnownGroupCode | 0.6% | 3 | - | - | - | - | Rare |
| Actor2EthnicCode | 0.6% | 3 | - | - | - | - | Rare |
| Actor2Religion1Code | 0.4% | 2 | - | - | - | - | Quasi absent |
| Actor2Religion2Code | 0.2% | 1 | - | - | - | - | Quasi absent |
| Actor2Type1Code | 35.4% | 9 | - | - | - | - | - |
| Actor2Type2Code | 1.4% | 4 | - | - | - | - | Quasi absent |
| Actor2Type3Code | 0.0% | 0 | - | - | - | - | 100% vide |
| IsRootEvent | 100% | 2 | 0 | 1 | - | - | {1: 66.4%, 0: 33.6%} |
| EventCode | 100% | 60 | - | - | - | - | 3 ou 4 caractères (padding zéro requis à la lecture) |
| EventBaseCode | 100% | 32 | - | - | - | - | Même contrainte que EventCode |
| EventRootCode | 100% | 17 | - | - | - | - | Même contrainte |
| QuadClass | 100% | 4 | 1 | 4 | - | - | {1: 69.8%, 2: 7.8%, 3: 10.8%, 4: 11.6%} |
| GoldsteinScale | 100% | 32 | -10.0 | 10.0 | 1.00 | 1.90 | Distribution asymétrique, std=4.42 |
| NumMentions | 100% | 125 | 1 | 1530 | 72.6 | 10.0 | Distribution très asymétrique — P95=412 |
| NumSources | 100% | 64 | 1 | 159 | 10.1 | - | - |
| NumArticles | 100% | 125 | 1 | 1530 | 68.5 | - | NumArticles identique à NumMentions sur cet échantillon |
| AvgTone | 100% | 320 | -12.50 | 11.21 | -1.57 | -1.39 | std=3.65, 3 valeurs > mean+3std |
| Actor1Geo_Type | 100% | 5 | 0 | 4 | - | - | 69% = 0 (géo inconnue) |
| Actor1Geo_FullName | 31.0% | 155 | - | - | - | - | - |
| Actor1Geo_CountryCode | 31.0% | 41 | - | - | - | - | FIPS 2 lettres |
| Actor1Geo_ADM1Code | 31.0% | 101 | - | - | - | - | - |
| Actor1Geo_Lat | 31.0% | 128 | - | - | - | - | - |
| Actor1Geo_Long | 31.0% | 128 | - | - | - | - | - |
| Actor1Geo_FeatureID | 31.0% | 129 | - | - | - | - | str, peut être négatif |
| Actor2Geo_Type | 100% | 6 | 0 | 5 | - | - | Distribution plus riche que Actor1Geo_Type |
| Actor2Geo_FullName | 77.4% | 217 | - | - | - | - | - |
| Actor2Geo_CountryCode | 77.8% | 49 | - | - | - | - | FIPS 2 lettres |
| Actor2Geo_ADM1Code | 77.8% | 141 | - | - | - | - | - |
| Actor2Geo_Lat | 77.4% | 192 | - | - | - | - | - |
| Actor2Geo_Long | 77.4% | 192 | - | - | - | - | - |
| Actor2Geo_FeatureID | 77.8% | 195 | - | - | - | str |
| ActionGeo_Type | 100% | 6 | 0 | 5 | - | - | 92% rempli (type != 0) |
| ActionGeo_FullName | 92.0% | 308 | - | - | - | - | Champ le plus rempli parmi les Geo |
| ActionGeo_CountryCode | 92.4% | 66 | - | - | - | - | FIPS 2 lettres |
| ActionGeo_ADM1Code | 92.4% | 208 | - | - | - | - | - |
| ActionGeo_Lat | 92.0% | 310 | - | - | - | - | - |
| ActionGeo_Long | 92.0% | 310 | - | - | - | - | - |
| ActionGeo_FeatureID | 92.4% | 312 | - | - | - | - | str |
| DATEADDED | 100% | 1 | 20250401 | 20250401 | - | - | Valeur unique — échantillon mono-journée |
| SOURCEURL | 100% | 500 | len=31 | len=222 | len~106 | - | 500 URLs distinctes |

---

## Champs prioritaires — contrats de données

### Actor1CountryCode
- Type documenté : char(3)
- Type observé : str (chaîne vide si absent, jamais NaN Python)
- Remplissage : 20.2% (101/500 non vides)
- Valeurs uniques : 14
- Top valeurs :
  - AUS : 22 (4.4%)
  - CAN : 21 (4.2%)
  - USA : 17 (3.4%)
  - AFG : 9 (1.8%)
  - ARG : 7 (1.4%)
  - VEN : 4 (0.8%)
  - AUT : 4 (0.8%)
  - BRA : 4 (0.8%)
  - SDN : 3 (0.6%)
  - DEU : 3 (0.6%)
  - BEL, BMU, BRB, AFR : moins de 3 occurrences chacun
- Codes régionaux CAMEO présents : AFR (1 occurrence — 1.0% des valeurs renseignées)
- Codes non-ISO observés : AFR (Afrique, code régional CAMEO)
- Comportement des vides : chaîne vide '' (pas de NaN) — 399/500 lignes vides
- Nulls Python/NaN : 0
- Contrat pipeline : filtrer les lignes où Actor1CountryCode == '' avant construction du graphe. Exclure ou isoler les codes régionaux CAMEO (non rattachables à un noeud pays géolocalisable). Lire la colonne en str obligatoirement.

### Actor2CountryCode
- Type documenté : char(3)
- Type observé : str (chaîne vide si absent, jamais NaN Python)
- Remplissage : 51.8% (259/500 non vides)
- Valeurs uniques : 34
- Top valeurs :
  - USA : 126 (25.2%)
  - CAN : 16 (3.2%)
  - RUS : 10 (2.0%)
  - GBR : 10 (2.0%)
  - CHN : 9 (1.8%)
  - AUS : 8 (1.6%)
  - IND : 8 (1.6%)
  - AFG : 7 (1.4%)
  - VEN : 6 (1.2%)
  - UKR : 6 (1.2%)
  - Et 24 autres codes
- Codes régionaux CAMEO présents : aucun observé sur cet échantillon
- Code PSE (Palestine) présent : 4 occurrences — code CAMEO non-ISO standard
- Comportement des vides : chaîne vide '' — 241/500 lignes vides
- Nulls Python/NaN : 0
- Contrat pipeline : filtrer les lignes où Actor2CountryCode == '' avant construction du graphe. PSE à traiter comme code pays valide (territoire géolocalisable). Lire en str obligatoirement.

### GoldsteinScale
- Type documenté : double
- Type observé : float64
- Remplissage : 100% (500/500) — aucun null ni vide observé
- Plage observée : -10.0 à +10.0 (conforme à la documentation)
- Distribution :
  - Min : -10.0 | Q1 : 0.0 | Médiane : 1.9 | Q3 : 3.4 | Max : 10.0
  - Moyenne : 1.00 | Ecart-type : 4.42
  - Valeurs discrètes les plus fréquentes : 1.9 (69 obs, 13.8%), 0.0 (46 obs, 9.2%), 2.8 (52 obs, 10.4%), 3.0 (42 obs, 8.4%), -2.0 (37 obs, 7.4%), -10.0 (25 obs, 5.0%)
- Valeurs aberrantes (> 3 ecarts-types) : 0
- Valeurs distinctes : 32 — valeurs discrètes fixes par type d'événement CAMEO (lookup statique)
- Nulls : 0 sur cet échantillon
- Contrat pipeline : pas de filtrage requis. Utiliser directement comme score relationnel. Valeur de lookup fixe — pas un score NLP.

### AvgTone
- Type documenté : double (plage théorique -100 à +100)
- Type observé : float64
- Remplissage : 100% (500/500)
- Plage observée : -12.50 à +11.21
- Distribution par tranches :
  - (-15, -10] : 8 (1.6%)
  - (-10, -5]  : 75 (15.0%)
  - (-5, -2]   : 138 (27.6%)
  - (-2, 0]    : 101 (20.2%)
  - (0, 2]     : 105 (21.0%)
  - (2, 5]     : 59 (11.8%)
  - (5, 10]    : 11 (2.2%)
  - (10, 15]   : 3 (0.6%)
- Q1 : -3.98 | Médiane : -1.39 | Moyenne : -1.57 | Q3 : 0.88 | Ecart-type : 3.65
- Valeurs aberrantes (seuil mean+3std = +9.38) : 3 lignes (AvgTone entre +10.2 et +11.2 — articles très positifs, valeurs légitimes)
- Corrélation avec GoldsteinScale : 0.31 (positive modérée — les deux métriques sont partiellement cohérentes mais mesurent des choses différentes)
- Nulls : 0 sur cet échantillon
- Contrat pipeline : plage effective à retenir [-15 ; +12]. Conserver les outliers — valeurs légitimes. La corrélation faible avec GoldsteinScale confirme qu'AvgTone et GoldsteinScale apportent une information complémentaire.

### SQLDATE
- Type documenté : int, format YYYYMMDD
- Type observé : int64
- Remplissage : 100%
- Plage observée : 20240401 à 20250401
- Valeurs distinctes : 4 (20240401, 20250101, 20250201, 20250401)
- Note : l'échantillon couvre 4 dates distinctes dans un fichier daily du 20250401. SQLDATE = date de l'événement (peut différer de DATEADDED). DATEADDED est uniformément 20250401.
- Contrat pipeline : utiliser SQLDATE pour le filtrage temporel, pas DATEADDED. Format int YYYYMMDD — convertir en date pour les filtres par plage.

### NumMentions
- Type documenté : int
- Type observé : int64
- Remplissage : 100%
- Distribution :
  - Min : 1 | P25 : 4 | Médiane : 10 | P75 : 40 | P90 : 169 | P95 : 412 | Max : 1530
  - Moyenne : 72.6 | Ecart-type : 192.7
- Distribution très asymétrique : 55.4% des événements ont 10 mentions ou moins
- Valeurs aberrantes (> mean+3std = 650) : 15 lignes (valeurs entre 692 et 1530)
- Valeurs = 1 : 23 lignes (4.6%)
- Contrat pipeline : utiliser comme pondération des edges. Distribution asymétrique — appliquer log1p(NumMentions) pour la pondération visuelle. Les 15 valeurs > 650 sont des événements très médiatisés — à conserver.

### EventCode
- Type documenté : char(4)
- Type observé en lecture pandas par défaut : int64 — ECART CRITIQUE : les zéros de tête sont perdus ("080" devient 80)
- Lire obligatoirement avec dtype=str
- Remplissage : 100%
- Longueur des codes : 3 caractères (492/500 lignes) ou 4 caractères (8/500 lignes)
- Codes à 4 caractères observés : 0831, 1123, 0353, 0874 — sous-types CAMEO
- Valeurs uniques : 60
- Top 10 codes :
  - 042 : 69 (13.8%)
  - 043 : 52 (10.4%)
  - 020 : 42 (8.4%)
  - 010 : 31 (6.2%)
  - 051 : 31 (6.2%)
  - 036 : 29 (5.8%)
  - 040 : 24 (4.8%)
  - 190 : 21 (4.2%)
  - 046 : 20 (4.0%)
  - 112 : 19 (3.8%)
- Contrat pipeline : lire en str, conserver le padding zéro, ne jamais convertir en int.

### QuadClass
- Type documenté : int (1–4)
- Type observé : int64
- Remplissage : 100%
- Distribution :
  - 1 (Coopération verbale) : 349 (69.8%)
  - 2 (Coopération matérielle) : 39 (7.8%)
  - 3 (Conflit verbal) : 54 (10.8%)
  - 4 (Conflit matériel) : 58 (11.6%)
- L'échantillon est dominé par la coopération verbale (69.8%). Les conflits représentent 22.4% au total.
- Contrat pipeline : champ entier, 4 valeurs distinctes attendues. Peut servir à colorer les edges du graphe (coopération vs conflit). Aucun null ni valeur hors plage observé.

---

## Condition de construction d'un edge (graphe pays)

Un edge dans le graphe nécessite que Actor1CountryCode ET Actor2CountryCode soient tous les deux non vides.

| Situation | Nb lignes | Proportion |
|-----------|-----------|------------|
| Les deux renseignés (edge possible) | 30 | 6.0% |
| Actor1 seulement renseigné | 71 | 14.2% |
| Actor2 seulement renseigné | 229 | 45.8% |
| Aucun des deux | 170 | 34.0% |

Sur 500 événements, 30 peuvent générer un edge dans le graphe pays (6.0%).

Parmi ces 30 edges potentiels :
- 1 implique un code régional CAMEO (AFR) dans Actor1CountryCode — cet edge ne serait pas géolocalisable sur une carte pays
- 29 edges avec deux codes pays ISO-compatibles

La forte proportion "Actor2 seulement" (45.8%) s'explique par le fait qu'Actor2CountryCode inclut des cas où l'acteur 2 est un État mais l'acteur 1 est un groupe non-étatique (individu, syndicat, entreprise) sans code pays.

Estimation mensuelle : un fichier daily contient 136 855 événements. Sur un mois (~4 millions d'événements), environ 240 000 edges potentiels sont attendus (6% de 4M) avant filtrage des codes régionaux.

---

## Schéma de la table `events` (pipeline)

Table construite à partir du CSV brut GDELT après filtrage et calcul des colonnes dérivées. 16 colonnes.

| # | Colonne | Type | Source | Description |
|---|---------|------|--------|-------------|
| 1 | GLOBALEVENTID | str | brut | Identifiant unique de l'événement |
| 2 | SQLDATE | str | brut | Date de l'événement, format YYYYMMDD (lu en str) |
| 3 | Actor1CountryCode | str \| null | brut | Code pays CAMEO acteur 1 — null si absent |
| 4 | Actor2CountryCode | str \| null | brut | Code pays CAMEO acteur 2 — null si absent |
| 5 | Actor1Name | str \| null | brut | Nom acteur 1 — null si absent |
| 6 | Actor2Name | str \| null | brut | Nom acteur 2 — null si absent |
| 7 | Actor1Type1Code | str \| null | brut | Code type principal acteur 1 (GOV, BUS, MIL, LAB, CVL, COP…) |
| 8 | Actor2Type1Code | str \| null | brut | Code type principal acteur 2 (mêmes valeurs) |
| 9 | EventCode | str | brut | Code CAMEO événement — lu en str (zéros de tête significatifs) |
| 10 | QuadClass | int64 | brut | 1=Coop verbale, 2=Coop mat., 3=Conflit verbal, 4=Conflit mat. |
| 11 | GoldsteinScale | float64 | brut | Score relationnel -10 à +10 |
| 12 | NumMentions | int64 | brut | Nombre de mentions — utilisé comme poids (log1p) |
| 13 | AvgTone | float64 | brut | Ton NLP moyen des articles sources |
| 14 | is_internal | bool | dérivé | Voir définition ci-dessous |
| 15 | edge_type | str | dérivé | "strict" ou "extended" — voir définition ci-dessous |
| 16 | goldstein_category | str | dérivé | "positif", "negatif" ou "neutre" — voir définition ci-dessous |

### Règle d'exclusion

Sont exclues de la table `events` uniquement les lignes où **les quatre champs suivants sont simultanément nuls** :

- `Actor1CountryCode` est null
- `Actor2CountryCode` est null
- `Actor1Name` est null
- `Actor2Name` est null

Ces lignes ne contiennent aucune information d'acteur utilisable. Toute ligne ayant au moins un de ces quatre champs renseigné est conservée.

### Définition des colonnes dérivées

**`is_internal` (bool)**

Classifie les événements probablement internes à un pays :

| Valeur | Condition | Interprétation |
|--------|-----------|----------------|
| `True` | `Actor1CountryCode IS NULL AND Actor2CountryCode IS NOT NULL` | Acteur 1 non identifié comme État, acteur 2 est un pays — événement probablement interne au pays cible |
| `True` | `Actor1CountryCode IS NOT NULL AND Actor2CountryCode IS NOT NULL AND Actor1CountryCode == Actor2CountryCode` | Même pays des deux côtés |
| `False` | Tous les autres cas | — |

Note : `IS NULL` correspond aux chaînes vides du CSV brut, converties en null Polars via `null_values=[""]`.

**`edge_type` (str)**

| Valeur | Condition |
|--------|-----------|
| `"strict"` | Actor1CountryCode non null ET non régional CAMEO, ET Actor2CountryCode non null ET non régional CAMEO |
| `"extended"` | Tous les autres cas (code manquant ou code régional CAMEO) |

Codes régionaux CAMEO exclus du type "strict" : AFR, ASA, ASM, BLK, CAF, CAS, CAU, CEU, CFR, EAF, EEU, EUR, LAM, MEA, NAF, NMR, SAF, SAM, SAS, SEA, WAF, ZAF.

**`goldstein_category` (str)**

| Valeur | Condition |
|--------|-----------|
| `"positif"` | `GoldsteinScale > 0` |
| `"negatif"` | `GoldsteinScale < 0` |
| `"neutre"` | `GoldsteinScale == 0` |

GoldsteinScale = 0 est une catégorie explicite : inclus dans `score_global`, exclu de `score_positif` et `score_negatif`.

---

## Profiling détaillé — champs complémentaires

### Actor1Name
- Remplissage : 33.6% (168/500)
- Valeurs uniques : 47
- Top 10 valeurs :
  - CANADA : 18 (3.6%)
  - UNITED STATES : 17 (3.4%)
  - AUSTRALIA : 12 (2.4%)
  - BUSINESS : 12 (2.4%)
  - INDUSTRY : 8 (1.6%)
  - COMPANIES : 7 (1.4%)
  - COMPANY : 6 (1.2%)
  - AFGHAN : 5 (1.0%)
  - ARGENTINE : 5 (1.0%)
  - MURRAY : 5 (1.0%)
- Observation : les noms peuvent désigner des pays (AUSTRALIA, CANADA), des groupes génériques (BUSINESS, INDUSTRY, GOVERNMENT) ou des personnes (MURRAY)
- Contrat pipeline : utiliser comme label d'annotation uniquement — pas comme clé d'identification. Ne pas utiliser pour déduire le code pays.

### Actor2Name
- Remplissage : 84.4% (422/500)
- Valeurs uniques : 145
- Top 10 valeurs :
  - UNITED STATES : 78 (15.6%)
  - EMPLOYEE : 13 (2.6%)
  - CANADA : 11 (2.2%)
  - GOVERNMENT : 10 (2.0%)
  - COMMUNITY : 9 (1.8%)
  - SCHOOL : 9 (1.8%)
  - POLICE : 9 (1.8%)
  - STUDENT : 8 (1.6%)
  - CHINESE : 7 (1.4%)
  - AUSTRALIA : 6 (1.2%)
- Contrat pipeline : label uniquement — même règle qu'Actor1Name.

### IsRootEvent
- Remplissage : 100%
- Distribution : {1: 332 (66.4%), 0: 168 (33.6%)}
- Contrat pipeline : peut être utilisé pour dédupliquer si nécessaire — décision humaine requise.

### NumSources / NumArticles
- NumSources : min=1, max=159, mean=10.1, P95=63
- NumArticles : min=1, max=1530, mean=68.5, P95=360
- Observation : NumArticles et NumMentions ont des valeurs identiques sur cet échantillon (mêmes min, max, mean) — particularité de l'échantillon ou équivalence dans GDELT 1.0 à confirmer.

### Actor1Type1Code
- Remplissage : 16.4% (82/500)
- Valeurs observées : GOV (gouvernement), BUS (business), MIL (militaire), LAB (syndicats/travail), CVL (civil), COP (police)
- Complément utile à Actor1CountryCode pour distinguer acteur étatique vs non-étatique

---

## Champs secondaires — schéma complet

| # | Champ | Type réel | Remplissage |
|---|-------|-----------|-------------|
| 1 | GLOBALEVENTID | int64 | 100.0% |
| 2 | SQLDATE | int64 | 100.0% |
| 3 | MonthYear | int64 | 100.0% |
| 4 | Year | int64 | 100.0% |
| 5 | FractionDate | float64 | 100.0% |
| 6 | Actor1Code | str | 33.6% |
| 7 | Actor1Name | str | 33.6% |
| 8 | Actor1CountryCode | str | 20.2% |
| 9 | Actor1KnownGroupCode | str | 0.2% |
| 10 | Actor1EthnicCode | float64 (vide) | 0.0% |
| 11 | Actor1Religion1Code | float64 (vide) | 0.0% |
| 12 | Actor1Religion2Code | float64 (vide) | 0.0% |
| 13 | Actor1Type1Code | str | 16.4% |
| 14 | Actor1Type2Code | str | 0.4% |
| 15 | Actor1Type3Code | float64 (vide) | 0.0% |
| 16 | Actor2Code | str | 84.4% |
| 17 | Actor2Name | str | 84.4% |
| 18 | Actor2CountryCode | str | 51.8% |
| 19 | Actor2KnownGroupCode | str | 0.6% |
| 20 | Actor2EthnicCode | str | 0.6% |
| 21 | Actor2Religion1Code | str | 0.4% |
| 22 | Actor2Religion2Code | str | 0.2% |
| 23 | Actor2Type1Code | str | 35.4% |
| 24 | Actor2Type2Code | str | 1.4% |
| 25 | Actor2Type3Code | float64 (vide) | 0.0% |
| 26 | IsRootEvent | int64 | 100.0% |
| 27 | EventCode | str (LIRE EN STR — zéros de tête) | 100.0% |
| 28 | EventBaseCode | str (LIRE EN STR — zéros de tête) | 100.0% |
| 29 | EventRootCode | str (LIRE EN STR — zéros de tête) | 100.0% |
| 30 | QuadClass | int64 | 100.0% |
| 31 | GoldsteinScale | float64 | 100.0% |
| 32 | NumMentions | int64 | 100.0% |
| 33 | NumSources | int64 | 100.0% |
| 34 | NumArticles | int64 | 100.0% |
| 35 | AvgTone | float64 | 100.0% |
| 36 | Actor1Geo_Type | int64 | 100.0% |
| 37 | Actor1Geo_FullName | str | 31.0% |
| 38 | Actor1Geo_CountryCode | str | 31.0% |
| 39 | Actor1Geo_ADM1Code | str | 31.0% |
| 40 | Actor1Geo_Lat | float64 | 31.0% |
| 41 | Actor1Geo_Long | float64 | 31.0% |
| 42 | Actor1Geo_FeatureID | str | 31.0% |
| 43 | Actor2Geo_Type | int64 | 100.0% |
| 44 | Actor2Geo_FullName | str | 77.4% |
| 45 | Actor2Geo_CountryCode | str | 77.8% |
| 46 | Actor2Geo_ADM1Code | str | 77.8% |
| 47 | Actor2Geo_Lat | float64 | 77.4% |
| 48 | Actor2Geo_Long | float64 | 77.4% |
| 49 | Actor2Geo_FeatureID | str | 77.8% |
| 50 | ActionGeo_Type | int64 | 100.0% |
| 51 | ActionGeo_FullName | str | 92.0% |
| 52 | ActionGeo_CountryCode | str | 92.4% |
| 53 | ActionGeo_ADM1Code | str | 92.4% |
| 54 | ActionGeo_Lat | float64 | 92.0% |
| 55 | ActionGeo_Long | float64 | 92.0% |
| 56 | ActionGeo_FeatureID | str | 92.4% |
| 57 | DATEADDED | int64 | 100.0% |
| 58 | SOURCEURL | str | 100.0% |

---

## Règles de validation (observées)

- `Actor1CountryCode` et `Actor2CountryCode` : toujours chaîne vide '' si absent — jamais NaN. Lire en str. Tester avec `!= ''` pour filtrer les vides.
- `EventCode`, `EventBaseCode`, `EventRootCode` : lire obligatoirement en `dtype=str`. Contient des codes à 3 ou 4 caractères avec zéros de tête significatifs. La lecture en int détruit l'information.
- `GoldsteinScale` : float64, plage strictement dans [-10.0 ; +10.0], 0 null sur cet échantillon, 32 valeurs discrètes.
- `AvgTone` : float64, plage effective [-12.5 ; +11.2] sur cet échantillon, 0 null. La plage documentée -100/+100 n'est pas représentative.
- `SQLDATE` et `DATEADDED` : int64, format YYYYMMDD, jamais null. SQLDATE = date de l'événement (peut varier dans un fichier daily). DATEADDED = date du fichier source.
- `NumMentions`, `NumSources`, `NumArticles` : int64, toujours >= 1, jamais null.
- `IsRootEvent` : int64, valeurs strictement 0 ou 1.
- `QuadClass` : int64, valeurs strictement 1, 2, 3 ou 4.
- `SOURCEURL` : str, 100% rempli, longueur 31–222 caractères sur cet échantillon.
- Champs Geo_Type (Actor1Geo_Type, Actor2Geo_Type, ActionGeo_Type) : int64, 100% remplis, valeur 0 si géographie inconnue — ne jamais confondre avec null.
- Champs 100% vides sur cet échantillon (Actor1EthnicCode, Actor1Religion1Code, Actor1Religion2Code, Actor1Type3Code, Actor2Type3Code) : pandas les lit en float64 (NaN). Forcer en str lors du chargement pour ne pas masquer des valeurs présentes dans d'autres fichiers.

---

## Règles de gestion des cas limites

1. **Edges avec code régional CAMEO** : exclure les lignes où Actor1CountryCode ou Actor2CountryCode est un code régional CAMEO (AFR, MEA, EUR, LAM, NMR, SEA, BLK, CAU, ASA, SCA, MDE, WST, EEU, FSU — liste complète dans CAMEO.country.txt). Ces codes ne correspondent pas à un pays géolocalisable sur la carte.

2. **Code PSE (Palestine)** : à traiter comme code pays valide — observable dans les données, correspond à un territoire géolocalisable.

3. **EventCode en int** : toute lecture sans `dtype=str` truncate les zéros de tête. Règle : `pd.read_csv(..., dtype={'EventCode': str, 'EventBaseCode': str, 'EventRootCode': str})`.

4. **NumMentions asymétrique** : 55% des événements ont 10 mentions ou moins, max à 1530. Appliquer log1p(NumMentions) pour la pondération des edges dans la visualisation.

5. **Actor1CountryCode à 79.8% de vides** : la majorité des événements n'ont pas d'acteur 1 étatique identifié. Le graphe pays ne peut être construit que sur la minorité d'événements (6% sur cet échantillon) ayant les deux codes renseignés.

6. **AvgTone et GoldsteinScale : corrélation faible (0.31)** : les deux métriques apportent de l'information complémentaire. Un edge avec GoldsteinScale positif peut avoir un AvgTone négatif.

7. **SQLDATE vs DATEADDED** : dans un fichier daily, SQLDATE peut référencer des événements de dates antérieures. Ne pas supposer SQLDATE == DATEADDED.

8. **Champs Geo_Type = 0 avec Geo_FullName vide** : comportement cohérent — type 0 signifie géographie inconnue. Actor1Geo_Type = 0 pour 69% des lignes.

---

## Décisions débloquées

Questions de `docs/intent.md` résolues par ce profiling :

1. **Quel dataset GDELT utiliser ?** — GDELT 1.0 Events est suffisant pour la phase 1. Il contient les quatre champs nécessaires au graphe pays : Actor1CountryCode, Actor2CountryCode, GoldsteinScale, AvgTone. Les datasets Mentions et GKG ne sont pas requis en phase 1.

2. **Quelle métrique pour la relation positive/négative ?** — GoldsteinScale est recommandé en priorité : 100% de remplissage, plage [-10 ; +10] confirmée, 32 valeurs discrètes stables par type d'événement CAMEO. AvgTone est complémentaire (corrélation 0.31) — apporte la dimension de couverture médiatique. Utiliser GoldsteinScale comme score primaire, AvgTone comme score secondaire facultatif.

3. **Les codes pays GDELT sont-ils ISO 3166 ?** — Majoritairement oui (ISO 3166-1 alpha-3), avec des exceptions : 27 codes régionaux CAMEO custom (liste connue) et quelques codes non-standard (PSE pour Palestine). Sur cet échantillon : 1 code régional (AFR) dans Actor1CountryCode, aucun dans Actor2CountryCode. La grande majorité des codes observés sont compatibles ISO 3166.

4. **Distribution réelle de GoldsteinScale et AvgTone** — Documentée ci-dessus. GoldsteinScale : médiane=1.9, 32 valeurs discrètes dans [-10 ; +10]. AvgTone : médiane=-1.39, plage effective [-12.5 ; +11.2], distribution continue.

5. **Volumétrie sur un mois** — Le fichier du 1er avril 2025 contient 136 855 événements. Estimation mensuelle : environ 4 millions d'événements. Avec 6% d'edges potentiels : environ 240 000 paires pays par mois avant filtrage des codes régionaux.

---

## Décisions encore bloquées — décisions humaines requises

1. **Granularité temporelle du graphe** — L'échantillon couvre 4 dates distinctes sur 500 lignes (non représentatif d'une vraie distribution mensuelle). Mesurer sur un mois complet avant de choisir entre agrégation journalière, hebdomadaire ou mensuelle.

2. **Agrégation de plusieurs événements entre deux pays** — L'échantillon est trop petit pour observer la distribution des doublons de paires (USA-RUS, USA-CAN...). Sur un mois complet : choisir entre moyenne pondérée par NumMentions, médiane, ou somme des GoldsteinScale.

3. **Traitement d'Actor1CountryCode à 20.2% de remplissage** — Le faible remplissage d'Actor1CountryCode (vs 51.8% pour Actor2) limite fortement le graphe (6% d'edges potentiels). Décision humaine : élargir la définition d'edge pour inclure les événements "Actor2 pays connu vs acteur non-étatique" ? Ou conserver la contrainte stricte "deux pays identifiés" ?

4. **Seuil de filtrage sur NumMentions** — Les événements à 1 mention (4.6%) sont légitimes mais peu significatifs pour le graphe. Faut-il filtrer NumMentions < N (N à définir) ?

5. **Package de visualisation réseau + carte** — Non décidé (décision ouverte dans intent.md). Ce profiling ne modifie pas cette décision.

6. **Comportement de GoldsteinScale si EventCode absent** — Non observé sur cet échantillon (EventCode 100% rempli). A vérifier sur un volume complet.

7. **Représentativité de l'échantillon** — Les 500 lignes sont consécutives dans un fichier de 136 855 lignes — ce n'est pas un échantillon aléatoire. Les distributions observées (surreprésentation d'AUS, CAN, USA dans Actor1CountryCode) peuvent ne pas être représentatives de l'ensemble du fichier. Relancer le profiling sur un échantillon stratifié ou sur le fichier complet pour valider.
