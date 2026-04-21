"""Item 3 du hotfix — le validator de grille émet un warning (pas une erreur)
quand un critère n'a pas de `label_fr`.

Rétrocompat : les 3 grilles existantes (enterprise-saas, health-ai,
regulated-industries) n'ont pas encore été migrées. Elles passent toujours
la validation, mais génèrent des warnings.
"""

from __future__ import annotations

import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

from validate_grid import cross_check_grid, lint_grid  # noqa: E402


def _minimal_grid(with_label_fr: bool = False) -> dict:
    critereon = {
        "id": "crit_a",
        "name": "Critere A",
        "weight": 1.0,
        "scale": [
            {"value": i, "label": f"Level {i}"} for i in range(1, 6)
        ],
    }
    if with_label_fr:
        critereon["label_fr"] = "Critère A accentué"
    return {
        "name": "test-grid",
        "version": "1.0",
        "criteria": [critereon],
    }


def test_lint_warns_on_missing_label_fr() -> None:
    grid = _minimal_grid(with_label_fr=False)
    warnings = lint_grid(grid)
    assert len(warnings) == 1
    assert "label_fr" in warnings[0]
    assert "crit_a" in warnings[0]


def test_lint_quiet_when_label_fr_present() -> None:
    grid = _minimal_grid(with_label_fr=True)
    warnings = lint_grid(grid)
    assert warnings == []


def test_lint_is_not_blocking() -> None:
    """Un grid sans label_fr doit passer cross_check_grid (pas d'erreur bloquante)."""
    grid = _minimal_grid(with_label_fr=False)
    errors = cross_check_grid(grid)
    assert errors == [], f"Ne doit pas bloquer, a reçu : {errors}"


def test_lisi_grid_has_label_fr_on_all_criteria() -> None:
    """La grille LISI doit avoir label_fr sur chaque critère (post hotfix item 3)."""
    grid_path = REPO_ROOT / "scoring-grids" / "lisi-souverainete.json"
    grid = json.loads(grid_path.read_text(encoding="utf-8"))
    warnings = lint_grid(grid)
    assert warnings == [], (
        "La grille LISI doit avoir label_fr sur tous ses critères :\n  - "
        + "\n  - ".join(warnings)
    )


def test_other_grids_still_validate_without_label_fr() -> None:
    """Rétrocompat : les grilles non migrées doivent toujours valider sans erreur."""
    for grid_name in ("enterprise-saas.json", "health-ai.json", "regulated-industries.json"):
        path = REPO_ROOT / "scoring-grids" / grid_name
        grid = json.loads(path.read_text(encoding="utf-8"))
        errors = cross_check_grid(grid)
        assert errors == [], f"{grid_name} casse la validation : {errors}"
        # Warnings sont OK (migration en cours)
