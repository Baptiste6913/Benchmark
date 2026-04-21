# BACKLOG — items reportés

Items identifiés pendant le Sprint 1 mais hors scope (par design : pas de feature creep).
À reprendre dans les Sprints ultérieurs ou sur demande explicite.

## Sprint 2 — livré en v1.2.0

- [x] **`lib/render.py`** — module qui prend un `bench.json` + la grille, produit le
      xlsx et le docx conformes aux specs. Charte Ascend stricte sur le docx.
- [x] **Workflow `rescore-after-change.md`** + `scripts/rescore.py` — propagation d'un
      changement de grille ou d'une révision de scoring vers les livrables.
- [x] **JSON Schema pour scoring-grids** — `schemas/scoring-grid.schema.json` + script
      `scripts/validate_grid.py`.

Reporté au Sprint 3 :

- [ ] **Durcissement `validate_bench.py` par mode** — en mode `full`, exiger `critic`,
      `red_team` et `transverse` non vides ; en mode `standard`, exiger `critic`.

## À reprendre en Sprint 3 (capitalisation)

- [x] ~~**Test suite minimale (`pytest`)**~~ — livré partiellement en v1.2.0 :
      40 tests pytest couvrent rendu xlsx/docx, validation grilles, rescore.
      **Reste à ajouter** : lint YAML frontmatter skills/agents, smoke test
      install.sh syntax, test snapshot visuel du docx.
- [ ] **GitHub Actions CI** — lance la test suite + `bash -n` sur install.sh + validation
      de `examples/*/bench.json` et scoring-grids sur chaque PR.
- [ ] **Test snapshot visuel du docx** — convertir en PDF et comparer les pages
      rendues pour attraper des régressions de mise en page (ajout Sprint 2 retro).
- [ ] **Migration `examples/fnmf-gt2-ia/` vers bench.json** — tester le générateur
      sur un deuxième exemple pour éviter les biais LISI-spécifiques (ajout Sprint 2 retro).
- [ ] **Versioning global + `VERSION` fichier à la racine** — aligné sur SemVer,
      cohérent avec CHANGELOG.md.
- [ ] **Lock des skills externes** — `git clone --depth 1` → `git clone` + `git
      checkout <commit-sha>`. Script `scripts/update-external-skills.sh` pour bump
      contrôlé.
- [ ] **Workflow `peer-review.md`** — playbook formel pour la validation niveau 4
      effectuée par un pair consultant (pas juste le consultant responsable).
- [ ] **Template `triple-partage-de-la-valeur.md`** — skill ou prompt injectable qui
      opérationnalise la méthodo Ascend Groupement/Bénéficiaire/Salarié. Aujourd'hui
      mentionnée dans CLAUDE.md mais non déclenchée automatiquement.
