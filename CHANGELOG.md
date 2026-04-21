# Changelog — Ascend-Bench

Format inspiré de [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning
[SemVer](https://semver.org/spec/v2.0.0.html).

---

## [1.3.1] — 2026-04-21 — Open source release publique

Première release publique du stack, sous licence MIT. Cette version condense l'ensemble du travail v1.0 → v1.3.1 produit initialement pour usage interne Ascend Partners.

### Added

- **Stack de benchmarking IA** calibré pour marchés régulés (santé, finance, public, défense)
  - 6 skills custom (market-scanner, vendor-deep-dive, sovereignty-analyzer, source-credibility, fact-checker, weighted-scorer)
  - 5 sub-agents spécialisés (benchmark-lead, discoverer, investigator, critic, red-teamer)
  - 6 workflows pas-à-pas (market-benchmark, vendor-due-diligence, regulatory-check, orchestrate-benchmark, pre-delivery-checklist, rescore-after-change)
  - 5 grilles de scoring JSON (health-ai, enterprise-saas, regulated-industries, public-sector-fr, lisi-souverainete)
- **Générateur de livrables `lib/render.py`** — xlsx (3 onglets : Matrice, Détails, Sources) + docx (11 sections, charte graphique)
- **Schéma canonique `bench.json`** (JSON Schema Draft 2020-12) + validator CLI
- **Script `rescore.py`** pour propager changements de grille ou révision de scores, avec diff structuré
- **Trois modes d'exécution** : Quick (20-40 min) / Standard (45-60 min) / Full (60-90 min)
- **Personnalisation par consultant** via `config/consultant.json` + placeholders
- **Budget Firecrawl dynamique 2 passes** (patch 3 v1.3)
  - P1 découverte (1 scrape/vendor), P2 approfondissement top 10 (3-5 scrapes)
  - Ledger `outputs/<run_id>/firecrawl-ledger.json`
  - Fallback WebFetch/WebSearch auto si budget épuisé
- **Phase 0 dealbreaker_check** (fix 1 v1.3)
  - `scope.yaml.dealbreakers` structuré (objets `{id, criterion, rule, verdict_if_violated, source_required}`)
  - Auto-traduction du format legacy v1.0
  - Bucket `exclus_dealbreaker` avant scoring pondéré
- **Run persistence `outputs/<run_id>/`** (patch 8 v1.3, Option A additive)
  - Arborescence déterministe : scope.yaml, discovery/, factsheets/, scoring/, reviews/, deliverables/, firecrawl-ledger.json, run.log
  - Convention `run_id = YYYYMMDD-HHMM-<client>-<usecase>`
- **Investigation depth tagging** (fix 4 v1.3)
  - `full / partial / shallow` dérivé du comptage firecrawl/webfetch/websearch
  - Seuil dégradé paramétrable via `scope.yaml.degraded_threshold` (défaut 0.5)
  - Formule pondérée `(shallow + partial/2) / total`
- **Render v1.3.1 conditionnel**
  - Encart rouge disclaimer dans docx si `degraded_mode_disclaimer` non vide
  - Onglet "Exclusions" xlsx + section exclusions docx si `exclus_dealbreaker` non vide
- **CI GitHub Actions** (`.github/workflows/ci.yml`) — pytest + validate_bench + validate_grid sur chaque PR
- **Documentation grand public** : README, INSTALL (avec guide Firecrawl complet), CONTRIBUTING, issue/PR templates
- **139 tests pytest verts** couvrant render, schema, scoring, dealbreakers, investigation_depth, run_id, ledger
- **Exemple public synthétique** (`examples/generic-demo/`) — 4 éditeurs fictifs pour démonstration

### Methodology

Le stack a été initialement développé et éprouvé en conditions réelles sur plusieurs missions internes chez Ascend Partners (2025-2026) avant d'être open-sourcé dans cette release. Les benchs clients utilisés pour ces missions (données confidentielles) ne sont pas publiés avec le stack — seul un exemple synthétique public est fourni dans `examples/generic-demo/`.

### License

MIT — voir `LICENSE`.

---

*Les changelogs des versions internes v1.0, v1.1.0, v1.1-hardening, v1.1.1-fixpack, v1.2.0, v1.2.1, v1.2.2, v1.3.0 ne sont pas reproduits ici — ils décrivaient le détail de chaque sprint sur des missions internes confidentielles. Cette v1.3.1 est le premier livrable public consolidé.*
