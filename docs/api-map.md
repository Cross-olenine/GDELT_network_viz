# API Map — GDELT (Global Database of Events, Language, and Tone)
Généré le : 2026-05-14
Source : https://www.gdeltproject.org/data.html

---

## Vue d'ensemble

GDELT expose ses données exclusivement sous forme de fichiers CSV compressés
en téléchargement bulk. Il n'existe pas d'API REST au sens classique du terme.
L'accès se fait via téléchargement direct de fichiers ZIP depuis des serveurs HTTP
statiques, ou via Google BigQuery (tables publiques mises à jour en temps réel).

Deux versions coexistent :
- **GDELT 1.0** : couverture 1979–présent, mise à jour quotidienne, 2 datasets
  (Events + GKG)
- **GDELT 2.0** : couverture 2015–présent, mise à jour toutes les 15 minutes,
  3 datasets (Events, Mentions, GKG v2.1) avec couverture multilingue (65 langues)

Pour un pipeline CSV -> DuckDB, les fichiers bulk daily (v1) ou les fichiers
15 minutes listés dans le master file list (v2) sont les deux points d'entrée.

---

## Authentification

Aucune authentification requise. Accès libre et gratuit en HTTP direct.

- Pas de clé API
- Pas de token
- Pas d'en-tête requis
- Licence : "100% free and open" selon la documentation officielle

⚠️ AMBIGU : La licence exacte (Creative Commons ? domaine public ?) n'est pas
explicitement détaillée sur la page data.html. Termes complets non publiés.

---

## Contraintes globales

### Rate limits
⚠️ NON DOCUMENTÉ : Aucun rate limit mentionné. Les fichiers sont servis en
HTTP statique depuis data.gdeltproject.org. Aucun mécanisme de throttling
documenté.

### Pagination
Sans objet. Les données sont des fichiers plats complets. Chaque fichier ZIP
contient l'intégralité des événements pour la période couverte (jour ou tranche
de 15 minutes). Pas de curseur ni d'offset.

### Encodage
⚠️ AMBIGU : UTF-8 ou ASCII compatible selon le codebook v1. Les champs codés
(country codes, event codes) sont en ASCII pur. Les noms propres (Actor1Name,
Actor2Name) sont translittérés en caractères latins. Présence d'un BOM non
documentée. A valider sur un fichier réel.

### Delimiter
**Tab** (`\t`). Les fichiers ont l'extension `.CSV` mais sont tab-délimités.
Les fichiers de données ne contiennent pas de ligne d'en-tête — les noms de
colonnes sont fournis dans des fichiers lookup séparés.

### Format de date
- **SQLDATE** : int, format YYYYMMDD (ex : 20140125)
- **MonthYear** : char(6), format YYYYMM (ex : 201401)
- **Year** : char(4), format YYYY
- **FractionDate** : double, ex : 2014.0685 (année + fraction décimale du jour)
- **DATEADDED** : int, format YYYYMMDD, date d'ajout dans la base

### Volumétrie
- GDELT 1.0 archive complète (1979–fév. 2014) : 1,1 Go compressé
- GKG 2015 seul : plus de 2,5 To (non compressé)
- GDELT 2.0 : plusieurs Mo par fichier ZIP de 15 minutes
- Couverture totale annoncée : plus de 215 ans de données

### Certificat TLS
⚠️ AMBIGU : Le sous-domaine data.gdeltproject.org retourne
ERR_TLS_CERT_ALTNAME_INVALID en HTTPS. Les téléchargements peuvent nécessiter
de passer en HTTP non-sécurisé ou de désactiver la vérification SSL côté client.
A confirmer via le connection-tester.

---

## Datasets / Endpoints

---

### GDELT 1.0 Events — Daily Updates (avril 2013–présent)

- **Accès** : `http://data.gdeltproject.org/events/YYYYMMDD.export.CSV.zip`
  - Exemple : `http://data.gdeltproject.org/events/20130523.export.CSV.zip`
  - Mis en ligne avant 6h00 EST chaque matin, 7 jours/7
