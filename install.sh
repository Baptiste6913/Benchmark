#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Ascend Research Stack — installer (Linux / macOS / Git Bash Windows)
# ------------------------------------------------------------------------------
# Installe :
#   - les skills et agents custom du stack
#   - les skills externes Weizhena/Deep-Research-skills
#   - les skills externes 199-biotechnologies/claude-deep-research-skill
#   - la dépendance Python pyyaml
# ------------------------------------------------------------------------------

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { printf "${BLUE}[install]${NC} %s\n" "$*"; }
ok()   { printf "${GREEN}[ ok  ]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[warn ]${NC} %s\n" "$*"; }
die()  { printf "${RED}[fail ]${NC} %s\n" "$*" >&2; exit 1; }

# ---- CLI args ---------------------------------------------------------------
DRY_RUN=0
FORCE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --force)   FORCE=1;   shift ;;
    --help|-h)
      cat <<HELP
Usage: $0 [--dry-run] [--force]
  --dry-run   Affiche ce qui changerait sur ~/.claude/ sans écrire.
  --force     Écrase les fichiers user modifiés (backup .bak en silence).
              Sans --force, un prompt [k/o/b] s'affiche par fichier modifié.
              En mode non-interactive (pipe/CI), les fichiers modifiés sont
              conservés et l'installeur signale le cas (code retour 2).
  --help      Affiche cette aide.
HELP
      exit 0 ;;
    *) die "Unknown option: $1 (try --help)" ;;
  esac
done

if [[ $DRY_RUN -eq 1 ]]; then
  warn "Mode --dry-run : aucune écriture sur ~/.claude/. Les prérequis et le git clone temp s'exécutent normalement."
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_HOME/skills"
AGENTS_DIR="$CLAUDE_HOME/agents"
TMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'ascend-research-stack')"

# smart_copy <src_dir> <dest_dir>  — wrappe scripts/install_helpers.py
smart_copy() {
  local src="$1" dest="$2"
  local opts=""
  [[ $DRY_RUN -eq 1 ]] && opts="$opts --dry-run"
  [[ $FORCE   -eq 1 ]] && opts="$opts --force"
  local pybin
  pybin="$(command -v python3 || command -v python || true)"
  [[ -z "$pybin" ]] && die "Python introuvable — requis pour la copie non destructive."
  # On ne fait pas die sur exit code 2 (= fichiers user conservés) pour que l'install continue.
  "$pybin" "$REPO_ROOT/scripts/install_helpers.py" smart-copy $opts "$src" "$dest" \
    || {
      local rc=$?
      [[ $rc -eq 2 ]] && warn "smart_copy $src: certains fichiers user conservés (utiliser --force pour les écraser)." \
                    || warn "smart_copy $src: échec (code $rc)."
    }
}