- [ ] **Doc `docs/collaborate.md`** — playbook pour qu'un pair consultant reprenne un
      bench en cours (qu'exporter, qu'anonymiser, qu'committer).
- [ ] **`/agents` post-install** — solution pour pousser l'user à recharger la session
      Claude Code après install. Peut-être un fichier `.claude-reload-me` créé par
      l'installer qui déclenche un message dans la prochaine session.

## Ajouté par hotfix Sprint 2

- [ ] **Migration `label_fr` sur les 3 autres grilles** — `enterprise-saas.json`,
      `health-ai.json`, `regulated-industries.json`. Le validator émet aujourd'hui un
      warning pour chaque critère sans `label_fr` (16 warnings au total). Pas bloquant
      mais les livrables générés depuis ces grilles auront des en-têtes non-accentués.
      Temps estimé : 15 min par grille (6 critères × 3 grilles). **Nouvelle grille
      `public-sector-fr.json` (v1.2.2) ajoute 2 warnings supplémentaires** sur
      `referencement_ugap_ccag` et `interop_franceconnect`.

## Cherry-picks restants depuis `archive/v1.1.1-fixpack`

Audit v1.2.2 (voir CHANGELOG) a identifié 14 items à cherry-picker depuis les
branches archivées. Lot 1 appliqué en v1.2.2 (LICENSE + patch(10) + patch(1)).
Lots 2, 3, 4 restants ci-dessous.

### Lot 2 — Améliorations investigator / scoring (~1h30 total)

- [x] ~~**patch(3) `078a43b` — dynamic Firecrawl budget + two-pass investigation**~~.
      **IN REVIEW (v1.3-consolidation, PR #TBD)** — adapté depuis `078a43b`, implémenté
      par-dessus la doctrine mainthread-orchestrator. Cf. `docs/v1.3-consolidation-plan.md`.
- [ ] **patch(6) `4aea98a` — fact-checker différencié par type de claim**.
      Modifie `skills/fact-checker/SKILL.md`. Différencie règles selon claim
      (certification = 2 sources primaires, pricing = 1 source primaire + 1
      analyste, etc.). Effort : S.
- [ ] **patch(4) `8ebf947` — completeness_ratio anti phantom rankings**. Modifie
      `skills/weighted-scorer/SKILL.md` + ajoute `completeness_thresholds` dans
      les 3 grilles legacy. Le champ root est déjà accepté par le schéma depuis
      v1.2.2. Effort : M.

### Lot 3 — Nouvelles briques méthodo (~2-3h total)

- [ ] **patch(2) `38fa6a6` — skill `entity-normalizer`**. Nouveau skill à intégrer
      entre scanner et investigator pour dédoublonner les solutions nommées
      différemment. Effort : M.
- [ ] **patch(5) `721158c` — freshness_policy par critère + verdict STALE**.
      Modifie les 3 grilles legacy. **COMBO recommandé avec la migration
      `label_fr`** (BACKLOG ci-dessus) — les deux modifs touchent les mêmes
      fichiers, un seul PR. Le champ `criterion.freshness_days` est déjà accepté
      par le schéma depuis v1.2.2. Effort : M.
- [x] ~~**fix(1) `693124b` — dealbreaker_check phase 0**~~.
      **IN REVIEW (v1.3-consolidation, PR #TBD)** — adapté depuis `693124b`.
      Scope-clarifier hunks foldés dans `benchmark-lead` (doctrine main Sprint 1).
      Format scope.yaml v1.1.1 structuré + auto-traduction legacy.
- [ ] **fix(2) `8e83888` partiel — règle critic N/D systémique**. Ne pas reprendre
      RGAA hints (hors scope LISI). Effort : S.

### Lot 4 — Features (à redimensionner après prochain bench)

- [ ] **patch(7) `2470075` — agent `scope-clarifier`**. PARTIEL : notre
      `benchmark-lead` en mode cadrage couvre ~70% du besoin. Décision :
      fusionner dans benchmark-lead OU créer agent dédié. À trancher au
      prochain run réel. Effort : M.
- [x] ~~**patch(8) `1ffae86` — run persistence (partie arborescence)**~~.
      **IN REVIEW (v1.3-consolidation, PR #TBD)** — Option A additive retenue :
      bench.json reste canonique, outputs/<run_id>/ ajouté en sidecar d'audit.
      Le flag `--resume` reste reporté v1.4.
- [ ] **patch(9) `7e3285f` — memory bank vendor factsheets**. **Conflit conceptuel
      avec `bench.json` canonique** (les factsheets sont dans bench.actors[]).
      Gros sujet : cross-mission persistence. À redimensionner après prochain
      bench. Effort : L.
- [ ] **`docs/architecture.md`** depuis commit `5900e9b` — doc d'architecture
      complète (363 lignes). Notre README est à jour Sprint 2 mais un doc dédié
      serait mieux. Effort : M (adaptation aux décisions architecturales Sprint
      1/2).
- [x] ~~**fix(4) `049d1ef` — degraded-mode guard + investigation_depth**~~.
      **IN REVIEW (v1.3-consolidation, PR #TBD)** — adapté avec seuil paramétrable
      (scope.yaml.degraded_threshold) et formule pondérée traitant le cas 10/15
      partial.

### Reporté v1.4 (non inclus dans v1.3-consolidation)

- [ ] **patch(2) entity-normalizer**, **patch(4) completeness_ratio**,
      **patch(5) freshness/STALE**, **patch(6) fact-checker claim_type**.
- [ ] **patch(7) scope-clarifier agent dédié** — **décidé v1.3 Q3 : fold dans
      benchmark-lead**. Reste ouvert si un second bench révèle un besoin d'agent séparé.
- [ ] **patch(9) memory bank**, **fix(2) critic N/D systémique**, **docs/architecture.md complète**.
- [ ] **`--resume <run_id>` flag actif**.
- [ ] **Render xlsx/docx des nouveaux champs v1.3** : colonne investigation_depth,
      onglet Exclusions dealbreaker, encart rouge degraded_mode_disclaimer.
      Data OK dans bench.json (v1.3), présentation visuelle déférée.

## Petits items (à caser quand opportunité)

- [ ] **Handling "fichier absent côté repo mais présent côté user"** dans
      `smart-copy` — orphelins post-refactor. Détecter et warner, pas supprimer.
- [ ] **`schemas/consultant.schema.json`** — si `config/consultant.json` grossit au-delà
      de 3 champs.
- [ ] **Installeur batch** testé end-to-end sur Windows cmd. Seul `install.sh` a été
      testé en dry-run lors du Sprint 1.
- [ ] **`scripts/apply_consultant_config.py`** : ajouter une option `--revert` pour
      remettre les placeholders (utile pour contribuer au repo depuis une installation
      personnalisée).
- [ ] **Bench LISI `bench.json`** : compléter les sources manquantes (44/62+). Pas
      critique, représentatif suffit pour le test de non-régression.

## Non priorités (à ignorer sauf réclamation)

- [ ] Refonte pure du `README.md` (ordre des sections un peu aléatoire après les ajouts
      Sprint 1).
- [ ] Internationalisation des messages installeur (fr + en).
- [ ] Support PowerShell natif (au-delà de `install.bat` exécutable depuis PowerShell).