- **Index complet** : `http://data.gdeltproject.org/events/index.html`
- **Méthode** : GET HTTP direct (téléchargement fichier)
- **Compression** : ZIP
- **Fréquence de mise à jour** : Quotidienne
- **Format de réponse** : CSV tab-délimité, sans en-tête, 58 colonnes
- **En-têtes colonnes** : `https://www.gdeltproject.org/data/lookups/CSV.header.dailyupdates.txt`

#### Schéma complet — 58 colonnes

| # | Nom | Type SQL | Notes |
|---|-----|----------|-------|
| 1 | GLOBALEVENTID | bigint | Identifiant unique global de l'événement |
| 2 | SQLDATE | int | Date événement, format YYYYMMDD |
| 3 | MonthYear | char(6) | Mois-année, format YYYYMM |
| 4 | Year | char(4) | Année, format YYYY |
| 5 | FractionDate | double | Date décimale (ex : 2014.0685) |
| 6 | Actor1Code | char(3) | Code CAMEO complet acteur 1 |
| 7 | Actor1Name | char(255) | Nom acteur 1, texte libre translittéré |
| 8 | Actor1CountryCode | char(3) | Code pays CAMEO acteur 1 — voir detail ci-dessous |
| 9 | Actor1KnownGroupCode | char(3) | Code groupe connu acteur 1 |
| 10 | Actor1EthnicCode | char(3) | Code ethnique acteur 1 |
| 11 | Actor1Religion1Code | char(3) | Code religion principale acteur 1 |
| 12 | Actor1Religion2Code | char(3) | Code religion secondaire acteur 1 |
| 13 | Actor1Type1Code | char(3) | Code type principal acteur 1 |
| 14 | Actor1Type2Code | char(3) | Code type secondaire acteur 1 |
| 15 | Actor1Type3Code | char(3) | Code type tertiaire acteur 1 |
| 16 | Actor2Code | char(3) | Code CAMEO complet acteur 2 |
| 17 | Actor2Name | char(255) | Nom acteur 2, texte libre translittéré |
| 18 | Actor2CountryCode | char(3) | Code pays CAMEO acteur 2 — voir detail ci-dessous |
| 19 | Actor2KnownGroupCode | char(3) | Code groupe connu acteur 2 |
| 20 | Actor2EthnicCode | char(3) | Code ethnique acteur 2 |
| 21 | Actor2Religion1Code | char(3) | Code religion principale acteur 2 |
| 22 | Actor2Religion2Code | char(3) | Code religion secondaire acteur 2 |
| 23 | Actor2Type1Code | char(3) | Code type principal acteur 2 |
| 24 | Actor2Type2Code | char(3) | Code type secondaire acteur 2 |
| 25 | Actor2Type3Code | char(3) | Code type tertiaire acteur 2 |
| 26 | IsRootEvent | int | 1 si événement racine, 0 sinon |
| 27 | EventCode | char(4) | Code CAMEO de l'événement (max 4 chiffres) |
| 28 | EventBaseCode | char(4) | Code CAMEO niveau 2 |
| 29 | EventRootCode | char(4) | Code CAMEO niveau 1 (racine) |
| 30 | QuadClass | int | 1=Coop verbale, 2=Coop matérielle, 3=Conflit verbal, 4=Conflit matériel |
| 31 | GoldsteinScale | double | Score Goldstein — voir detail ci-dessous |
| 32 | NumMentions | int | Nombre total de mentions de l'événement |
| 33 | NumSources | int | Nombre de domaines sources distincts |
| 34 | NumArticles | int | Nombre d'articles distincts |
| 35 | AvgTone | double | Ton émotionnel moyen des articles sources — voir detail ci-dessous |
| 36 | Actor1Geo_Type | int | 0=inconnu, 1=pays, 2=US état, 3=US ville, 4=monde ville, 5=lac/rivière |
| 37 | Actor1Geo_FullName | char(255) | Nom géographique complet acteur 1 |
| 38 | Actor1Geo_CountryCode | char(2) | Code pays FIPS 10-4 acteur 1 (2 lettres) |
| 39 | Actor1Geo_ADM1Code | char(4) | Code région administrative niveau 1 acteur 1 |
| 40 | Actor1Geo_Lat | float | Latitude acteur 1 |
| 41 | Actor1Geo_Long | float | Longitude acteur 1 |
| 42 | Actor1Geo_FeatureID | int | Identifiant GNS/GNIS feature géo acteur 1 |
| 43 | Actor2Geo_Type | int | Mêmes valeurs que Actor1Geo_Type |
| 44 | Actor2Geo_FullName | char(255) | Nom géographique complet acteur 2 |
| 45 | Actor2Geo_CountryCode | char(2) | Code pays FIPS 10-4 acteur 2 (2 lettres) |
| 46 | Actor2Geo_ADM1Code | char(4) | Code région administrative niveau 1 acteur 2 |
| 47 | Actor2Geo_Lat | float | Latitude acteur 2 |
| 48 | Actor2Geo_Long | float | Longitude acteur 2 |
| 49 | Actor2Geo_FeatureID | int | Identifiant GNS/GNIS feature géo acteur 2 |
| 50 | ActionGeo_Type | int | Mêmes valeurs que Actor1Geo_Type |
| 51 | ActionGeo_FullName | char(255) | Nom géographique complet de l'action |
| 52 | ActionGeo_CountryCode | char(2) | Code pays FIPS 10-4 de l'action (2 lettres) |
| 53 | ActionGeo_ADM1Code | char(4) | Code région administrative niveau 1 de l'action |
| 54 | ActionGeo_Lat | float | Latitude de l'action |
| 55 | ActionGeo_Long | float | Longitude de l'action |
| 56 | ActionGeo_FeatureID | int | Identifiant GNS/GNIS feature géo action |
| 57 | DATEADDED | int | Date d'ajout dans la base, format YYYYMMDD |
| 58 | SOURCEURL | char(255) | URL de l'article source principal |

