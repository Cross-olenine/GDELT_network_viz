# Domain Glossary — GDELT Network Viz

### Edge (graphe pays)
Définition : Agrégat de tous les événements GDELT entre deux pays sur une
période donnée, représenté comme un lien directionnel entre deux nœuds du
réseau. Un edge n'existe que si Actor1CountryCode ET Actor2CountryCode sont
tous deux non vides et correspondent à des États (codes CAMEO à 3 lettres
ISO-compatibles, hors codes régionaux custom). Chaque edge porte 4 scores
(score_positif, score_negatif, score_neutre, score_global) et un tag de
type (état→état, état→org, etc.) pour permettre un filtrage dans l'interface.
Source : Décision projet session 2026-05-14
Statut : confirmé
Champ(s) associé(s) : Actor1CountryCode, Actor2CountryCode (docs/data-contracts.md)

### GoldsteinScale
Définition : Score numérique de -10 à +10 assigné statiquement à chaque
type d'événement CAMEO. Représente la valeur théorique de coopération
(valeurs positives) ou de conflit (valeurs négatives) associée à ce type
d'événement. Ce n'est pas un calcul NLP — la valeur est identique pour
tous les événements d'un même type CAMEO. 100% rempli sur l'échantillon,
32 valeurs discrètes observées.
Source : Documentation GDELT + profiling terrain session 2026-05-14
Statut : confirmé
Champ(s) associé(s) : GoldsteinScale (docs/data-contracts.md)

### AvgTone
Définition : Moyenne du ton calculé par analyse NLP (traitement du langage
naturel) sur l'ensemble des articles sources couvrant un événement donné.
Variable et contextuel — deux événements de même type CAMEO peuvent avoir
des AvgTone très différents selon la couverture médiatique. Complémentaire
du GoldsteinScale (corrélation r=0,31 mesurée sur l'échantillon). Plage
observée : [-12,5 ; +11,2]. 100% rempli sur l'échantillon.
Source : Documentation GDELT + profiling terrain session 2026-05-14
Statut : confirmé
Champ(s) associé(s) : AvgTone (docs/data-contracts.md)

### Codes CAMEO pays
Définition : Système hybride de 276 codes à 3 lettres utilisé par GDELT
pour identifier les acteurs géopolitiques dans les champs Actor1CountryCode
et Actor2CountryCode. Composé de 249 codes pays (majoritairement ISO 3166-1
alpha-3, avec quelques divergences) et de 27 codes régionaux custom
(exemples : AFR = Afrique, MEA = Moyen-Orient, EUR = Europe, LAM =
Amérique latine, SEA = Asie du Sud-Est, BLK = Balkans, CAU = Caucase...).
A ne pas confondre avec Actor1Geo_CountryCode / Actor2Geo_CountryCode qui
utilisent le format FIPS 10-4 à 2 lettres.
Les codes régionaux custom sont à exclure pour la construction des edges
État-État.
Source : Documentation GDELT + profiling terrain session 2026-05-14
Statut : confirmé
Champ(s) associé(s) : Actor1CountryCode, Actor2CountryCode (docs/data-contracts.md)

### Moyenne pondérée par log1p(NumMentions)
Définition : Formule d'agrégation des scores relationnels entre deux pays.
Pour une paire (pays A, pays B) sur une période donnée, le score est calculé
comme la somme des (GoldsteinScale_i × log1p(NumMentions_i)) divisée par
la somme des log1p(NumMentions_i), sur l'ensemble des événements i de la
paire. L'usage de log1p plutôt que NumMentions brut est justifié par la
distribution très asymétrique de NumMentions (médiane=10, max=1 530 sur
l'échantillon) : sans compression logarithmique, un seul événement très
médiatisé écraserait tous les autres. log1p(x) = log(1+x) permet de traiter
correctement les événements avec NumMentions=0.
Source : Décision projet session 2026-05-14
Statut : confirmé
Champ(s) associé(s) : GoldsteinScale, NumMentions (docs/data-contracts.md)
