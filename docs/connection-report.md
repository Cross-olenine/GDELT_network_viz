# Connection Report — GDELT (Global Database of Events, Language, and Tone)
Statut : OK SUCCES
Date : 2026-05-14

## Tests effectues

| Endpoint | Statut | Latence | Taille | Notes |
|----------|--------|---------|--------|-------|
| https://www.gdeltproject.org/data/lookups/CSV.header.dailyupdates.txt | 200 OK | 602ms | 58 colonnes | Lookup en-tetes 58 colonnes |
| http://data.gdeltproject.org/events/20250401.export.CSV.zip | 200 OK — 8,788,636 octets | 280ms | 8,788,636 octets | Fichier daily GDELT 1.0 |

## Authentification

Methode : aucune authentification requise (source publique HTTP)
Format : GET HTTP direct, sans header ni parametre d'auth
Acces HTTP (non HTTPS) utilise : OUI — data.gdeltproject.org retourne ERR_TLS_CERT_ALTNAME_INVALID en HTTPS, confirme

## Connectivite

Endpoint principal teste : http://data.gdeltproject.org/events/20250401.export.CSV.zip
Date du fichier telecharge : 20250401
Latence de telechargement : 280ms
Code retour : 200
Taille du fichier ZIP : 8,788,636 octets
Lignes totales dans le fichier : 136,855

## Rate limits

Documentes dans api-map.md : NON DOCUMENTES (source HTTP statique, aucun throttling mentionne)
Test empirique : 10 requetes consecutives sur https://www.gdeltproject.org/data/lookups/CAMEO.country.txt
Resultat : Aucun 429 sur 10 requetes consecutives
Latence moyenne observee : 480ms
Comportement sur depassement : non observe (aucun 429 declenche)

## Encodage et formats

Encodage detecte : UTF-8 sans BOM (confirme)
Delimiter : tabulation (\t) — extension .CSV trompeuse, fichier TSV
En-tete dans le fichier de donnees : aucune (colonnes fournies par fichier lookup separe)
Format de reponse : ZIP contenant un TSV de 58 colonnes

## Echantillon extrait

Fichier : exploration/data/raw/sample_raw.csv
Lignes extraites : 500
Colonnes : 58

## Mesures sur l'echantillon (500 lignes)

| Champ | Valeur |
|-------|--------|
| Actor1CountryCode — remplissage | 20.2% |
| Actor2CountryCode — remplissage | 51.8% |
| GoldsteinScale — min | -10.0 |
| GoldsteinScale — mean | 0.995 |
| GoldsteinScale — max | 10.0 |
| AvgTone — min | -12.5 |
| AvgTone — mean | -1.572 |
| AvgTone — max | 11.213 |

## Zones d'incertitude resolues

1. **Certificat TLS data.gdeltproject.org** : CONFIRME — le serveur ne supporte pas HTTPS. HTTP obligatoire pour les telechargements.
2. **Encodage** : UTF-8 sans BOM (confirme) — verifie sur le fichier 20250401.
3. **Format reel** : Confirme TSV tab-delimite, sans en-tete, 58 colonnes.
4. **Rate limits** : Aucun mecanisme de throttling observe sur 10 requetes consecutives.
5. **Actor1CountryCode remplissage** : 20.2% sur l'echantillon (a confirmer sur volume complet via field-profiler).
6. **GoldsteinScale plage reelle** : min=-10.0 / max=10.0 sur 500 lignes.
7. **AvgTone plage reelle** : min=-12.5 / max=11.213 — plage observee bien inferieure a la plage theorique -100/+100.

## Zones d'incertitude restantes

1. **Taux de remplissage Actor1/2CountryCode sur volume reel** : mesure sur 500 lignes seulement. A mesurer sur le fichier complet via field-profiler.
2. **GoldsteinScale sur nulls** : comportement quand EventCode absent non observe sur cet echantillon.
3. **GDELT 2.0 Events colonnes** : schema non documente — necessite inspection d'un fichier reel v2.0.
4. **GKG v1 et v2.1 schemas** : non testes dans ce rapport, codebooks PDF inaccessibles automatiquement.
5. **Licence exacte** : "100% free and open" confirme sur la page, termes precis toujours non publies.