---

### GDELT 1.0 Events — Historique (1979–mars 2013)

- **Accès** : `http://data.gdeltproject.org/events/index.html` (lister les fichiers)
- **Format des fichiers** : mensuel ou annuel selon la période
- **Différence vs daily** : 57 colonnes (sans SOURCEURL en position 58)
- **En-têtes colonnes** : `https://www.gdeltproject.org/data/lookups/CSV.header.historical.txt`
- **Contraintes spécifiques** : Archives statiques, non mises à jour

---

### Détail des champs prioritaires pour le pipeline

#### Actor1CountryCode / Actor2CountryCode (colonnes 8 et 18)
- **Type** : char(3), chaîne vide si non renseigné (pas de NULL SQL)
- **Format** : Système CAMEO hybride — 276 codes au total :
  - 249 codes pays : majoritairement ISO 3166-1 alpha-3 (USA, GBR, FRA, CHN,
    RUS, DEU...) avec quelques codes non-standard ou dépréciés (TMP pour
    Timor-Est, PSE pour Palestine occupée)
  - 27 codes régionaux custom non-ISO : AFR (Afrique), MEA (Moyen-Orient),
    EUR (Europe), LAM (Amérique latine), NMR (Amérique du Nord), SEA
    (Asie du Sud-Est), BLK (Balkans), CAU (Caucase), etc.
- **Semantique** : Encode l'acteur politique, pas sa localisation géographique.
  Un acteur peut être une ONG, un individu, ou un groupe transnational — dans
  ce cas le champ est vide.
- **Distinction critique** : Ne pas confondre avec Actor1Geo_CountryCode
  (colonne 38), qui est le code FIPS 2 lettres de la localisation géographique.
- **Référence** : `https://www.gdeltproject.org/data/lookups/CAMEO.country.txt`
- **Exemple confirmé par la documentation officielle** : 'EGY' = Egypte,
  'USA' = États-Unis
- **Nulls** : Champ vide fréquent quand l'acteur n'est pas un Etat.
  ⚠️ NON DOCUMENTÉ : taux de remplissage exact inconnu.

