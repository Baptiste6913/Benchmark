"""Helpers Python pour install.sh / install.bat — copie non destructive.

Commandes:
    smart-copy SRC DEST [--dry-run] [--force] [--no-interactive]

Comportement smart-copy:
    - Fichier destination absent         → création.
    - Fichier destination identique (hash SHA-256) → skip.
    - Fichier destination différent:
        * --dry-run       : log WOULD OVERWRITE, aucune écriture
        * --force         : backup .bak + overwrite sans demander
        * sinon (TTY)     : prompt [k]eep / [o]verwrite / [b]ackup-and-overwrite
        * sinon (no TTY)  : keep + warn + exit code non-zéro en fin si ≥1 fichier conservé

Usage depuis installeur:
    python scripts/install_helpers.py smart-copy \\
        path/to/repo/skills  ~/.claude/skills  [--dry-run|--force]
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


EXCLUDE_DIR_NAMES = {".git", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".vscode"}
EXCLUDE_FILE_PATTERNS = (".DS_Store", "Thumbs.db", "desktop.ini")


def is_excluded(path: Path, src_root: Path) -> bool:
    """Exclut les dossiers infra (.git, __pycache__, etc.) et fichiers OS junk."""
    try:
        rel = path.relative_to(src_root)
    except ValueError:
        return False
    for part in rel.parts:
        if part in EXCLUDE_DIR_NAMES:
            return True
    if path.name in EXCLUDE_FILE_PATTERNS:
        return True
    return False


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class CopyStats:
    created: int = 0
    updated: int = 0
    kept: int = 0
    backed_up: int = 0
    identical: int = 0
    prompts: list[str] = field(default_factory=list)

    def summary(self, name: str) -> str:
        return (
            f"[stats] {name}: created={self.created} updated={self.updated} "
            f"kept={self.kept} backed_up={self.backed_up} identical={self.identical}"
        )


def prompt_choice(dest_file: Path) -> str:
    """Ask user what to do. Returns 'k', 'o', or 'b'. Default 'k'."""
    print(f"\n[conflict] Fichier modifié côté user : {dest_file}")
    try:
        raw = input("  [k]eep / [o]verwrite / [b]ackup-and-overwrite (default k) : ")
    except (EOFError, KeyboardInterrupt):
        return "k"
    raw = raw.strip().lower()
    if raw in ("o", "overwrite"):
        return "o"
    if raw in ("b", "backup", "backup-and-overwrite"):
        return "b"
    return "k"


def backup_path(dest_file: Path) -> Path:
    return dest_file.with_name(dest_file.name + ".bak")


def smart_copy(
    src: Path,
    dest: Path,
    *,
    dry_run: bool,
    force: bool,
    interactive: bool,
) -> CopyStats:
    stats = CopyStats()

    for src_file in src.rglob("*"):
        if not src_file.is_file():
            continue
        if is_excluded(src_file, src):
            continue
        rel = src_file.relative_to(src)
        dest_file = dest / rel

        if not dest_file.exists():
            if dry_run:
                print(f"[dry-run] CREATE {dest_file}")
            else:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
            stats.created += 1
            continue

        # dest exists
        if file_hash(src_file) == file_hash(dest_file):
            stats.identical += 1
            continue

        # differ
        if dry_run:
            print(f"[dry-run] WOULD OVERWRITE (user-modified) {dest_file}")
            stats.updated += 1
            continue

        if force:
            bkp = backup_path(dest_file)
            shutil.copy2(dest_file, bkp)
            shutil.copy2(src_file, dest_file)
            stats.backed_up += 1
            stats.updated += 1
            print(f"[force] overwritten with backup: {dest_file} (backup: {bkp.name})")
            continue

        if interactive and sys.stdin.isatty():
            choice = prompt_choice(dest_file)
            if choice == "o":
                shutil.copy2(src_file, dest_file)
                stats.updated += 1
                print(f"[ok] overwritten: {dest_file}")
            elif choice == "b":
                bkp = backup_path(dest_file)
                shutil.copy2(dest_file, bkp)
                shutil.copy2(src_file, dest_file)
                stats.backed_up += 1
                stats.updated += 1
                print(f"[ok] overwritten with backup: {dest_file} (backup: {bkp.name})")
            else:
                stats.kept += 1
                stats.prompts.append(str(dest_file))
                print(f"[kept] user version preserved: {dest_file}")
        else:
            stats.kept += 1
            stats.prompts.append(str(dest_file))
            print(
                f"[warn] no TTY, keeping user-modified file "
                f"(use --force to overwrite): {dest_file}"
            )

    return stats


def cmd_smart_copy(args: argparse.Namespace) -> int:
    src = Path(args.src).resolve()
    dest = Path(args.dest).expanduser().resolve()

    if not src.exists():
        print(f"[fail] source introuvable: {src}", file=sys.stderr)
        return 1

    if not args.dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    stats = smart_copy(
        src,
        dest,
        dry_run=args.dry_run,
        force=args.force,
        interactive=not args.no_interactive,
    )
    print(stats.summary(src.name))
    # Exit code non-zéro si des fichiers user ont été conservés malgré le conflit,
    # en mode non-interactive sans --force : signale à l'installeur.
    if stats.kept and not args.force and (args.no_interactive or not sys.stdin.isatty()):
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ascend-Bench install helpers")
    sub = p.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("smart-copy", help="Copie récursive non destructive")
    sc.add_argument("src")
    sc.add_argument("dest")
    sc.add_argument("--dry-run", action="store_true")
    sc.add_argument("--force", action="store_true")
    sc.add_argument("--no-interactive", action="store_true")
    sc.set_defaults(func=cmd_smart_copy)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