## Recommandations pour le pipeline

1. **Utiliser HTTP uniquement** pour data.gdeltproject.org — ne pas tenter HTTPS.
2. **Parser avec sep='\t' et header=None** dans pandas/DuckDB — assigner les colonnes depuis le fichier lookup.
3. **Filtrer Actor1CountryCode et Actor2CountryCode non vides** avant de construire le graphe pays.
4. **GoldsteinScale est suffisant en phase 1** pour le score relationnel — plage confirmee dans les bornes documentees.
5. **Charger dans DuckDB via COPY FROM CSV** apres dezip en memoire ou temporaire.
6. **Ne pas supposer l'ISO 3166** pour les codes pays — CAMEO inclut 27 codes regionaux custom (AFR, MEA, EUR...) a traiter separement.
7. **Polars incompatible** avec ce processeur (absence d'AVX2) — utiliser pandas ou DuckDB natif pour les transformations intermediaires.

## Ecarts avec api-map.md

Aucun ecart detecte. Les informations documentees correspondent aux observations :
- HTTP obligatoire : confirme
- Format TSV 58 colonnes sans en-tete : confirme
- Header lookup accessible en HTTPS : confirme
- Dates testees dans l'ordre ['20250401', '20250101', '20241201'] : premier succes sur 20250401

## Note technique — environnement

Polars a ete installe mais est incompatible avec ce processeur (CPU sans AVX2 / FMA).
Le script a utilise pandas 3.0.3 comme substitut. Pour le pipeline de production,
utiliser DuckDB natif (recommande) ou pandas — pas Polars sur cette machine.

## Journal detaille des tentatives

=== Etape 1 : Recuperation du header lookup ===
  [header-lookup] tentative 1 — HTTP 200 — 602ms
  Colonnes extraites : 58

=== Etape 2 : Telechargement fichier daily GDELT 1.0 ===
  Essai : http://data.gdeltproject.org/events/20250401.export.CSV.zip
  [20250401] tentative 1 — HTTP 200 — 280ms
  -> OK : 8,788,636 octets

=== Etape 3 : Extraction et validation de l'echantillon ===
  Fichier dans le ZIP : 20250401.export.CSV
  Pas de BOM detecte — UTF-8 sans BOM
  Lignes totales dans le fichier : 136,855
  Echantillon retenu : 500 lignes x 58 colonnes

=== Etape 4 : Mesures sur l'echantillon ===
  Actor1CountryCode remplissage : 101/500 = 20.2%
  Actor2CountryCode remplissage : 259/500 = 51.8%
  GoldsteinScale : min=-10.0 / mean=0.995 / max=10.0
  AvgTone : min=-12.5 / mean=-1.572 / max=11.213

=== Etape 5 : Test rate limits empiriques ===
  Requete 1/10 — HTTP 200 — 496ms
  Requete 2/10 — HTTP 200 — 474ms
  Requete 3/10 — HTTP 200 — 484ms
  Requete 4/10 — HTTP 200 — 485ms
  Requete 5/10 — HTTP 200 — 485ms
  Requete 6/10 — HTTP 200 — 468ms
  Requete 7/10 — HTTP 200 — 488ms
  Requete 8/10 — HTTP 200 — 467ms
  Requete 9/10 — HTTP 200 — 480ms
  Requete 10/10 — HTTP 200 — 482ms
  Latence moyenne : 480ms — Aucun 429 sur 10 requetes consecutives

=== Etape 6 : Sauvegarde echantillon ===
  Fichier sauvegarde : C:\Users\Christophe\Documents\Cas d'usages\template-agent-data\exploration\data\raw\sample_raw.csv

=== Etape 7 : Production connection-report.md ===