#### Actor1Name / Actor2Name (colonnes 7 et 17)
- **Type** : char(255), peut être vide
- **Format** : Texte libre, majuscules, translittéré en caractères latins ASCII
- **Exemples** : "UNITED STATES", "BARACK OBAMA", "HAMAS", "FRENCH POLICE"
- **Nulls** : Possible si acteur non identifié

#### GoldsteinScale (colonne 31)
- **Type** : double
- **Plage** : -10.0 à +10.0 (confirmé par CAMEO.goldsteinscale.txt)
- **Resolution** : 1 décimale (ex : -10.0, -9.5, +4.0, +2.8)
- **Signification** :
  - +10.0 : événement le plus coopératif (ex : accord de paix formel)
  - 0.0 : neutre
  - -10.0 : événement le plus conflictuel (ex : embargo, assaut militaire)
- **Derivation** : Valeur assignée statiquement par type d'événement CAMEO.
  Pas un calcul NLP sur le texte. Lookup fixe :
  `https://www.gdeltproject.org/data/lookups/CAMEO.goldsteinscale.txt`
- **Nulls** : ⚠️ NON DOCUMENTÉ — comportement si EventCode est absent.

#### AvgTone (colonne 35)
- **Type** : double
- **Plage** : ⚠️ AMBIGU — plage théorique -100 à +100 mentionnée dans le
  codebook v1. En pratique les valeurs observées sont dans une fourchette
  beaucoup plus étroite (estimée -20 / +20 selon analyses publiées). A
  mesurer sur données réelles via field-profiler.
- **Signification** : Moyenne du score de ton calculé par GDELT NLP sur
  l'ensemble des articles couvrant l'événement. Valeur négative = couverture
  négative, positive = couverture positive.
- **Différence avec GoldsteinScale** : GoldsteinScale = valeur fixe par type
  d'événement ; AvgTone = calcul dynamique sur contenu textuel, varie selon
  les sources et le contexte éditorial.
- **Nulls** : ⚠️ NON DOCUMENTÉ — comportement si aucun article disponible.

#### SQLDATE (colonne 2)
- **Type** : int(11)
- **Format** : YYYYMMDD (ex : 20140125 = 25 janvier 2014)
- **Signification** : Date de l'événement (pas la date de publication de l'article)
- **Nulls** : Non attendus — champ obligatoire

#### NumMentions (colonne 32)
- **Type** : int(11), entier positif >= 1
- **Signification** : Nombre total de mentions de l'événement dans tous les articles.
  Peut dépasser NumArticles si un article mentionne l'événement plusieurs fois.

#### NumSources (colonne 33)
- **Type** : int(11), entier positif >= 1
- **Signification** : Nombre de domaines sources distincts ayant couvert l'événement

#### NumArticles (colonne 34)
- **Type** : int(11), entier positif >= 1
- **Signification** : Nombre d'articles distincts ayant couvert l'événement

---

### GDELT 1.0 — GKG (Global Knowledge Graph)

- **Accès** :
  - Full graph : `http://data.gdeltproject.org/gkg/YYYYMMDD.gkg.csv.zip`
  - Counts file : `http://data.gdeltproject.org/gkg/YYYYMMDD.gkgcounts.csv.zip`
  - Index : `http://data.gdeltproject.org/gkg/index.html`
- **Méthode** : GET HTTP direct
- **Compression** : ZIP
- **Fréquence** : Quotidienne, mis en ligne avant 6h00 EST
- **Format** : CSV tab-délimité, sans en-tête

**Schéma GKG v1 :** ⚠️ NON DOCUMENTÉ — Le PDF codebook
(GDELT-Global_Knowledge_Graph_Codebook.pdf, 352 Ko) est accessible à
`https://www.gdeltproject.org/data/documentation/GDELT-Global_Knowledge_Graph_Codebook.pdf`
mais son contenu textuel n'a pas pu être extrait automatiquement (flux PDF
compressé non décodable par fetch). Lecture manuelle du PDF requise.

