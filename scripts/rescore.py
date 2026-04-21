"""Recalcule un bench après changement de grille ou révision de scores.

Trois modes d'usage :

1. Changement de grille (poids modifiés) :
    python scripts/rescore.py <bench.json> --new-grid <grid.json> --output <new.json>

   Applique les poids de la nouvelle grille à chaque actors[].scoring[] (sur
   la base de criterion_id), recalcule weighted_score, re-classe les acteurs
   selon les tie_breakers de la nouvelle grille, bump meta.version.

2. Révision manuelle de scores (l'utilisateur a déjà édité bench.json) :
    python scripts/rescore.py <bench.json> --output <new.json>

   Recalcule les weighted_score à partir des scoring[] existants et re-classe.

3. Diff entre deux versions :
    python scripts/rescore.py <new.json> --diff-against <old.json>

   Génère un DIFF.md à côté de <new.json>. Non destructif.

Flag `--render` : déclenche lib/render.render_all pour regénérer xlsx + docx.

Exit codes:
    0  succès
    1  erreur de règle (weights ne somment pas à 1, criterion inconnu, etc.)
    2  fichier introuvable / JSON mal formé
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[fail] fichier introuvable : {path}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as e:
        print(f"[fail] JSON mal formé : {path}\n  {e}", file=sys.stderr)
        raise SystemExit(2)


def dump_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# -----------------------------------------------------------------------------
# Rescore core
# -----------------------------------------------------------------------------


def apply_grid_weights(bench: dict, grid: dict) -> list[str]:
    """Applique les poids `grid.criteria[].weight` aux `actors[].scoring[].weight`.

    Retourne la liste des warnings (critères manquants, etc.).
    """
    warnings = []
    weight_by_id = {c["id"]: c["weight"] for c in grid.get("criteria", [])}
    allowed_ids = set(weight_by_id.keys())

    for actor in bench.get("actors", []):
        actor_rows = actor.get("scoring", [])
        existing_ids = {row.get("criterion_id") for row in actor_rows}

        for row in actor_rows:
            cid = row.get("criterion_id")
            if cid not in weight_by_id:
                warnings.append(
                    f"acteur '{actor.get('id')}' score sur critère '{cid}' absent de la nouvelle grille — ignoré"
                )
                row["weight"] = 0.0
            else:
                row["weight"] = weight_by_id[cid]

        missing = allowed_ids - existing_ids
        if missing:
            warnings.append(
                f"acteur '{actor.get('id')}' manque un score sur critères {sorted(missing)} — ajouter à la main"
            )

    return warnings


def recalc_weighted_scores(bench: dict) -> list[str]:
    errs = []
    for actor in bench.get("actors", []):
        rows = actor.get("scoring", [])
        total_w = sum(r.get("weight", 0) or 0 for r in rows)
        if abs(total_w - 1.0) > 0.01:
            errs.append(f"acteur '{actor.get('id')}' : sum(weights)={total_w:.3f} (attendu 1.0)")
            continue
        actor["weighted_score"] = round(
            sum((r.get("score") or 0) * (r.get("weight") or 0) for r in rows),
            4,
        )
    return errs


def reorder_ranking(bench: dict, grid: dict) -> None:
    """Re-classe les acteurs selon weighted_score puis tie_breakers.

    Met à jour actors[].rank et exec_summary.ranking.
    """
    tie_criteria = [t["criterion"] for t in (grid.get("tie_breakers") or []) if t.get("criterion")]

    def score_for(actor: dict, cid: str) -> float:
        for row in actor.get("scoring", []):
            if row.get("criterion_id") == cid:
                return float(row.get("score") or 0)
        return 0.0

    def sort_key(actor: dict):
        # Desc sur weighted_score puis desc sur chaque tie_breaker
        return tuple(
            [-float(actor.get("weighted_score") or 0)]
            + [-score_for(actor, cid) for cid in tie_criteria]
        )

    sorted_actors = sorted(bench.get("actors", []), key=sort_key)
    for i, actor in enumerate(sorted_actors, start=1):
        actor["rank"] = i

    # Met à jour exec_summary.ranking
    exec_ = bench.setdefault("exec_summary", {})
    exec_["ranking"] = [
        {
            "rank": a["rank"],
            "actor_id": a["id"],
            "weighted_score": round(float(a.get("weighted_score") or 0), 2),
            "positioning": a.get("positioning_one_liner")
            or (a.get("tldr") or {}).get("positioning", ""),
        }
        for a in sorted_actors
    ]


def bump_version(version: str) -> str:
    """Incrémente la version du bench : '2.0' → '2.1', '1.1.0' → '1.1.1', fallback +1."""
    m = re.match(r"^(\d+(?:\.\d+)*)(.*)$", version.strip())
    if not m:
        return f"{version}+1"
    parts = [int(p) for p in m.group(1).split(".")]
    suffix = m.group(2)
    parts[-1] += 1
    return ".".join(str(p) for p in parts) + suffix


# -----------------------------------------------------------------------------
# DIFF
# -----------------------------------------------------------------------------


def generate_diff(old_bench: dict, new_bench: dict) -> str:
    """Construit un DIFF.md markdown comparant deux versions."""
    lines = ["# Diff de bench", ""]

    # Meta
    old_meta = old_bench.get("meta", {})
    new_meta = new_bench.get("meta", {})
    lines.append("## Meta")
    lines.append("")
    lines.append(f"- version : `{old_meta.get('version', '?')}` → `{new_meta.get('version', '?')}`")
    lines.append(f"- date    : `{old_meta.get('date', '?')}` → `{new_meta.get('date', '?')}`")
    lines.append(f"- mode    : `{old_meta.get('mode', '?')}` → `{new_meta.get('mode', '?')}`")
    if old_bench.get("grid_ref") != new_bench.get("grid_ref"):
        lines.append(f"- grid_ref : `{old_bench.get('grid_ref')}` → `{new_bench.get('grid_ref')}`")
    lines.append("")

    # Actors add/remove
    old_ids = {a["id"] for a in old_bench.get("actors", [])}
    new_ids = {a["id"] for a in new_bench.get("actors", [])}
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    if added or removed:
        lines.append("## Acteurs ajoutés / retirés")
        lines.append("")
        if added:
            lines.append("**Ajoutés** :")
            for aid in added:
                a = next((x for x in new_bench["actors"] if x["id"] == aid), None)
                lines.append(
                    f"- `{aid}` ({a.get('name', '') if a else ''}) — rang {a.get('rank', '?') if a else '?'}, score {a.get('weighted_score', '?') if a else '?'}"
                )
        if removed:
            lines.append("")
            lines.append("**Retirés** :")
            for aid in removed:
                lines.append(f"- `{aid}`")
        lines.append("")

    # Rank & score changes (only for actors in both)
    old_by_id = {a["id"]: a for a in old_bench.get("actors", [])}
    new_by_id = {a["id"]: a for a in new_bench.get("actors", [])}
    common = sorted(old_ids & new_ids)
    ranking_changes = []
    score_changes = []
    for aid in common:
        o = old_by_id[aid]
        n = new_by_id[aid]
        o_rank, n_rank = o.get("rank"), n.get("rank")
        o_score, n_score = o.get("weighted_score"), n.get("weighted_score")
        if o_rank != n_rank:
            ranking_changes.append(f"- `{aid}` : rang {o_rank} → {n_rank}")
        if o_score != n_score:
            delta = (n_score or 0) - (o_score or 0)
            sign = "+" if delta >= 0 else ""
            score_changes.append(
                f"- `{aid}` : {o_score} → {n_score} ({sign}{delta:.2f})"
            )

    if ranking_changes:
        lines.append("## Changements de classement")
        lines.append("")
        lines.extend(ranking_changes)
        lines.append("")
    if score_changes:
        lines.append("## Changements de score pondéré")
        lines.append("")
        lines.extend(score_changes)
        lines.append("")

    # Per-criterion score changes
    per_crit_changes = []
    for aid in common:
        o = old_by_id[aid]
        n = new_by_id[aid]
        o_map = {r["criterion_id"]: r for r in o.get("scoring", [])}
        n_map = {r["criterion_id"]: r for r in n.get("scoring", [])}
        for cid in sorted(set(o_map) | set(n_map)):
            or_row = o_map.get(cid, {})
            nr_row = n_map.get(cid, {})
            if or_row.get("score") != nr_row.get("score"):
                per_crit_changes.append(
                    f"- `{aid}` / `{cid}` : score {or_row.get('score')} → {nr_row.get('score')}"
                )
            if or_row.get("weight") != nr_row.get("weight"):
                per_crit_changes.append(
                    f"- `{aid}` / `{cid}` : poids {or_row.get('weight')} → {nr_row.get('weight')}"
                )
    if per_crit_changes:
        lines.append("## Changements par critère (score / poids)")
        lines.append("")
        lines.extend(per_crit_changes)
        lines.append("")

    if not (added or removed or ranking_changes or score_changes or per_crit_changes):
        lines.append("_Aucune différence de scoring ni de panel détectée._")
        lines.append("_Seuls des champs méta (version, date) ont été mis à jour — voir section Meta ci-dessus._")
        lines.append("")

    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Rendering
# -----------------------------------------------------------------------------


def call_render_all(bench_path: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from lib.render import render_all  # noqa: E402 — import tardif pour éviter coût si pas demandé

    paths = render_all(bench_path, bench_path.parent)
    print(f"[ ok ] xlsx regénéré : {paths['xlsx']}")
    print(f"[ ok ] docx regénéré : {paths['docx']}")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(prog="rescore", description=__doc__)
    parser.add_argument("bench", help="bench.json à recalculer")
    parser.add_argument("--new-grid", help="Nouvelle grille — applique ses poids")
    parser.add_argument("--output", help="Fichier de sortie (défaut : overwrite bench)")
    parser.add_argument("--diff-against", help="Écrit DIFF.md comparant avec cette ancienne version")
    parser.add_argument("--render", action="store_true", help="Regénère xlsx + docx après rescore")
    parser.add_argument("--no-bump-version", action="store_true", help="N'incrémente pas meta.version")

    args = parser.parse_args()

    bench_path = Path(args.bench)
    bench = load_json(bench_path)
    if not isinstance(bench, dict):
        print("[fail] bench.json n'est pas un objet JSON", file=sys.stderr)
        return 2

    warnings: list[str] = []

    if args.new_grid:
        grid = load_json(Path(args.new_grid))
        warnings.extend(apply_grid_weights(bench, grid))
        # Met à jour grid_ref relatif au repo
        bench["grid_ref"] = str(Path(args.new_grid).as_posix())
        if "scoring-grids/" in bench["grid_ref"]:
            bench["grid_ref"] = "scoring-grids/" + bench["grid_ref"].split("scoring-grids/")[-1]
    else:
        # Charge la grille depuis bench.grid_ref pour les tie_breakers
        grid_ref = bench.get("grid_ref")
        if grid_ref:
            grid = load_json(REPO_ROOT / grid_ref)
        else:
            grid = {}

    errs = recalc_weighted_scores(bench)
    if errs:
        for e in errs:
            print(f"[fail] {e}", file=sys.stderr)
        return 1

    reorder_ranking(bench, grid)

    if not args.no_bump_version:
        bench.setdefault("meta", {})
        old_v = bench["meta"].get("version", "1.0")
        bench["meta"]["version"] = bump_version(old_v)
        print(f"[info] version bumpee : {old_v} -> {bench['meta']['version']}")

    for w in warnings:
        print(f"[warn] {w}")

    out_path = Path(args.output) if args.output else bench_path
    dump_json(bench, out_path)
    print(f"[ ok ] {out_path} écrit — {len(bench.get('actors', []))} acteurs reclassés.")

    # DIFF
    if args.diff_against:
        old = load_json(Path(args.diff_against))
        diff_md = generate_diff(old, bench)
        diff_path = out_path.parent / "DIFF.md"
        diff_path.write_text(diff_md, encoding="utf-8")
        print(f"[ ok ] diff écrit : {diff_path}")

    # Render
    if args.render:
        call_render_all(out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