cleanup() {
  if [[ -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

# ------------------------------------------------------------------------------
# 1. Prérequis
# ------------------------------------------------------------------------------
log "Vérification des prérequis..."

command -v git    >/dev/null 2>&1 || die "git n'est pas installé."
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 \
  || die "python (3.x) n'est pas installé."

if command -v claude >/dev/null 2>&1; then
  ok "Claude Code détecté : $(claude --version 2>/dev/null || echo 'version inconnue')"
else
  warn "Claude Code non détecté dans le PATH. Installe-le depuis https://claude.com/claude-code."
fi

mkdir -p "$SKILLS_DIR" "$AGENTS_DIR"
ok "Répertoires Claude prêts : $CLAUDE_HOME"

# ------------------------------------------------------------------------------
# 1bis. Config consultant (nom, email, handle)
# ------------------------------------------------------------------------------
CONFIG_FILE="$REPO_ROOT/config/consultant.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
  log "Première installation : configuration du consultant."
  DEFAULT_NAME="$(git -C "$REPO_ROOT" config user.name 2>/dev/null || echo '')"
  DEFAULT_EMAIL="$(git -C "$REPO_ROOT" config user.email 2>/dev/null || echo '')"

  if [[ -t 0 ]]; then
    read -r -p "Nom du consultant [${DEFAULT_NAME}] : " _CN || true
    read -r -p "Email [${DEFAULT_EMAIL}] : " _CE || true
    read -r -p "Handle (optionnel) : " _CH || true
  fi
  _CN="${_CN:-$DEFAULT_NAME}"
  _CE="${_CE:-$DEFAULT_EMAIL}"
  _CH="${_CH:-}"

  if [[ -z "$_CN" || -z "$_CE" ]]; then
    warn "Nom ou email vide — config consultant non créée. Le stack sera installé avec les placeholders {{CONSULTANT_*}} non substitués."
    warn "Pour corriger plus tard : copier config/consultant.example.json → config/consultant.json, puis rejouer install.sh."
  elif [[ $DRY_RUN -eq 1 ]]; then
    log "[dry-run] WOULD WRITE $CONFIG_FILE"
  else
    mkdir -p "$REPO_ROOT/config"
    cat > "$CONFIG_FILE" <<JSON
{
  "consultant_name": "$_CN",
  "consultant_email": "$_CE",
  "consultant_handle": "$_CH"
}
JSON
    ok "Config consultant créée : $CONFIG_FILE"
  fi
else
  ok "Config consultant existe déjà : $CONFIG_FILE"
fi

# ------------------------------------------------------------------------------
# 2. Skills externes
# ------------------------------------------------------------------------------
log "Clonage des skills externes..."

git clone --depth 1 https://github.com/Weizhena/Deep-Research-skills.git \
  "$TMP_DIR/deep-research-skills" >/dev/null 2>&1 \
  || warn "Clonage Deep-Research-skills échoué (continuer sans)."

git clone --depth 1 https://github.com/199-biotechnologies/claude-deep-research-skill.git \
  "$TMP_DIR/claude-deep-research-skill" >/dev/null 2>&1 \
  || warn "Clonage claude-deep-research-skill échoué (continuer sans)."

if [[ -d "$TMP_DIR/deep-research-skills/skills" ]]; then
  smart_copy "$TMP_DIR/deep-research-skills/skills" "$SKILLS_DIR"
  ok "Deep-Research-skills installé."
elif [[ -d "$TMP_DIR/deep-research-skills" ]]; then
  smart_copy "$TMP_DIR/deep-research-skills" "$SKILLS_DIR/deep-research-skills"
  ok "Deep-Research-skills installé (structure alternative)."
fi

if [[ -d "$TMP_DIR/claude-deep-research-skill/skills" ]]; then
  smart_copy "$TMP_DIR/claude-deep-research-skill/skills" "$SKILLS_DIR"
  ok "claude-deep-research-skill installé."
elif [[ -d "$TMP_DIR/claude-deep-research-skill" ]]; then
  smart_copy "$TMP_DIR/claude-deep-research-skill" "$SKILLS_DIR/claude-deep-research-skill"
  ok "claude-deep-research-skill installé (structure alternative)."
fi

# ------------------------------------------------------------------------------
# 3. Skills custom Ascend
# ------------------------------------------------------------------------------
log "Installation des skills custom Ascend..."
if [[ -d "$REPO_ROOT/skills" ]]; then
  smart_copy "$REPO_ROOT/skills" "$SKILLS_DIR"
  ok "Skills custom traités (voir stats ci-dessus)."
else
  die "Dossier skills/ introuvable dans $REPO_ROOT"
fi

# ------------------------------------------------------------------------------
# 4. Agents custom Ascend
# ------------------------------------------------------------------------------
log "Installation des agents custom Ascend..."
if [[ -d "$REPO_ROOT/agents" ]]; then
  smart_copy "$REPO_ROOT/agents" "$AGENTS_DIR"
  ok "Agents custom traités (voir stats ci-dessus)."
else
  warn "Dossier agents/ introuvable, skip."
fi

# ------------------------------------------------------------------------------
# 4bis. Application de la config consultant aux copies installées
# ------------------------------------------------------------------------------
if [[ $DRY_RUN -eq 1 ]]; then
  warn "dry-run : skip application config consultant."
elif [[ -f "$CONFIG_FILE" ]]; then
  log "Application de la config consultant aux skills et agents installés..."
  PYBIN="$(command -v python3 || command -v python)"
  if [[ -n "$PYBIN" ]]; then
    if "$PYBIN" "$REPO_ROOT/scripts/apply_consultant_config.py" \
        "$CONFIG_FILE" "$SKILLS_DIR" "$AGENTS_DIR"; then
      ok "Placeholders {{CONSULTANT_*}} substitués."
    else
      warn "Substitution consultant échouée — les fichiers installés conservent les placeholders."
    fi
  else
    warn "Python introuvable — substitution consultant skipée."
  fi
else
  warn "Pas de config/consultant.json — skills et agents installés avec placeholders {{CONSULTANT_*}}."
fi

# ------------------------------------------------------------------------------
# 5. Dépendances Python
# ------------------------------------------------------------------------------
log "Installation de pyyaml + jsonschema + openpyxl + python-docx..."
if [[ $DRY_RUN -eq 1 ]]; then
  log "[dry-run] WOULD pip install --user pyyaml jsonschema openpyxl python-docx"
else
  if command -v python3 >/dev/null 2>&1; then
    python3 -m pip install --quiet --user pyyaml jsonschema openpyxl python-docx || warn "Install dépendances Python échouée."
  else
    python -m pip install --quiet --user pyyaml jsonschema openpyxl python-docx || warn "Install dépendances Python échouée."
  fi
  ok "Dépendances Python OK (pyyaml / jsonschema / openpyxl / python-docx)."
fi

# ------------------------------------------------------------------------------
# 6. MCP Firecrawl (optionnel mais recommandé)
# ------------------------------------------------------------------------------
log "Configuration du MCP Firecrawl..."

if [[ $DRY_RUN -eq 1 ]]; then
  log "[dry-run] WOULD configure Firecrawl MCP (claude mcp add firecrawl ...)"
elif ! command -v claude >/dev/null 2>&1; then
  warn "Claude Code absent : skip config MCP Firecrawl."
else
  # pipefail est actif, on désactive localement pour tolérer l'erreur de claude mcp list
  set +e
  claude mcp list 2>/dev/null | grep -q 'firecrawl'
  _fc_already_configured=$?
  set -e

  if [[ $_fc_already_configured -eq 0 ]]; then
    ok "MCP Firecrawl déjà configuré."
  else
    FIRECRAWL_API_KEY="${FIRECRAWL_API_KEY:-}"
    if [[ -z "$FIRECRAWL_API_KEY" ]]; then
      log "Firecrawl permet aux investigator de scraper les sites éditeurs (budget 500 crédits/mois)."
      log "Inscription gratuite : https://www.firecrawl.dev"
      # Lecture interactive (tolère l'absence de TTY, ex. pipe CI)
      if [[ -t 0 ]]; then
        read -r -p "Clé Firecrawl (fc-...) ou Entrée pour skip : " FIRECRAWL_API_KEY || true
      fi
    fi

    if [[ -n "${FIRECRAWL_API_KEY:-}" ]]; then
      if claude mcp add --scope user firecrawl \
          -e "FIRECRAWL_API_KEY=$FIRECRAWL_API_KEY" \
          -- npx -y firecrawl-mcp >/dev/null 2>&1; then
        ok "MCP Firecrawl ajouté (scope user)."
      else
        warn "Échec ajout MCP Firecrawl, à faire manuellement (voir commande ci-dessous)."
      fi
    else
      warn "Clé Firecrawl non fournie. Investigator fonctionnera en mode dégradé (WebFetch seul)."
      warn "Pour l'ajouter plus tard :"
      warn "  claude mcp add --scope user firecrawl \\"
      warn "    -e FIRECRAWL_API_KEY=fc-xxx -- npx -y firecrawl-mcp"
    fi
  fi
fi

# ------------------------------------------------------------------------------
# 7. Résumé
# ------------------------------------------------------------------------------
cat <<EOF

${GREEN}-------------------------------------------------------------------${NC}
${GREEN}  Ascend Research Stack installé avec succès.${NC}
${GREEN}-------------------------------------------------------------------${NC}

Skills installés     : $SKILLS_DIR
Agents installés     : $AGENTS_DIR

Next steps :
  1. cd $REPO_ROOT
  2. claude
  3. Dans Claude Code, essaie :
       "Benchmark-moi les solutions de RAG d'entreprise, grille health-ai"
     ou :
       "@prompts/benchmark-full.md"

Documentation :
  - README.md      : vue d'ensemble
  - CLAUDE.md      : règles et méthodologie (chargé auto par Claude Code)
  - workflows/     : pas-à-pas par type de mission
  - scoring-grids/ : grilles JSON prêtes à l'emploi

Bon benchmarking.
EOF
