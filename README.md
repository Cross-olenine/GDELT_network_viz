# [Nom du projet]

## Structure
- `docs/`        — connaissance accumulée (sur main, partagée par toutes les branches)
- `exploration/` — EDA, notebooks, scripts jetables (branche exploration uniquement)
- `src/`         — code de production (branches dev → recette → prod)
- `tests/`       — tests unitaires et d'intégration (couvre src/ uniquement)
- `.claude/`     — agents et configuration Claude Code

## Branches
- `main`        — source de vérité pour docs/
- `dev`         — développement en cours
- `recette`     — validation avant prod
- `prod`        — application stable
- `exploration` — ne merge jamais sur main
