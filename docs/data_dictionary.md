# Dictionnaire de données — GDELT 2.0 Events

61 colonnes organisées en 9 sections. Types : `Int64`, `Float64`, `String`.

---

## Identifiants & dates

| Colonne | Type | Description |
|---|---|---|
| `GlobalEventID` | Int64 | Identifiant unique de l'événement dans la base GDELT |
| `Day` | Int64 | Date de l'événement au format `YYYYMMDD` |
| `MonthYear` | Int64 | Mois et année de l'événement au format `YYYYMM` |
| `Year` | Int64 | Année de l'événement |
| `FractionDate` | Float64 | Date décimale (ex. 2024.5 ≈ juillet 2024), utile pour les tris et interpolations |

---

## Acteur 1

| Colonne | Type | Description |
|---|---|---|
| `Actor1Code` | String | Code CAMEO complet de l'acteur 1 (concaténation pays + groupe + type) |
| `Actor1Name` | String | Nom textuel de l'acteur 1 tel qu'extrait de l'article |
| `Actor1CountryCode` | String | Code pays ISO 3166 alpha-3 de l'acteur 1 |
| `Actor1KnownGroupCode` | String | Code du groupe connu auquel appartient l'acteur 1 (ex. `NATO`, `UN`) |
| `Actor1EthnicCode` | String | Code du groupe ethnique de l'acteur 1 (référentiel CAMEO) |
| `Actor1Religion1Code` | String | Code de la religion principale de l'acteur 1 |
| `Actor1Religion2Code` | String | Code de la religion secondaire de l'acteur 1 |
| `Actor1Type1Code` | String | Code du type primaire de l'acteur 1 (ex. `GOV`, `MIL`, `OPP`) |
| `Actor1Type2Code` | String | Code du type secondaire de l'acteur 1 |
| `Actor1Type3Code` | String | Code du type tertiaire de l'acteur 1 |

---

## Acteur 2

| Colonne | Type | Description |
|---|---|---|
| `Actor2Code` | String | Code CAMEO complet de l'acteur 2 |
| `Actor2Name` | String | Nom textuel de l'acteur 2 tel qu'extrait de l'article |
| `Actor2CountryCode` | String | Code pays ISO 3166 alpha-3 de l'acteur 2 |
| `Actor2KnownGroupCode` | String | Code du groupe connu auquel appartient l'acteur 2 |
| `Actor2EthnicCode` | String | Code du groupe ethnique de l'acteur 2 |
| `Actor2Religion1Code` | String | Code de la religion principale de l'acteur 2 |
| `Actor2Religion2Code` | String | Code de la religion secondaire de l'acteur 2 |
| `Actor2Type1Code` | String | Code du type primaire de l'acteur 2 |
| `Actor2Type2Code` | String | Code du type secondaire de l'acteur 2 |
| `Actor2Type3Code` | String | Code du type tertiaire de l'acteur 2 |

---

## Classification CAMEO

| Colonne | Type | Description |
|---|---|---|
| `IsRootEvent` | Int64 | `1` si cet événement est l'événement racine du cluster, `0` sinon |
| `EventCode` | String | Code CAMEO complet de l'événement (jusqu'à 4 chiffres, ex. `0311`) |
| `EventBaseCode` | String | Code CAMEO à 3 chiffres, sous-catégorie d'action |
| `EventRootCode` | String | Code CAMEO racine à 2 chiffres, grande catégorie d'action (ex. `03` = Exprimer une intention de coopérer) |
| `QuadClass` | Int64 | Classe quadratique : `1` = coopération verbale, `2` = coopération matérielle, `3` = conflit verbal, `4` = conflit matériel |

---

## Métriques

| Colonne | Type | Description |
|---|---|---|
| `GoldsteinScale` | Float64 | Impact théorique de l'événement de `-10` (très conflictuel) à `+10` (très coopératif) |
| `NumMentions` | Int64 | Nombre total de mentions de l'événement dans tous les articles |
| `NumSources` | Int64 | Nombre de sources distinctes ayant mentionné l'événement |
| `NumArticles` | Int64 | Nombre d'articles distincts ayant mentionné l'événement |
| `AvgTone` | Float64 | Ton moyen de la couverture médiatique (valeurs négatives = ton négatif/conflictuel) |

---

## Géolocalisation Acteur 1

| Colonne | Type | Description |
|---|---|---|
| `Actor1Geo_Type` | Int64 | Précision géographique : `0` = inconnu, `1` = pays, `2` = région admin, `3` = ville, `4` = point précis |
| `Actor1Geo_FullName` | String | Nom complet du lieu associé à l'acteur 1 |
| `Actor1Geo_CountryCode` | String | Code pays FIPS 10-4 du lieu de l'acteur 1 |
| `Actor1Geo_ADM1Code` | String | Code de la division administrative de niveau 1 (région/état) |
| `Actor1Geo_ADM2Code` | String | Code de la division administrative de niveau 2 (département/comté) |
| `Actor1Geo_Lat` | Float64 | Latitude en degrés décimaux du lieu de l'acteur 1 |
| `Actor1Geo_Long` | Float64 | Longitude en degrés décimaux du lieu de l'acteur 1 |
| `Actor1Geo_FeatureID` | String | Identifiant GeoNames ou GNIS du lieu de l'acteur 1 |

---

## Géolocalisation Acteur 2

| Colonne | Type | Description |
|---|---|---|
| `Actor2Geo_Type` | Int64 | Précision géographique : `0` = inconnu, `1` = pays, `2` = région admin, `3` = ville, `4` = point précis |
| `Actor2Geo_FullName` | String | Nom complet du lieu associé à l'acteur 2 |
| `Actor2Geo_CountryCode` | String | Code pays FIPS 10-4 du lieu de l'acteur 2 |
| `Actor2Geo_ADM1Code` | String | Code de la division administrative de niveau 1 |
| `Actor2Geo_ADM2Code` | String | Code de la division administrative de niveau 2 |
| `Actor2Geo_Lat` | Float64 | Latitude en degrés décimaux du lieu de l'acteur 2 |
| `Actor2Geo_Long` | Float64 | Longitude en degrés décimaux du lieu de l'acteur 2 |
| `Actor2Geo_FeatureID` | String | Identifiant GeoNames ou GNIS du lieu de l'acteur 2 |

---

## Géolocalisation Action

| Colonne | Type | Description |
|---|---|---|
| `ActionGeo_Type` | Int64 | Précision géographique du lieu de l'action : `0` = inconnu, `1` = pays, `2` = région admin, `3` = ville, `4` = point précis |
| `ActionGeo_FullName` | String | Nom complet du lieu où l'action s'est produite |
| `ActionGeo_CountryCode` | String | Code pays FIPS 10-4 du lieu de l'action |
| `ActionGeo_ADM1Code` | String | Code de la division administrative de niveau 1 du lieu de l'action |
| `ActionGeo_ADM2Code` | String | Code de la division administrative de niveau 2 du lieu de l'action |
| `ActionGeo_Lat` | Float64 | Latitude en degrés décimaux du lieu de l'action |
| `ActionGeo_Long` | Float64 | Longitude en degrés décimaux du lieu de l'action |
| `ActionGeo_FeatureID` | String | Identifiant GeoNames ou GNIS du lieu de l'action |

---

## Source

| Colonne | Type | Description |
|---|---|---|
| `DATEADDED` | Int64 | Timestamp d'ajout dans GDELT au format `YYYYMMDDHHmmSS` |
| `SOURCEURL` | String | URL de l'article source ayant déclenché l'enregistrement de l'événement |