**Champ TONE dans GKG v1 :** ⚠️ NON DOCUMENTÉ dans les sources accessibles.

---

### GDELT 2.0 — Events

- **Master file list** : `http://data.gdeltproject.org/gdeltv2/masterfilelist.txt`
- **Version traduite** : `http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt`
- **Dernière tranche (15 min)** : `http://data.gdeltproject.org/gdeltv2/lastupdate.txt`
- **Traduit dernière tranche** : `http://data.gdeltproject.org/gdeltv2/lastupdate-translation.txt`
- **Format nom de fichier** : `YYYYMMDDHHMMSS.export.CSV.zip` (timestamp UTC)
  - Exemple : `20230615143000.export.CSV.zip`
- **Méthode** : GET HTTP direct sur les URLs listées dans le master file list
- **Compression** : ZIP
- **Fréquence** : Toutes les 15 minutes, 24h/24
- **Format** : CSV tab-délimité, sans en-tête
- **BigQuery** : `gdelt-bq:gdeltv2.events`

**Colonnes GDELT 2.0 Events vs 1.0 :** ⚠️ NON DOCUMENTÉ dans les sources
web accessibles. Le codebook PDF v2.0 (GDELT-Event_Codebook-V2.0.pdf) retourne
404 sur gdeltproject.org et data.gdeltproject.org. Les colonnes additionnelles
sont mentionnées par la documentation mais non listées. Lecture directe du PDF
via navigateur recommandée, ou inspection d'un fichier réel via connection-tester.

---

### GDELT 2.0 — Mentions

- **Format nom de fichier** : `YYYYMMDDHHMMSS.mentions.CSV.zip`
- **Accès** : Via master file list (même URL que Events)
- **Fréquence** : Toutes les 15 minutes
- **Format** : CSV tab-délimité, sans en-tête
- **BigQuery** : `gdelt-bq:gdeltv2.eventmentions`
- **Description** : Chaque ligne représente une mention d'un événement dans un
  article distinct. Permet de suivre l'évolution temporelle de la couverture
  d'un événement.
- **Schéma** : ⚠️ NON DOCUMENTÉ dans les sources accessibles.

---

### GDELT 2.0 — GKG v2.1

- **Format nom de fichier** : `YYYYMMDDHHMMSS.gkg.csv.zip`
- **Accès** : Via master file list (même URL que Events)
- **Fréquence** : Toutes les 15 minutes
- **Format** : CSV tab-délimité, sans en-tête
- **BigQuery** : `gdelt-bq:gdeltv2.gkg`

**Champ TONE dans GKG v2.1 :** ⚠️ AMBIGU — Le codebook PDF v2.1
(GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf) retourne 404. Selon la
littérature secondaire, TONE est une chaîne de valeurs séparées par des
points-virgules comprenant plusieurs composantes (ton positif, ton négatif,
polarité, activité de référence, auto-référence, ton dynamique). Format exact
et plages à valider sur un fichier réel.

**Schéma GKG v2.1 complet :** ⚠️ NON DOCUMENTÉ dans les sources accessibles.

---

## Fichiers de référence (lookups)

Base URL : `https://www.gdeltproject.org/data/lookups/`

