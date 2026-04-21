<!-- Merci de contribuer. Remplis les sections ci-dessous puis supprime ce commentaire. -->

## Résumé

<!-- 2-3 bullets. Qu'est-ce qui change et pourquoi ? -->

-
-

## Type de changement

- [ ] Nouvelle fonctionnalité (feat)
- [ ] Correction de bug (fix)
- [ ] Amélioration documentaire (docs)
- [ ] Refactor (sans changement de comportement)
- [ ] Nouvelle grille de scoring
- [ ] Chore / maintenance (ci, lint, deps)

## Test plan

- [ ] `pytest tests/` passe (139 tests attendus, ± nouveaux tests)
- [ ] `scripts/validate_bench.py examples/generic-demo/bench.json` → `[ ok ]`
- [ ] `scripts/validate_grid.py --all` → toutes grilles valides
- [ ] Render LISI : `python -m lib.render examples/generic-demo/bench.json --out /tmp/test/`
- [ ] (Si modif lib/) Comparaison render LISI avant/après → sémantiquement identique

## Breaking changes

<!-- Décrire tout changement qui casse la compatibilité existante. Sinon "Aucun." -->

## Migration notes

<!-- Comment les utilisateurs existants doivent-ils adapter leur installation / leurs benchs ? -->

## Checklist

- [ ] Mes commits ont des messages en français, verbe à l'infinitif
- [ ] Mes changements sont documentés dans le CHANGELOG.md (si visible utilisateur)
- [ ] J'ai ajouté / mis à jour les tests pytest nécessaires
- [ ] Le CI `.github/workflows/ci.yml` est vert sur ma branche
- [ ] J'ai lu le CONTRIBUTING.md

## Issues liées

<!-- Closes #N, Fixes #N, Refs #N -->
