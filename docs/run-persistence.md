# Run persistence — `outputs/<run_id>/` (v1.3, patch 8 adapté)

Ce document fixe la convention de persistance d'un run Ascend-Bench. Il a été repris depuis
`v1.1-hardening/docs/run-persistence.md` et **adapté** à l'architecture `bench.json` canonique
introduite en Sprint 1 (v1.1.0) et au render engine `lib/render.py` du Sprint 2 (v1.2.0).

## Principe directeur (v1.3 — Option A "additive")

**`bench.json` reste la seule source de vérité** du bench. `outputs/<run_id>/` est un
**sidecar d'audit** qui trace comment le bench a été produit — pas une substitution.

```
bench.json                         ← source de vérité (lu par lib/render.py)
  ↔
outputs/<run_id>/                  ← trace du run qui a produit bench.json (audit)
```

### Où vit `bench.json` en v1.3 ?

Deux chemins sont acceptés par `lib/render.py` et `scripts/validate_bench.py` :

1. **Fixtures pérennes** (LISI, FNMF…) : `examples/<mission>/bench.json` — versionnées, servent
   de référence pour les tests et de documentation.
2. **Nouvelles missions** : `outputs/<run_id>/bench.json` — gitignoré (data client), au
   côté des artefacts d'audit.

Aucun chemin n'est imposé par le code — c'est une convention de disposition. Un consultant
peut faire évoluer un `outputs/<run_id>/bench.json` et le migrer en `examples/` après
anonymisation (devient fixture).

## Convention `run_id`

```
<run_id> = YYYYMMDD-HHMM-<client-slug>-<usecase-slug>
```

Règles :

- `YYYYMMDD-HHMM` : date/heure de démarrage du run, timezone locale du consultant.
- `client-slug` : **un seul mot ASCII kebab-minus-dashes** (`ascend`, `fnmf`, `dgfip`, `maif`, `interne`) — max 40 chars. Pas de tiret interne (lève l'ambiguïté avec usecase-slug).
- `usecase-slug` : kebab-case ASCII, **peut contenir des tirets** (`banque-privee-fr`, `ia-conv-n1`, `rag-benefs`), max 40 chars.
- Exemples :
  - `20260421-1120-ascend-banque-patrimoniale-privee-fr`
  - `20260503-0900-fnmf-gt2-ia-conv`
  - `20260614-1500-interne-veille-ai-ops`

Le `run_id` est figé en début de run (dans `scope.yaml`) et ne change plus. Si le client ou le
cas d'usage change en cours, c'est un **nouveau run**, pas une modification de l'existant.

## Arborescence

```
outputs/<run_id>/
├── scope.yaml                    # Contrat d'entrée (benchmark-lead en cadrage, v1.3)
├── discovery/
│   ├── raw-solutions.json        # Output brut discoverer (append-only par instance)
│   └── canonical-solutions.json  # Output entity-normalizer (si Lot 3 patch 2 mergé)
├── factsheets/
│   └── <vendor-slug>.json        # 1 fichier par éditeur (investigator × N)
├── scoring/
│   ├── grid-used.json            # Snapshot de la grille (pour audit)
│   ├── scores.json               # Output weighted-scorer (4 buckets v1.3)
│   └── dealbreaker-check.json    # Audit Phase 0 (v1.3 fix 1)
├── reviews/
│   ├── critic-report.md
│   └── red-team-report.md
├── deliverables/
│   ├── <run_id>.xlsx             # Sortie lib/render.py
│   ├── <run_id>.docx             # Sortie lib/render.py
│   └── <run_id>.pptx             # Optionnel
├── bench.json                    # Source de vérité (v1.3 Option A)
├── firecrawl-ledger.json         # Budget Firecrawl + fallbacks (v1.3 patch 3)
├── tools-health.json             # Ping Firecrawl/WebFetch/WebSearch (v1.3 fix 4)
├── blocked-urls.json             # URLs 403/timeout pour traitement manuel (v1.3 fix 4)
└── run.log                       # JSONL — 1 ligne par événement
```

**`outputs/` est gitignoré** (cf. `.gitignore`). Un run qui doit devenir fixture est migré
manuellement dans `examples/<mission>/` après anonymisation.

## Format `run.log` (JSONL)

Une ligne par événement, parseable ligne à ligne. Format d'événement :

```jsonl
{"ts":"2026-04-21T11:20:00","agent":"benchmark-lead","event":"scope_ready","mode":"standard"}
{"ts":"2026-04-21T11:22:00","agent":"mainthread","event":"phase","name":"discovery_start","parallel_agents":3}
{"ts":"2026-04-21T11:28:00","agent":"discoverer-a","event":"solutions_found","count":15}
{"ts":"2026-04-21T11:30:00","agent":"weighted-scorer","event":"dealbreaker_check","excluded":1,"passed":14}
{"ts":"2026-04-21T11:40:00","agent":"weighted-scorer","event":"scoring_complete","main":10,"a_approfondir":3,"insuffisants":1,"exclus":1}
{"ts":"2026-04-21T11:45:00","agent":"critic","event":"report_written","blocking":0,"warnings":3}
{"ts":"2026-04-21T11:48:00","agent":"render","event":"deliverables_written","xlsx":"...","docx":"..."}
```

### Champs minimaux

| Champ | Type | Obligatoire | Notes |
|---|---|---|---|
| `ts` | ISO 8601 (UTC recommandé, local toléré) | ✅ | Timestamp de l'événement |
| `agent` | string | ✅ | Identifiant de l'émetteur (nom d'agent, "mainthread", "render", "validator") |
| `event` | string | ✅ | Type d'événement (`start`, `phase`, `scope_ready`, `scoring_complete`, etc.) |
| + champs libres | mix | — | Dépend du type d'événement |

