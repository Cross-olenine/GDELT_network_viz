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
- **Ingestion** : `asyncio` + `httpx` + Polars (téléchargement
  GDELT daily ZIP, parsing all-string, transformation, écriture
  Parquet Hive-partitionné `year=YYYY/month=MM`)
- **Stockage** : Parquet zstd, un fichier par mois
- **Couche query** : DuckDB lit les Parquet (`read_parquet([...])`),
  pré-agrège tous les événements au grain jour, le résultat est mis
  en cache par session via `@st.cache_data` ; chaque mouvement de
  filtre est ensuite un `pandas` `groupby` en mémoire sur la table
  cachée
- **Restitution** : Streamlit comme shell minimal (chrome masqué par
  CSS) + composant custom (`components.declare_component`) — iframe
  HTML/JS contenant Leaflet (tuiles + interactions carte) et D3
  (rendu SVG du réseau et des silhouettes pays). Toute l'UI de filtres
  vit dans le composant (sidebar slide-in custom) ; les changements
  sont poussés à Streamlit via le protocole `streamlit:setComponentValue`,
  qui déclenche un rerun Python recalculant les edges et les renvoyant
  au composant

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

## Évolution — composant Streamlit custom plein écran (2026-05-17)

### Besoin
Maximiser la surface visible de la carte (le réseau est l'objet
principal) et regrouper tous les filtres dans une UI compacte et
discrète, ouverte à la demande.

### Problèmes à résoudre
- **Sidebar Streamlit native** : occupe ~300 px de viewport en
  permanence et impose un look "dashboard" inadapté à une viz
  immersive.
- **Chrome Streamlit** : header, footer, toolbar et padding du
  block-container réduisent encore la surface utile.
- **Communication bidirectionnelle iframe ↔ Streamlit** : avec
  `components.v1.html` (injection HTML brute, stateless), le
  composant peut recevoir des données via `postMessage` mais ne peut
  pas en renvoyer vers Streamlit pour déclencher un rerun côté
  Python — donc impossible de gérer l'UI de filtres depuis l'iframe.

### Solution retenue
- Migration de `components.v1.html` vers `components.declare_component`
  qui implémente le protocole Streamlit
  (`streamlit:componentReady`, `streamlit:render`,
  `streamlit:setComponentValue`, `streamlit:setFrameHeight`).
  L'iframe peut désormais pousser des valeurs vers Streamlit.
- CSS injecté côté Python : `display: none` sur la sidebar, le header,
  le footer, la toolbar et la décoration Streamlit ; `iframe`
  forcée à `100vw × 100vh`.
- Sidebar custom intégrée au composant : bouton flottant rond 40×40
  qui ouvre un panneau 280×100vh animé (`transform 300ms ease`),
  contenant le range slider de dates, les radios catégorie et un
  compteur d'edges. Clic extérieur ferme le panneau.
- L'état de filtre vit côté Python dans `st.session_state` ; chaque
  modification depuis la sidebar custom déclenche un rerun, recompute
  les edges, et les renvoie au composant.

## Évolution — cartographie codes pays GeoJSON (2026-05-17)

### Besoin
Afficher correctement tous les pays présents dans les données GDELT,
sans en exclure silencieusement à cause de divergences de codification
dans le GeoJSON de référence.

### Problèmes à résoudre
- **Bug Natural Earth `ISO_A3 == "-99"`** : certains États (statuts
  contestés, divergences ISO/SO) portent la valeur sentinelle `"-99"`
  comme code ISO_A3. Lire `ISO_A3` sans fallback exclut ces pays du
  rendu — ils sont absents de la carte alors qu'ils sont présents
  dans les données GDELT.
- **Edges fantômes** : lorsqu'un code GDELT n'a pas de feature
  GeoJSON, le centroïde retourné par défaut était `(0, 0)` en
  coordonnées Leaflet — l'edge correspondant traçait une ligne
  fantôme vers le nord-ouest de la carte.

### Solution retenue
- **Résolveur dynamique** au chargement du GeoJSON : pour chaque
  feature, tentative `ISO_A3` puis fallback `ADM0_A3` (toujours
  présent, toujours code à 3 lettres). Aucune liste hardcodée — la
  table de correspondance est entièrement construite depuis le
  GeoJSON, donc fonctionne avec n'importe quelle version Natural
  Earth.
- **Centroïde invalide → null explicite** : `geoCentroid(code)` ne
  retourne plus jamais `(0, 0)` en fallback silencieux. Filtre amont
  des edges : on ne trace que si les deux extrémités ont un centroïde
  valide (présent + lat/lng/pixels finis).
- **Diagnostic console** : logs `[GeoJSON]` (features chargées,
  fallbacks ADM0_A3, features ignorées avec raison) et
  `[GDELT × GeoJSON]` (pays matchés vs sans feature) émis à chaque
  chargement et chaque changement de filtre.

## UI/UX — Décisions prises (2026-05-17)

- **Carte plein écran** : la sidebar Streamlit native est supprimée
  (CSS `display: none` côté Python). Le composant iframe occupe la
  totalité du viewport (`100vw × 100vh`).
- **Barre d'outils verticale fixe à gauche** : `position: fixed`,
  `left: 0`, `top: 0`, `height: 100vh`, `width: 48px`, fond blanc,
  légère ombre portée vers la droite (`box-shadow: 2px 0 6px`).
  Liste verticale de boutons (`flex-direction: column`, `gap: 8px`,
  `padding: 8px`).
- **Boutons de la barre** :
  - Filtres (☰) — implémenté, ouvre le panneau de filtres
  - Glossaire — prévu (slot réservé sous le bouton Filtres)
  - Chaque bouton : 36×36 px, fond transparent, `border-radius: 6px`,
    hover `#f0f0f0`, tooltip natif `title="…"`.
- **Panneau filtres** : slide depuis `left: 48px` (largeur 280 px,
  hauteur 100vh) pour ne pas recouvrir la barre d'outils. Clic
  extérieur (hors panneau et hors barre d'outils) ferme le panneau.
- **Zoom Leaflet initial** : `setView([20, 15], 3)` — centre sur le
  monde habité, zoom 3 pour éliminer les bandes grises haut/bas du
  viewport initial. `minZoom: 2`, `maxZoom: 8`.
- **Contrôles zoom Leaflet repositionnés** : déplacés en haut à
  droite (`top: 16px`, `right: 16px`) pour libérer la zone gauche
  occupée par la barre d'outils.

## Décisions précédemment bloquées — résolues

- **Comment représenter techniquement le réseau superposé à la carte ?**
  Résolu (2026-05-17) : Leaflet (carte raster + interactions zoom/pan)
  + D3 (rendu SVG du réseau et des silhouettes pays) à l'intérieur
  d'un composant Streamlit custom (`declare_component`). Aucun
  package Python de network viz côté serveur — tout le rendu est
  HTML/JS dans une iframe, Python ne fournit que les edges agrégés
  et les centroïdes via le protocole composant Streamlit.

## Décisions bloquées — nécessitent une exploration dédiée

(Aucune actuellement.)

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
