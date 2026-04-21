# Installation — Ascend-Bench

Ce guide te prend depuis **zéro** (rien d'installé) jusqu'à ton **premier benchmark qui tourne**. Durée : 10 minutes.

---

## 1. Prérequis système

### Obligatoires

- **[Claude Code](https://claude.com/claude-code)** — CLI d'Anthropic. Vérifie :
  ```bash
  claude --version
  # → 2.x.x ou supérieur
  ```
- **Git** ≥ 2.20 :
  ```bash
  git --version
  ```
- **Python** ≥ 3.11 :
  ```bash
  python3 --version
  ```
- **Node.js** ≥ 18 (pour `npx` utilisé par le MCP Firecrawl) :
  ```bash
  node --version
  ```

### Recommandé

- **[Firecrawl](https://www.firecrawl.dev/)** API key (gratuit) — voir section [§3](#3-obtenir-une-clé-firecrawl).
- Sans clé Firecrawl, les `investigator` fonctionnent en **mode dégradé** (WebFetch seul), ce qui limite la profondeur des fiches éditeur. Le flag `investigation_depth: partial` est automatiquement posé.

---

## 2. Cloner et installer

```bash
git clone https://github.com/Baptiste6913/Benchmark.git ascend-bench
cd ascend-bench
```

**Dépendances Python** (installées automatiquement par `install.sh` si besoin) :

```bash
pip install -r requirements.txt
# ou individuellement :
pip install openpyxl python-docx pyyaml jsonschema pytest
```

**Installer les skills + agents Claude Code** :

```bash
# Optionnel : pré-charger la clé Firecrawl (sinon l'installeur la demande)
export FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxx

bash install.sh            # Linux / macOS / Git Bash
# ou
install.bat                # Windows (PowerShell ou cmd)
```

**Vérification** : l'installeur doit afficher :
- `[ ok ]` skills copiées dans `~/.claude/skills/` (6 skills)
- `[ ok ]` agents copiés dans `~/.claude/agents/` (5 agents)
- `[ ok ]` MCP Firecrawl configuré (si clé fournie)
- `[ ok ]` `config/consultant.json` créé (si pas déjà présent)

### Options de l'installeur

| Flag | Effet |
|---|---|
| `--dry-run` | Affiche ce qui changerait sur `~/.claude/` sans rien écrire. |
| `--force` | En cas de conflit (fichier utilisateur modifié vs repo), crée un backup `.bak` puis écrase. |
| `--help` / `-h` | Affiche l'aide. |

**Comportement par défaut** : si un fichier destination a été modifié côté utilisateur, l'installeur prompt `[k]eep / [o]verwrite / [b]ackup-and-overwrite`.

---

## 3. Obtenir une clé Firecrawl

Firecrawl est le service qui permet aux `investigator` de scraper les sites éditeurs (plus fiable que WebFetch pour les sites à paywall ou JS-heavy).

### Étape 1 — Créer un compte

1. Aller sur **https://www.firecrawl.dev/**
2. Cliquer **Sign up** (en haut à droite)
3. S'inscrire avec email + mot de passe ou GitHub OAuth
4. Valider l'email de confirmation

### Étape 2 — Plan recommandé

Le **plan gratuit "Hobby"** donne **500 crédits / mois** — suffisant pour **~30 benchmarks / mois** avec le profil typique 2-passes (P1 = 1 scrape / vendor × 10 vendors + P2 = 3-5 scrapes × 3-5 top = ~15-30 scrapes / bench).

- **Free Hobby** : 500 crédits / mois, 1 thread, suffit pour un consultant en solo.
- **Starter $16/mois** : 3 000 crédits / mois, 3 threads en parallèle — pour un usage plus soutenu.
- **Growth** : voir le pricing sur firecrawl.dev.

Pour démarrer, **le plan gratuit suffit amplement**.

### Étape 3 — Récupérer la clé

1. Dans le dashboard Firecrawl, aller dans **Settings** → **API Keys**.
2. Cliquer **+ Create API key**.
3. Copier la clé (format `fc-xxxxxxxxxxxxxxxxxxxxxxxxxxx`, ~40 caractères).
4. **Stocker la clé en sécurité** (pas dans un fichier commité — le `.gitignore` exclut `.env*`).

### Étape 4 — Fournir la clé au stack

Trois options, par ordre de préférence :

**Option A — Variable d'environnement (recommandé)**
```bash
# Ajouter à ~/.zshrc ou ~/.bashrc :
export FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxx
# Puis recharger le shell :
source ~/.zshrc
```
Relancer `install.sh` — il détecte automatiquement la variable et configure le MCP.

**Option B — Prompt interactif install.sh**
Si tu ne veux pas mettre la clé dans `~/.zshrc`, l'installeur la demande interactivement la première fois.

**Option C — Fichier `.env` local**
```bash
# À la racine du repo cloné
echo "FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
# .env est gitignoré, donc jamais commité
```

### Budget Firecrawl dans scope.yaml

Chaque mission peut surcharger le budget. Dans le `scope.yaml` d'une mission :

```yaml
budget:
  firecrawl_scrapes: 60    # défaut 60 — peut être réduit/augmenté
```

Le ledger `outputs/<run_id>/firecrawl-ledger.json` trace chaque scrape (URL, verdict, credits_used). Si le budget est épuisé, fallback automatique sur WebFetch + WebSearch, tag `investigation_depth: partial` posé sur les fiches concernées.

---

## 4. Premier benchmark — test grandeur nature

### 4.1 Lancer Claude Code

Dans le dossier cloné (`ascend-bench/`), lance :

```bash
claude
```

Le stack `CLAUDE.md` se charge automatiquement (c'est le cerveau du stack — règles absolues + méthodologie).

### 4.2 Prompt de démarrage

Copie-colle dans Claude Code :

```
Benchmark-moi les solutions de RAG d'entreprise pour mutuelles santé.
Grille : scoring-grids/health-ai.json.
Mode : Standard (45-60 min, pas de red-team).
```

Le mainthread va :
1. **Charger la grille** et vérifier sa validité.
2. **Cadrage** — `benchmark-lead` agent pose 4-5 questions pour structurer la mission (cas d'usage, géographie, seuils, dealbreakers éventuels).
3. **Discovery** — dispatch de 3 `discoverer` en parallèle sur des angles différents (leaders mondiaux, FR/EU, open source).
4. **Investigation P1** — dispatch d'1 `investigator` par solution retenue (5-15 en parallèle), budget Firecrawl = 1 scrape / vendor.
5. **Scoring pondéré** — `weighted-scorer` applique la grille avec completeness_ratio.
6. **Critic** — audit interne des failles, sources faibles, biais.
7. **Consolidation** — `benchmark-lead` consolide en synthèse exécutive.
8. **Render** — `python -m lib.render outputs/<run_id>/bench.json` produit xlsx + docx dans `outputs/<run_id>/deliverables/`.

**Durée réelle** : 45-60 min pour Standard, 60-90 min pour Full avec red-team.

### 4.3 Vérifier les livrables

```bash
ls outputs/<run_id>/deliverables/
# → bench.xlsx  bench.docx
```

Ouvre le `.docx` dans Word / LibreOffice / Google Docs — la note de synthèse respecte la charte Ascend avec 11 sections (cover, sommaire, exec summary, ranking, fiches acteurs × N, critic, red-team, transverse, recommendations, sources annex, exclusions si applicable).

---

## 5. Personnalisation

### 5.1 `config/consultant.json` (identité)

Généré automatiquement par `install.sh`. Pour éditer :

```bash
nano config/consultant.json
# Exemple :
{
  "name": "Marie Dupont",
  "email": "marie.dupont@moncabinet.fr",
  "handle": "marie.dupont"
}
```

Puis ré-appliquer :

```bash
python scripts/apply_consultant_config.py config/consultant.json ~/.claude/skills ~/.claude/agents
```

Et recharger Claude Code (`claude` ou `/agents` pour recharger en session).

### 5.2 Créer ta propre grille de scoring

Copier une grille proche de ton secteur :

```bash
cp scoring-grids/enterprise-saas.json scoring-grids/ma-grille.json
nano scoring-grids/ma-grille.json
# Édite le nom, la description, les critères, les pondérations
python scripts/validate_grid.py scoring-grids/ma-grille.json
```

Format d'une grille : 5 à 10 critères, pondérations qui somment à 1.0, échelle 1-5 avec label + `requires` par niveau. Voir les 5 grilles incluses pour exemples.

### 5.3 `ascend-context.md` (optionnel, conflits d'intérêts)

Si tu veux que le stack vérifie les conflits d'intérêts (clients actifs, partenaires, concurrents) pendant le cadrage, crée un fichier `ascend-context.md` à la racine du repo (gitignoré) :

```markdown
# Contexte {ton cabinet}

## Clients actifs
- Client A, secteur santé
- Client B, secteur public

## Partenaires
- Éditeur X (partenariat depuis 2024)

## Concurrents directs
- Cabinet Y
```

Le stack le lit automatiquement en cadrage et prompte si un éditeur en conflit apparaît dans la short-list.

---

## 6. Troubleshooting

### "No skills found" dans Claude Code

```bash
ls ~/.claude/skills/
# Attendu : 6 sous-dossiers (market-scanner, vendor-deep-dive, sovereignty-analyzer, source-credibility, fact-checker, weighted-scorer)
```

Si vide, relance `bash install.sh`.

### "Firecrawl MCP not configured"

```bash
cat ~/.claude/mcp.json
# Attendu : une entrée firecrawl avec ta clé
```

Si absent, re-set la variable et relance l'installeur :
```bash
export FIRECRAWL_API_KEY=fc-xxx
bash install.sh --force
```

### Les agents ne sont pas dispatchés

Les sub-agents sont chargés au **démarrage** d'une session Claude Code. Si tu viens de lancer `install.sh` dans une session active, relance `claude` ou tape `/agents` pour recharger. Vérification : `/agents` doit lister `benchmark-lead`, `discoverer`, `investigator`, `critic`, `red-teamer`.

### `pytest` échoue

```bash
python -m pip install --upgrade pytest openpyxl python-docx pyyaml jsonschema
python -m pytest tests/ -v
# → 139 passed
```

### Budget Firecrawl épuisé

Normal si tu fais > 30 benchmarks / mois sur le plan gratuit. Upgrade `Starter` ($16/mois) ou configure un budget local plus agressif :

```yaml
# scope.yaml de la mission
budget:
  firecrawl_scrapes: 20    # au lieu de 60
```

Le fallback WebFetch + WebSearch prend automatiquement le relais avec `investigation_depth: partial`.

---

## 7. Étape suivante

- Lis **[CLAUDE.md](CLAUDE.md)** — cerveau du stack (règles absolues + méthodologie complète).
- Consulte les **[exemples](examples/)** — benchs LISI et FNMF déjà rendus.
- Explore les **[workflows](workflows/)** — market-benchmark, vendor-due-diligence, regulatory-check, pre-delivery-checklist.
- Si tu veux contribuer : **[CONTRIBUTING.md](CONTRIBUTING.md)**.
