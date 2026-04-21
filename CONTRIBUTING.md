# Contribuer à Ascend-Bench

Merci de considérer une contribution ! Ce projet est ouvert aux améliorations méthodologiques, corrections de bugs, nouvelles grilles de scoring, et adaptations sectorielles.

## Checklist avant PR

- [ ] `pytest tests/` passe en local (**139 tests verts attendus**)
- [ ] `scripts/validate_bench.py examples/generic-demo/bench.json` retourne `[ ok ]` (non-régression)
- [ ] `scripts/validate_grid.py --all` valide toutes les grilles
- [ ] Le code ajouté est sous **MIT** (même licence que le repo)
- [ ] Les modifications documentaires sont **en français** (cohérence avec le reste du stack)

## Types de contributions bienvenues

### Nouvelles grilles de scoring sectorielles

Les 5 grilles actuelles (`health-ai`, `enterprise-saas`, `regulated-industries`, `public-sector-fr`, `lisi-souverainete`) ne couvrent pas tout. Exemples de contributions utiles :
- `scoring-grids/fintech-banque.json` — secteur bancaire, DSP2, LCB-FT
- `scoring-grids/retail-ecommerce.json` — retail, omnicanal, data client
- `scoring-grids/telecom-cyber.json` — opérateurs, 5G, souveraineté
- `scoring-grids/education-edtech.json` — éducation, RGPD enfants, accessibilité

Template : copier une grille proche, adapter critères + pondérations, valider avec `scripts/validate_grid.py`, ajouter 5 entrées `test_validate_grids.py` paramétrées.

### Corrections de méthodologie

Le stack a des **règles absolues** (CLAUDE.md §3). Si tu détectes une incohérence ou un angle mort :
- Ouvre une **issue** d'abord pour discuter (évite les PRs abandonnées)
- Propose une modification **justifiée par un cas d'usage concret** (pas abstrait)
- Ajoute un test pytest qui verrouille la nouvelle règle

### Améliorations render (xlsx / docx)

Si tu trouves un défaut visuel dans `lib/_xlsx.py` ou `lib/_docx.py` :
- Reproduis sur le bench LISI (`examples/generic-demo/bench.json`)
- Propose le fix
- Ajoute un test dans `tests/test_render_docx.py` ou `test_render_xlsx.py` qui verrouille

### Workflows / agents / skills

Les agents (`agents/*.md`) et skills (`skills/*/SKILL.md`) sont des fichiers Markdown que Claude Code charge. Pour proposer un nouvel agent :
- Il doit avoir une **raison d'être en une phrase** (pas de redondance avec les agents existants)
- Il doit être **dispatchable par le mainthread**, pas par un sub-agent (limitation native Claude Code)
- Exemple candidat : `cost-estimator` (calcule TCO), `compliance-gap-analyzer` (checklist régulatoire)

## Style de code

### Python

- Suit les conventions de `lib/render.py` (imports triés, type hints, docstrings concises en français).
- Pas de `f-string` dans les docstrings (problème d'échappement).
- Pour les tests : fixtures pytest + `@pytest.mark.parametrize` quand pertinent.

### Markdown

- Titres en français.
- Tableaux alignés (pipe `|` avec padding).
- Code blocks avec langage : ` ```python ` / ` ```bash ` / ` ```yaml `.
- Pas d'émojis (sauf dans CONTRIBUTING.md où on tolère 😊).

### JSON (grilles, bench.json)

- 2 espaces d'indentation.
- `name`, `description`, `id` obligatoires sur tout critère.
- Pondérations somment à `1.0` (±0.001 toléré par `validate_grid.py`).
- Chaque niveau de l'échelle a `value`, `label`, `requires`.

## Workflow de PR

1. **Fork** ce repo vers ton compte.
2. **Branch** depuis `main` : `git checkout -b feat/ma-contribution`.
3. **Commits atomiques** — un commit = une modification logique. Message en français, verbe à l'infinitif :
   ```
   feat(grid): ajouter grille fintech-banque DSP2
   fix(render): corriger calcul page break dans _docx
   docs(install): clarifier procédure Firecrawl OAuth
   ```
4. **Push** vers ton fork.
5. **Ouvre une PR** vers `Baptiste6913/Benchmark:main`. Body :
   - Résumé en 3 bullets
   - Test plan (commandes exécutées pour valider)
   - Breaking changes (si applicables)
6. **CI** (`.github/workflows/ci.yml`) doit être verte. Si rouge, inspecte les logs et corrige.

## Code of conduct

- Sois **respectueux** dans les reviews.
- **Argumente tes refus** (pas juste "non, c'est pas bien").
- Pas de **drama** sur la langue (le stack est en français par choix — traductions EN acceptées en sus dans un autre fichier, jamais en remplacement).

## Reporter une vulnérabilité de sécurité

**Ne PAS ouvrir une issue publique.** Envoie un mail à `security@ascend-partners.com` avec :
- Description du problème
- Étapes de reproduction
- Impact estimé
- Suggestion de fix si tu en as une

Nous te répondrons sous 72h et coordonnerons la divulgation responsable.

## Reconnaissance

Toute PR mergée donne droit à une mention dans le CHANGELOG de la release concernée. Les contributeurs réguliers sont ajoutés au fichier `CONTRIBUTORS.md` (à créer dès qu'on aura 3+ contributeurs externes).

---

Merci pour ta contribution — le stack devient utile pour plus de monde à chaque PR mergée.
