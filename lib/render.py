"""API publique de génération des livrables Ascend-Bench.

Trois points d'entrée :
    render_xlsx(bench_json_path, out_path, grid_json_path=None)
    render_docx(bench_json_path, out_path, grid_json_path=None)
    render_all(bench_json_path, out_dir, grid_json_path=None)

Si `grid_json_path` est None, la grille est résolue depuis `bench.grid_ref`
(relatif au repo, remonte depuis bench_path).

Usage ligne de commande :
    python -m lib.render <bench.json> [--out <dir>] [--grid <grid.json>] [--only xlsx|docx]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lib._common import BenchContext
from lib._xlsx import write_xlsx


def render_xlsx(
    bench_json_path: str | Path,
    output_path: str | Path,
    grid_json_path: str | Path | None = None,
) -> Path:
    """Génère le xlsx. Retourne le chemin effectif du fichier écrit."""
    bench_path = Path(bench_json_path)
    grid_path = Path(grid_json_path) if grid_json_path else None
    out = Path(output_path)
    ctx = BenchContext.load(bench_path, grid_path)
    write_xlsx(ctx, out)
    return out


def render_docx(
    bench_json_path: str | Path,
    output_path: str | Path,
    grid_json_path: str | Path | None = None,
) -> Path:
    """Génère le docx conforme à la charte Ascend. Livré en S2.3."""
    # Import tardif pour ne pas forcer python-docx si l'utilisateur ne génère que xlsx.
    from lib._docx import write_docx

    bench_path = Path(bench_json_path)
    grid_path = Path(grid_json_path) if grid_json_path else None
    out = Path(output_path)
    ctx = BenchContext.load(bench_path, grid_path)
    write_docx(ctx, out)
    return out


def render_all(
    bench_json_path: str | Path,
    output_dir: str | Path,
    grid_json_path: str | Path | None = None,
    basename: str | None = None,
) -> dict[str, Path]:
    """Génère xlsx + docx dans output_dir. Retourne {'xlsx': path, 'docx': path}."""
    bench_path = Path(bench_json_path)
    out_dir = Path(output_dir)
    if basename:
        base = basename
    else:
        base = bench_path.stem
        if base == "bench":
            base = bench_path.parent.name or "bench"
    xlsx_path = out_dir / f"{base}.xlsx"
    docx_path = out_dir / f"{base}.docx"
    return {
        "xlsx": render_xlsx(bench_path, xlsx_path, grid_json_path),
        "docx": render_docx(bench_path, docx_path, grid_json_path),
    }


def _main() -> int:
    parser = argparse.ArgumentParser(prog="python -m lib.render", description=__doc__)
    parser.add_argument("bench", help="Chemin vers bench.json")
    parser.add_argument("--out", default=None, help="Dossier ou fichier de sortie (défaut : dossier du bench)")
    parser.add_argument("--grid", default=None, help="Grille scoring (défaut : bench.grid_ref)")
    parser.add_argument("--only", choices=["xlsx", "docx"], default=None, help="Génère un seul format")

    args = parser.parse_args()

    bench_path = Path(args.bench)
    if not bench_path.exists():
        raise SystemExit(f"[fail] bench introuvable : {bench_path}")

    out_dir = Path(args.out) if args.out else bench_path.parent

    if args.only == "xlsx":
        out_path = out_dir if out_dir.suffix == ".xlsx" else (out_dir / f"{bench_path.parent.name}.xlsx")
        render_xlsx(bench_path, out_path, args.grid)
        print(f"[ ok ] xlsx écrit : {out_path}")
    elif args.only == "docx":
        out_path = out_dir if out_dir.suffix == ".docx" else (out_dir / f"{bench_path.parent.name}.docx")
        render_docx(bench_path, out_path, args.grid)
        print(f"[ ok ] docx écrit : {out_path}")
    else:
        paths = render_all(bench_path, out_dir, args.grid)
        print(f"[ ok ] xlsx écrit : {paths['xlsx']}")
        print(f"[ ok ] docx écrit : {paths['docx']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