## Contrat par étape

Chaque agent/skill qui écrit un output respecte :

1. **Lit ses inputs** depuis l'emplacement attendu.
2. **Écrit son output** à l'emplacement canonique **avant** de rendre la main — pas à la fin
   d'un appel multi-étapes, mais à chaque étape atomique.
3. **Loggue** dans `run.log` un événement JSON à l'entrée et à la sortie de l'étape.

### Mapping producer → chemin

| Producer | Output path |
|---|---|
| benchmark-lead (cadrage) | `scope.yaml` |
| discoverer | `discovery/raw-solutions.json` (append par instance) |
| entity-normalizer (Lot 3) | `discovery/canonical-solutions.json` |
| investigator × vendor-deep-dive | `factsheets/<vendor-slug>.json` |
| weighted-scorer Phase 0 (v1.3) | `scoring/dealbreaker-check.json` |
| weighted-scorer | `scoring/grid-used.json` + `scoring/scores.json` |
| critic | `reviews/critic-report.md` |
| red-teamer | `reviews/red-team-report.md` |
| benchmark-lead (consolidation) | `bench.json` |
| lib/render.py | `deliverables/<run_id>.{xlsx,docx}` |
| tous | `run.log` (append JSONL) |

## Reprise — `--resume <run_id>` (reporté v1.4)

La reprise automatisée est **hors scope v1.3** (ne mérite pas d'implémentation tant que le
test `--resume` n'a pas été exercé en conditions réelles — cf. BACKLOG Lot 4). L'arborescence
ci-dessus est néanmoins conçue pour supporter `--resume` sans changement structurel ultérieur.

## Audit & confidentialité

- `outputs/` est gitignoré — jamais commité.
- Un run migré en fixture passe par `examples/<mission>/` après anonymisation.
- Le `bench.json` final peut être commité sous `examples/` ; les artefacts d'audit
  (`firecrawl-ledger.json`, `run.log`, `tools-health.json`) **restent** sous `outputs/`.

## Slug conventions

- `client-slug` : `ascend-interne`, `fnmf`, `maif`, `dgfip`.
- `usecase-slug` : `banque-privee-fr`, `ia-conv-n1`, `rag-benefs`, `ocr-medical`.
- Kebab-case strict, sans accents, max 40 chars.

## Cohérence avec bench.json canonique

Le schéma `bench.json` est **inchangé** par le patch 8 v1.3. Les artefacts
`outputs/<run_id>/` sont des sidecars d'audit ; ils ne remplacent aucun champ de `bench.json`.
Un consommateur externe (ex: PowerPoint generator, export CSV) continue de lire `bench.json`
seul, sans besoin de parcourir `outputs/<run_id>/`.
