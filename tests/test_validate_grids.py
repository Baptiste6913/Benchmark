"""Test non-régression : toutes les grilles de scoring du repo passent le validator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_grid import cross_check_grid  # noqa: E402

GRIDS_DIR = REPO_ROOT / "scoring-grids"
SCHEMA_PATH = REPO_ROOT / "schemas" / "scoring-grid.schema.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    Draft202012Validator.check_schema(data)
    return data


def _grid_files():
    return sorted(GRIDS_DIR.glob("*.json"))


@pytest.mark.parametrize("grid_path", _grid_files(), ids=lambda p: p.name)
def test_grid_valid(grid_path: Path, schema: dict) -> None:
    with grid_path.open(encoding="utf-8") as f:
        grid = json.load(f)

    # Schéma JSON
    validator = Draft202012Validator(schema)
    errs = [e.message for e in validator.iter_errors(grid)]
    assert not errs, f"{grid_path.name} échoue au schéma :\n  - " + "\n  - ".join(errs)

    # Règles croisées
    cross = cross_check_grid(grid)
    assert not cross, f"{grid_path.name} échoue aux règles :\n  - " + "\n  - ".join(cross)


def test_discovers_at_least_one_grid() -> None:
    files = _grid_files()
    assert files, "Aucune grille trouvée dans scoring-grids/"
