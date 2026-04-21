"""Valide une grille de scoring contre schemas/scoring-grid.schema.json.

Usage:
    python scripts/validate_grid.py <grid.json> [<schema.json>]
    python scripts/validate_grid.py --all

Si `--all`, itère sur tous les `scoring-grids/*.json` du repo.

Règles complémentaires au-delà du schéma :
    - Somme des weights == 1.0 (±0.001).
    - IDs de critères uniques dans une grille.
    - Échelle 1-5 : les 5 values présentes, couvrant 1, 2, 3, 4, 5.
    - tie_breakers référencent des criterion_id existants.
    - tie_breakers.priority unique.

Exit codes:
    0  toutes valides
    1  au moins une invalide
    2  fichier introuvable / JSON mal formé
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("[fail] jsonschema non installé. Lance : python -m pip install --user jsonschema", file=sys.stderr)
    raise SystemExit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "scoring-grid.schema.json"
GRIDS_DIR = REPO_ROOT / "scoring-grids"


def load_json(path: Path) -> object:
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[fail] fichier introuvable : {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as e:
        print(f"[fail] JSON mal formé : {path}\n  {e}", file=sys.stderr)
        raise SystemExit(2)


def lint_grid(grid: dict) -> list[str]:
    """Warnings non bloquants (vs cross_check_grid qui retourne des erreurs)."""
    warnings = []
    for c in grid.get("criteria", []):
        if not c.get("label_fr"):
            warnings.append(
                f"critère '{c.get('id', '?')}' sans `label_fr` — migrez en ajoutant un libellé accentué. "
                f"Fallback sur `name` pour l'affichage."
            )
    return warnings


def cross_check_grid(grid: dict) -> list[str]:
    errors = []

    # Sum weights = 1.0 ±0.001
    weights = [c.get("weight", 0) for c in grid.get("criteria", [])]
    total = sum(weights)
    if abs(total - 1.0) > 0.001:
        errors.append(f"somme des weights = {total:.4f} (attendu exactement 1.0 ±0.001)")

    # Unique IDs
    ids = [c.get("id", "") for c in grid.get("criteria", [])]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        errors.append(f"IDs critères dupliqués : {sorted(duplicates)}")

    # Scale completeness : values 1..5 exactement
    for c in grid.get("criteria", []):
        cid = c.get("id", "?")
        scale = c.get("scale", [])
        values = sorted(s.get("value") for s in scale if "value" in s)
        if values != [1, 2, 3, 4, 5]:
            errors.append(f"critère '{cid}' : échelle incomplète ou dupliquée (trouvé {values}, attendu [1,2,3,4,5])")

    # tie_breakers : priority unique, criterion existants
    tbs = grid.get("tie_breakers", []) or []
    priorities = [t.get("priority") for t in tbs]
    if len(priorities) != len(set(priorities)):
        errors.append(f"tie_breakers : priority dupliquée dans {priorities}")
    id_set = set(ids)
    for t in tbs:
        cref = t.get("criterion")
        if cref and cref not in id_set:
            errors.append(f"tie_breaker priority={t.get('priority')} réfère à '{cref}' absent de criteria[]")

    # weight_total_check cohérent si fourni
    wtc = grid.get("weight_total_check")
    if wtc is not None and abs(wtc - total) > 0.001:
        errors.append(
            f"weight_total_check={wtc} ne correspond pas à la somme réelle {total:.4f}"
        )

    return errors


def validate_one(path: Path, schema: dict) -> bool:
    grid = load_json(path)
    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(grid), key=lambda e: list(e.absolute_path))
    cross_errors = cross_check_grid(grid) if isinstance(grid, dict) else []

    if schema_errors:
        print(f"[fail] {path.name} — {len(schema_errors)} erreur(s) de schéma :", file=sys.stderr)
        for err in schema_errors:
            p = ".".join(str(x) for x in err.absolute_path) or "<root>"
            print(f"  - {p}: {err.message}", file=sys.stderr)
    if cross_errors:
        print(f"[fail] {path.name} — {len(cross_errors)} erreur(s) de règle :", file=sys.stderr)
        for err in cross_errors:
            print(f"  - {err}", file=sys.stderr)

    if schema_errors or cross_errors:
        return False

    lint_warnings = lint_grid(grid) if isinstance(grid, dict) else []
    for w in lint_warnings:
        print(f"[warn] {path.name} — {w}", file=sys.stderr)

    n_crit = len(grid.get("criteria", [])) if isinstance(grid, dict) else 0
    print(f"[ ok ] {path.name} — {n_crit} critères, somme des poids = 1.0")
    return True


def main() -> int:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return 2

    schema_path = DEFAULT_SCHEMA
    targets: list[Path] = []

    if args[0] == "--all":
        targets = sorted(GRIDS_DIR.glob("*.json"))
        if len(args) >= 2:
            schema_path = Path(args[1])
    else:
        targets = [Path(args[0])]
        if len(args) >= 2:
            schema_path = Path(args[1])

    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)

    if not targets:
        print(f"[warn] aucune grille trouvée ({GRIDS_DIR})")
        return 0

    ok_count = 0
    for p in targets:
        if validate_one(p, schema):
            ok_count += 1
        print()

    fail_count = len(targets) - ok_count
    print(f"[total] {ok_count}/{len(targets)} grilles valides.")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
