"""Substitue les placeholders {{CONSULTANT_*}} dans un dossier cible.

Appelé par install.sh / install.bat après la copie des skills et agents dans
~/.claude/. Le repo lui-même conserve les placeholders ; seule la copie
installée est personnalisée.

Usage:
    python scripts/apply_consultant_config.py <config_json> <target_dir> [target_dir...]

Exemple:
    python scripts/apply_consultant_config.py config/consultant.json \\
        ~/.claude/skills ~/.claude/agents

Placeholders remplacés:
    {{CONSULTANT_NAME}}   -> config["consultant_name"]
    {{CONSULTANT_EMAIL}}  -> config["consultant_email"]
    {{CONSULTANT_HANDLE}} -> config["consultant_handle"]

Règles:
- Ne touche qu'aux fichiers .md, .json, .txt (évite binaires).
- Idempotent : si un fichier n'a plus de placeholder, il est ignoré.
- Affiche un résumé à la fin (fichiers modifiés / ignorés).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLACEHOLDERS = ("{{CONSULTANT_NAME}}", "{{CONSULTANT_EMAIL}}", "{{CONSULTANT_HANDLE}}")
MAP_KEYS = {
    "{{CONSULTANT_NAME}}": "consultant_name",
    "{{CONSULTANT_EMAIL}}": "consultant_email",
    "{{CONSULTANT_HANDLE}}": "consultant_handle",
}
EXTS = {".md", ".json", ".txt"}


def load_config(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    missing = [k for k in ("consultant_name", "consultant_email") if not data.get(k)]
    if missing:
        sys.exit(f"[fail] Champs obligatoires manquants dans {path}: {missing}")
    # handle est optionnel
    data.setdefault("consultant_handle", "")
    return data


def substitute_in_text(text: str, cfg: dict[str, str]) -> tuple[str, int]:
    replaced = 0
    for ph in PLACEHOLDERS:
        if ph in text:
            value = cfg.get(MAP_KEYS[ph], "")
            count = text.count(ph)
            text = text.replace(ph, value)
            replaced += count
    return text, replaced


def process_file(path: Path, cfg: dict[str, str]) -> int:
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return 0
    new_text, n = substitute_in_text(original, cfg)
    if n > 0 and new_text != original:
        path.write_text(new_text, encoding="utf-8")
    return n


def walk_and_substitute(root: Path, cfg: dict[str, str]) -> tuple[int, int]:
    modified = 0
    total_subs = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        n = process_file(path, cfg)
        if n:
            modified += 1
            total_subs += n
    return modified, total_subs


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    config_path = Path(sys.argv[1])
    targets = [Path(p).expanduser() for p in sys.argv[2:]]

    if not config_path.exists():
        sys.exit(f"[fail] Config introuvable: {config_path}")

    cfg = load_config(config_path)
    print(f"[apply] Consultant: {cfg['consultant_name']} <{cfg['consultant_email']}>")

    grand_total_files = 0
    grand_total_subs = 0
    for target in targets:
        if not target.exists():
            print(f"[warn] Cible inexistante, skip: {target}")
            continue
        n_files, n_subs = walk_and_substitute(target, cfg)
        print(f"[apply] {target}: {n_files} fichier(s) modifié(s), {n_subs} substitution(s)")
        grand_total_files += n_files
        grand_total_subs += n_subs

    print(f"[ ok ] Total: {grand_total_files} fichier(s), {grand_total_subs} substitution(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