| Fichier | Taille | Contenu |
|---------|--------|---------|
| CSV.header.historical.txt | 883 o | En-têtes 57 colonnes fichiers historiques |
| CSV.header.dailyupdates.txt | 893 o | En-têtes 58 colonnes daily updates |
| CSV.header.fieldids.xlsx | 12 Ko | Identifiants de champs (format Excel) |
| CAMEO.country.txt | 4,0 Ko | 276 codes pays/régions CAMEO 3 lettres |
| CAMEO.eventcodes.txt | 12 Ko | Codes événements CAMEO avec descriptions |
| CAMEO.goldsteinscale.txt | 3,1 Ko | Mapping code CAMEO -> valeur GoldsteinScale |
| CAMEO.ethnic.txt | 8,3 Ko | Codes ethniques CAMEO |
| CAMEO.knowngroup.txt | 4,1 Ko | Codes groupes connus CAMEO |
| CAMEO.type.txt | 818 o | Codes types d'acteurs CAMEO |
| CAMEO.religion.txt | 515 o | Codes religions CAMEO |
| FIPS.country.txt | 4,2 Ko | Codes FIPS 10-4 deux lettres (pour champs Geo_CountryCode) |
| SQL.tablecreate.txt | 3,5 Ko | CREATE TABLE MySQL complet pour les deux tables |
| SQL.samplequeryexport.txt | 441 o | Exemple de requête export SELECT INTO OUTFILE |
| SQL.loaddata.txt | 417 o | Script MySQL LOAD DATA INFILE |
| PERL.dailydownloader.txt | 328 o | Script Perl de téléchargement quotidien automatique |

Documentation PDF (dans `/data/documentation/`) :
- `CAMEO.Manual.1.1b3.pdf` (773 Ko) — Manuel complet du système CAMEO
- `GDELT-Data_Format_Codebook.pdf` (309 Ko) — Codebook GDELT 1.0 Events
- `GDELT-Global_Knowledge_Graph_Codebook.pdf` (352 Ko) — Codebook GKG v1
- `GDELT-Global_Knowledge_Graph_MakeMasterGraphSampleScript.pdf` (284 Ko)
- `GDELT-Global_Knowledge_Graph_CategoryList.xlsx` (20 Ko)
- `ISA.2013.GDELT.pdf` (16 Mo) — Article académique introductif

---

## Zones d'incertitude

Liste consolidée de toutes les zones à résoudre manuellement ou via
connection-tester / field-profiler :

1. **Licence exacte** : Termes d'utilisation non explicitement publiés. "100%
   free and open" est la seule mention disponible. A confirmer avant usage
   commercial ou redistribution.

2. **Certificat TLS data.gdeltproject.org** : ERR_TLS_CERT_ALTNAME_INVALID
   en HTTPS. Téléchargements en HTTP non-sécurisé possiblement nécessaire, ou
   contournement de la vérification SSL. A tester via connection-tester.

3. **AvgTone — plage réelle** : Plage théorique -100/+100 documentée mais
   probablement non représentative des valeurs réelles. A mesurer sur un
   échantillon via field-profiler (min, max, percentiles).

4. **GoldsteinScale — comportement sur nulls** : Comportement si EventCode
   absent non documenté. Valeur vide, 0.0, ou NULL réel ? A vérifier sur
   les données réelles.

5. **Actor1/2CountryCode — taux de remplissage** : Proportion d'événements
   avec code pays non vide inconnue. Critique pour évaluer la densité du réseau
   pays. A mesurer via field-profiler.

6. **GDELT 2.0 Events — colonnes supplémentaires** : Codebook PDF v2.0
   inaccessible automatiquement (404 sur gdeltproject.org et
   data.gdeltproject.org). Colonnes additionnelles vs v1.0 non documentées.
   Accès manuel au PDF requis, ou inspection d'un fichier réel.

7. **GKG v1 — schéma complet** : PDF codebook non extractible automatiquement.
   Lecture manuelle du PDF `GDELT-Global_Knowledge_Graph_Codebook.pdf` requise
   pour obtenir la liste des colonnes et le format du champ TONE.

8. **GKG v2.1 — schéma complet et format TONE** : PDF codebook v2.1 retourne
   404 sur gdeltproject.org. Format exact du champ TONE (separateur, ordre
   des sous-composantes, plages de valeurs) a extraire depuis un fichier réel
   ou via BigQuery.

9. **Mentions v2.0 — schéma** : Aucune source accessible ne documente les
   colonnes de la table Mentions. A extraire depuis BigQuery ou un fichier réel
   via connection-tester.

10. **Encodage exact** : UTF-8 vs ASCII non confirmé formellement. Presence
    d'un BOM non documentée. A valider sur un fichier réel (ex : tester
    Actor1Name sur des événements impliquant des pays avec caractères non-latins).
