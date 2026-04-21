"""Tests pour scripts/rescore.py.

Vérifient les 3 cas d'usage : changement de grille, révision de score,
ajout d'acteur (via édition JSON + rescore). Plus unit tests sur les
primitives (bump_version, generate_diff).
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

from rescore import (  # noqa: E402
    apply_grid_weights,
    bump_version,
    generate_diff,
    recalc_weighted_scores,
    reorder_ranking,
)

LISI_BENCH = REPO_ROOT / "examples" / "generic-demo" / "bench.json"
LISI_GRID = REPO_ROOT / "scoring-grids" / "lisi-souverainete.json"


@pytest.fixture()
def bench() -> dict:
    return json.loads(LISI_BENCH.read_text(encoding="utf-8"))


@pytest.fixture()
def grid() -> dict:
    return json.loads(LISI_GRID.read_text(encoding="utf-8"))


def test_bump_version_simple():
    assert bump_version("1.0") == "1.1"
    assert bump_version("2.0") == "2.1"
    assert bump_version("1.1.3") == "1.1.4"


def test_bump_version_with_suffix():
    assert bump_version("2.0-rc1") == "2.1-rc1"


def test_recalc_preserves_already_consistent_scores(bench):
    original = {a["id"]: a["weighted_score"] for a in bench["actors"]}
    errs = recalc_weighted_scores(bench)
    assert errs == []
    for actor in bench["actors"]:
        assert abs(actor["weighted_score"] - original[actor["id"]]) < 0.01


def test_reorder_ranking_preserves_order_after_recalc(bench, grid):
    """Recalc + reorder doit préserver l'ordre initial si aucun score n'a bougé."""
    b2 = copy.deepcopy(bench)
    recalc_weighted_scores(b2)
    reorder_ranking(b2, grid)
    # Le ranking initial est 1:acme, 2:nova, 3:hybrid, 4:legacy
    ranks = {a["id"]: a["rank"] for a in b2["actors"]}
    assert ranks["acme-cloud"] < ranks["nova-industries"]
    assert ranks["nova-industries"] < ranks["demo-hybrid"]
    assert ranks["demo-hybrid"] < ranks["sample-legacy"]


def test_apply_grid_weights_updates_scoring_weights(bench, grid):
    # Modifie la grille : mettre indep_stack à 0.30 et pertinence à 0.10
    g2 = copy.deepcopy(grid)
    for c in g2["criteria"]:
        if c["id"] == "independance_stack":
            c["weight"] = 0.30
        elif c["id"] == "pertinence_lisi":
            c["weight"] = 0.10
    # Sum doit redevenir 1.0 — on retouche les autres en conséquence (on ne teste que l'apply)
    warnings = apply_grid_weights(bench, g2)
    assert warnings == []    # tous les critères existent dans les deux

    # Vérifier qu'OVH a indep_stack à 0.30 dans scoring[]
    ovh = next(a for a in bench["actors"] if a["id"] == "acme-cloud")
    weight = next(s["weight"] for s in ovh["scoring"] if s["criterion_id"] == "independance_stack")
    assert weight == 0.30


def test_apply_grid_weights_warns_on_unknown_criterion(bench, grid):
    g2 = copy.deepcopy(grid)
    # Retire un critère de la grille pour simuler un schéma de grille changé
    g2["criteria"] = [c for c in g2["criteria"] if c["id"] != "traction_resultats"]

    warnings = apply_grid_weights(bench, g2)
    # Chaque acteur a scoring sur traction_resultats → 1 warning par acteur = 6
    assert any("traction_resultats" in w for w in warnings)


def test_generate_diff_detects_ranking_change(bench):
    old = copy.deepcopy(bench)
    new = copy.deepcopy(bench)
    # Swap ranks between #3 et #4
    a3 = next(a for a in new["actors"] if a["rank"] == 3)
    a4 = next(a for a in new["actors"] if a["rank"] == 4)
    a3["rank"], a4["rank"] = 4, 3

    diff = generate_diff(old, new)
    assert "Changements de classement" in diff
    assert a3["id"] in diff
    assert a4["id"] in diff


def test_generate_diff_detects_added_actor(bench):
    old = copy.deepcopy(bench)
    # Retirer un acteur de "old" pour simuler un ajout dans "new"
    old["actors"] = [a for a in old["actors"] if a["id"] != "acme-cloud"]
    old["sources"] = [s for s in old["sources"] if s.get("actor_ref") != "acme-cloud"]

    diff = generate_diff(old, bench)
    assert "Acteurs ajoutés" in diff
    assert "acme-cloud" in diff


def test_generate_diff_no_change(bench):
    diff = generate_diff(bench, bench)
    assert "Aucune différence" in diff
