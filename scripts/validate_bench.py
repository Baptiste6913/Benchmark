"""Valide un bench.json contre schemas/bench.schema.json.

Usage:
    python scripts/validate_bench.py <bench.json> [<schema.json>]

Si le second argument est omis, utilise schemas/bench.schema.json du repo.

Exit codes:
    0  valide
    1  invalide (avec détail des erreurs)
    2  fichier introuvable / JSON mal formé

Règles supplémentaires au-delà du schéma:
    - Somme des scoring[].weight de chaque acteur doit être proche de 1.0 (±0.01),
      SI les weights sont fournis (ils sont optionnels dans le schéma).
    - Chaque source_id référencé dans les acteurs doit exister dans sources[].
    - Chaque actor_id dans exec_summary.ranking / red_team.verdicts /
      red_team.details_per_actor / critic_item.actor_ref doit exister dans actors[].
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
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "bench.schema.json"


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


def check_cross_refs(bench: dict) -> list[str]:
    errors = []
    actor_ids = {a["id"] for a in bench.get("actors", [])}
    source_ids = {s["id"] for s in bench.get("sources", []) if isinstance(s, dict)}

    # actor_id referenced anywhere
    def check_actor_ref(value: str, where: str):
        if value and value != "global" and value not in actor_ids:
            errors.append(f"actor_ref '{value}' introuvable dans actors[] ({where})")

    # exec_summary.ranking
    for i, row in enumerate(bench.get("exec_summary", {}).get("ranking", []) or []):
        check_actor_ref(row.get("actor_id", ""), f"exec_summary.ranking[{i}]")

    # red_team.verdicts
    for aid in (bench.get("red_team") or {}).get("verdicts", {}) or {}:
        if aid not in actor_ids:
            errors.append(f"actor_id '{aid}' dans red_team.verdicts introuvable dans actors[]")

    # red_team.details_per_actor
    for aid in (bench.get("red_team") or {}).get("details_per_actor", {}) or {}:
        if aid not in actor_ids:
            errors.append(f"actor_id '{aid}' dans red_team.details_per_actor introuvable dans actors[]")

    # critic items
    for section in ("blocking", "warnings", "observations"):
        for i, item in enumerate((bench.get("critic") or {}).get(section, []) or []):
            ar = item.get("actor_ref")
            if ar:
                check_actor_ref(ar, f"critic.{section}[{i}]")

    # source_ids inside actors
    for actor in bench.get("actors", []):
        for field in ("key_figures", "scoring"):
            for i, item in enumerate(actor.get(field, []) or []):
                for sid in item.get("source_ids", []) or []:
                    if sid not in source_ids:
                        errors.append(f"source_id '{sid}' introuvable dans sources[] (actor={actor['id']}, field={field}[{i}])")
        if actor.get("flagship_quote"):
            fq_sid = actor["flagship_quote"].get("source_id")
            if fq_sid and fq_sid not in source_ids:
                errors.append(f"source_id '{fq_sid}' introuvable dans sources[] (actor={actor['id']}, flagship_quote)")

    # weight sum per actor (si weights fournis)
    for actor in bench.get("actors", []):
        weights = [c.get("weight") for c in actor.get("scoring", []) if c.get("weight") is not None]
        if weights:
            total = sum(weights)
            if abs(total - 1.0) > 0.01:
                errors.append(f"somme des weights pour actor {actor['id']} = {total:.3f} (attendu ≈ 1.0)")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    bench_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_SCHEMA

    bench = load_json(bench_path)
    schema = load_json(schema_path)

    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(bench), key=lambda e: list(e.absolute_path))

    if schema_errors:
        print(f"[fail] {bench_path} — {len(schema_errors)} erreur(s) de schéma :", file=sys.stderr)
        for err in schema_errors:
            path = ".".join(str(p) for p in err.absolute_path) or "<root>"
            print(f"  - {path}: {err.message}", file=sys.stderr)

    cross_errors = check_cross_refs(bench if isinstance(bench, dict) else {})
    if cross_errors:
        print(f"[fail] {bench_path} — {len(cross_errors)} erreur(s) de références croisées :", file=sys.stderr)
        for err in cross_errors:
            print(f"  - {err}", file=sys.stderr)

    if schema_errors or cross_errors:
        return 1

    actors = bench.get("actors", []) if isinstance(bench, dict) else []
    sources = bench.get("sources", []) if isinstance(bench, dict) else []
    mode = (bench.get("meta") or {}).get("mode", "?") if isinstance(bench, dict) else "?"
    print(f"[ ok ] {bench_path} conforme au schéma — mode={mode}, {len(actors)} acteur(s), {len(sources)} source(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
