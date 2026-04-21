# Ascend-Bench

**Stack open source de benchmarking pour consulting IA — marchés régulés, souveraineté, conformité française.**

[![CI](https://github.com/Baptiste6913/Benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/Baptiste6913/Benchmark/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code compatible](https://img.shields.io/badge/Claude%20Code-compatible-blueviolet)](https://claude.com/claude-code)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

---

## Ce que c'est

`Ascend-Bench` est un **stack de recherche** — une collection de skills, sub-agents, workflows et grilles de scoring — qui transforme une instance [Claude Code](https://claude.com/claude-code) en **expert benchmarking pour marchés régulés** (santé, finance, public, défense).

Il est conçu pour des consultants seniors qui produisent des benchmarks de solutions logicielles à destination de grands comptes (CAC40, mutuelles, secteur public, industries régulées), avec une méthodologie qui met l'accent sur :

- **Vérification multi-niveaux** — 4 niveaux de contrôle (source primaire, triangulation, fraîcheur, validation humaine).
- **Regard critique systématique** — `critic` et `red-teamer` sont des étapes obligatoires du workflow.
- **Souveraineté numérique** — analyse capital / hébergement / modèles / dépendances sur tous les marchés régulés.
- **Livrables COPIL-ready** — Excel (tableau comparatif), Word (note de synthèse charte graphique), PowerPoint (slides).

---

## Démarrage rapide (3 minutes)

### Prérequis

- [Claude Code](https://claude.com/claude-code) installé (CLI dans le `PATH`, `claude --version` doit répondre).
- Git, Python ≥ 3.11, Node.js (pour `npx`).
- **Une clé API Firecrawl recommandée** (plan gratuit 500 crédits/mois suffisent pour 30 benchmarks/mois). Voir [INSTALL.md](INSTALL.md#3-obtenir-une-clé-firecrawl) pour le guide pas à pas.

### Installation

```bash
git clone https://github.com/Baptiste6913/Benchmark.git ascend-bench
cd ascend-bench

# Optionnel : pré-charger la clé Firecrawl pour éviter la saisie interactive
export FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxx

bash install.sh            # Linux / macOS / Git Bash
# ou
install.bat                # Windows (PowerShell ou cmd)
```

L'installeur crée `config/consultant.json` à la première exécution, configure le MCP Firecrawl dans `~/.claude/`, et déploie les skills + agents dans `~/.claude/skills/` et `~/.claude/agents/`.

### Premier benchmark

Lance `claude` dans un dossier vide, puis :

```
Benchmark-moi les solutions de RAG d'entreprise pour mutuelles santé.
Grille : scoring-grids/health-ai.json.
Mode : Full.
```

Le mainthread Claude Code orchestre la chaîne `discoverer` → `investigator` → `critic` → `red-teamer`, applique le scoring pondéré, et produit un livrable Excel + Word + synthèse exécutive (~60 min).

Détails complets dans [INSTALL.md](INSTALL.md).

---

## Modes d'exécution — Quick / Standard / Full

| Mode | Durée | Ce qui tourne | Livrable autorisé | Prompt |
|---|---|---|---|---|
| **Quick** | 20-40 min | discoverer + investigator | Markdown interne — **pas client** | `prompts/benchmark-quick.md` |
| **Standard** | 45-60 min | + weighted-scorer + critic | xlsx + docx marqués DRAFT INTERNAL | `prompts/benchmark-standard.md` |
| **Full** | 60-90 min | chaîne complète + red-team + checklist pre-delivery | xlsx + docx validés niveau 4 — **seul mode autorisé client / COPIL** | `prompts/benchmark-full.md` |

---

## Architecture

```
         Demande utilisateur
                │
                ▼
    ┌─────────────────────────┐
    │   WORKFLOW choisi       │   market-benchmark / vendor-dd / regulatory-check
    └────────────┬────────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │   MAINTHREAD (Claude)   │   orchestre, dispatch parallèle
    └────────────┬────────────┘
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
  discoverer  investigator investigator   (5-15 en parallèle)
      │          │          │
      └──────────┼──────────┘
                 ▼
           weighted-scorer
                 │
                 ▼  (mode ≥ Standard)
              critic
                 │
                 ▼  (mode = Full)
            red-teamer
                 │
                 ▼
        lib/render.py → xlsx + docx
```

- **[CLAUDE.md](CLAUDE.md)** — cerveau du stack (règles absolues, méthodologie, checklist de livraison).
- **[docs/run-persistence.md](docs/run-persistence.md)** — arborescence `outputs/<run_id>/`, audit trail, `firecrawl-ledger.json`.
- **[docs/v1.3-consolidation-plan.md](docs/v1.3-consolidation-plan.md)** — audit détaillé des décisions d'architecture v1.3.
- **[docs/v1.4-roadmap-from-hardening.md](docs/v1.4-roadmap-from-hardening.md)** — roadmap prochaine itération.

---

## Grilles de scoring incluses

| Grille | Secteur cible | Exemples de critères |
|---|---|---|
| `health-ai.json` | Santé / mutualistes | Conformité HDS, certif, souveraineté |
| `enterprise-saas.json` | B2B generic | Maturité, clients, intégrations, pricing |
| `regulated-industries.json` | Défense / aéro / industrie lourde | Souveraineté, clearance, exigences cloud |
| `public-sector-fr.json` | État / collectivités / EPA | RGS, SecNumCloud, RGAA, UGAP, FranceConnect |
| `lisi-souverainete.json` | Exemple industriel réel (LISI Group COMEX) | Souveraineté IA, by-design vs remédiation |

Les grilles sont du JSON documenté — **tu peux créer la tienne en 30 minutes** en copiant celle qui se rapproche le plus de ton secteur (7 critères × 5 niveaux × pondérations). Validation : `python scripts/validate_grid.py scoring-grids/<ta-grille>.json`.

---

## Fonctionnalités clés v1.3.1

- **Budget Firecrawl dynamique 2-passes** — P1 découverte large (1 scrape/vendor) → P2 approfondissement top 10 (3-5 scrapes/vendor). Ledger `outputs/<run_id>/firecrawl-ledger.json` pour audit.
- **Dealbreaker Phase 0** — acteurs écartés avant scoring pondéré, 4e bucket `exclus_dealbreaker`, onglet Excel dédié et section Word dédiée si non vide.
- **Run persistence `outputs/<run_id>/`** — arborescence déterministe par mission, audit complet, sidecar de `bench.json` canonique.
- **Investigation depth tagging** — `full` / `partial` / `shallow` dérivé du comptage Firecrawl/WebFetch/WebSearch.
- **Degraded mode disclaimer paramétrable** — seuil `scope.yaml.degraded_threshold` (défaut 0.5), formule pondérée `(shallow + partial/2) / total`, **encart rouge automatique dans le docx** si déclenché.
- **139 tests pytest** automatisés verrouillent les règles métier.

---

## Personnalisation par consultant

`config/consultant.json` (gitignoré) permet à chaque utilisateur de personnaliser les livrables sans forker le repo :

```json
{
  "name": "Nom Prenom",
  "email": "prenom.nom@exemple.fr",
  "handle": "prenom.nom"
}
```

Les placeholders `{{CONSULTANT_NAME}}`, `{{CONSULTANT_EMAIL}}`, `{{CONSULTANT_HANDLE}}` dans les fichiers déployés sont substitués par les valeurs du `consultant.json` lors de l'installation.

Pour changer d'identité sans tout réinstaller :
```bash
nano config/consultant.json
python scripts/apply_consultant_config.py config/consultant.json ~/.claude/skills ~/.claude/agents
```

---

## Validation et tests

```bash
# Tests unitaires pytest
python -m pytest tests/
# → 139 passed

# Valider un bench.json canonique
python scripts/validate_bench.py examples/<mission>/bench.json

# Valider toutes les grilles
python scripts/validate_grid.py --all

# Régénérer les livrables xlsx + docx après édition
python -m lib.render examples/<mission>/bench.json
```

---

## Exemples inclus

- **[examples/generic-demo/](examples/generic-demo/)** — bench LISI Group COMEX (6 acteurs européens, résilience IA souveraine). `bench.json` + xlsx + docx générés.
- **[examples/fnmf-gt2-ia/](examples/fnmf-gt2-ia/)** — bench FNMF GT2-IA (santé mutualiste).

Pour créer ton propre exemple, copie `examples/generic-demo/bench.json`, adapte `meta.client`, `meta.mission`, `actors[]`, `sources[]`, puis valide avec `validate_bench.py` et render avec `lib.render`.

---

## Philosophie

Les cinq principes directeurs :

1. **Minimalisme** — chaque skill a une raison d'être en une phrase. Pas de remplissage.
2. **Spécialisation** — calibré pour marchés régulés + souveraineté + conformité française.
3. **Vérification** — 4 niveaux de contrôle (source primaire, triangulation, fraîcheur, validation humaine).
4. **Regard critique** — le stack produit du doute méthodique, pas de la compilation.
5. **Réutilisabilité** — les grilles sont en JSON, adaptables à n'importe quel marché.

---

## Contribuer

Issues, PRs, remarques méthodologiques bienvenus. Voir [CONTRIBUTING.md](CONTRIBUTING.md).

Le workflow CI (`.github/workflows/ci.yml`) exécute pytest + validate_bench.py + validate_grid.py sur chaque PR.

---

## Origine & crédits

Développé par **[Ascend Partners](https://www.ascend-partners.com)** (Paris) pour ses équipes de conseil en transformation IA, puis open-sourcé en 2026 pour la communauté des consultants.

Intègre deux projets externes de qualité :

- **[Weizhena / Deep-Research-skills](https://github.com/Weizhena/Deep-Research-skills)** — moteur de recherche parallèle avec web-search-agent.
- **[199-biotechnologies / claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill)** — validation de citations et red teaming multi-persona.

Merci aux auteurs pour leur travail open source.

---

## License

MIT — voir [LICENSE](LICENSE).

---

## Besoin d'aide ?

- **Installation** → [INSTALL.md](INSTALL.md) — guide pas à pas avec obtention clé Firecrawl
- **Contribuer** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **Méthodologie** → [CLAUDE.md](CLAUDE.md) — cerveau du stack
- **Issue / bug** → [GitHub Issues](https://github.com/Baptiste6913/Benchmark/issues)
