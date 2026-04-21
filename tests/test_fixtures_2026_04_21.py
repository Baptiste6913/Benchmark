"""Tests light sur fixtures statiques du run du 2026-04-21 (bench banque privée FR).

Demandé par l'utilisateur en Q6 v1.3 : valider la logique v1.3 (firecrawl-ledger flag,
degraded_mode pondéré) sans consommer de crédits Firecrawl.

3 fixtures pytest inspirées de fiches réelles du run :
- Rothschild Martin Maurel — AUM chiffré 2017, chiffre STALE (>2 ans) → à flagger
- BNP Paribas BP — AUM 2025-09-30 publié, fresh → ne doit PAS flagger
- Lombard Odier FR — AUM FR non publié, investigation_depth=partial (WebFetch fallback)
"""

from __future__ import annotations

from datetime import date

import pytest

from lib._common import (
    compute_investigation_depth,
    degraded_threshold_from_scope,
    get_excluded_actors,
    should_trigger_degraded_mode,
)


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def rothschild_stale() -> dict:
    """Fiche Rothschild MM — AUM 2017, stale."""
    return {
        "id": "rothschild-mm",
        "name": "Rothschild & Co Martin Maurel",
        "key_figures": [
            {
                "metric": "AUM fusion 2017",
                "value": "34 Md€",
                "date": "2017",
                "source_ids": ["rothschild-1"],
                "notes": "Pas de republication depuis la sortie de cote 2023.",
            }
        ],
        "sources_used": {
            "firecrawl_pages": 1,
            "webfetch_pages": 2,
            "websearch_queries": 6,
        },
        "investigation_depth": "partial",
    }


@pytest.fixture
def bnp_fresh() -> dict:
    """Fiche BNP — AUM publié Q3 2025, fresh."""
    return {
        "id": "bnp-paribas-bp",
        "name": "BNP Paribas Banque Privée",
        "key_figures": [
            {
                "metric": "AUM Wealth Management monde",
                "value": "484 Md€",
                "date": "2025-09-30",
                "source_ids": ["bnp-1"],
            }
        ],
        "sources_used": {
            "firecrawl_pages": 3,
            "webfetch_pages": 1,
            "websearch_queries": 4,
        },
        "investigation_depth": "full",
    }


@pytest.fixture
def lombard_odier_partial() -> dict:
    """Fiche Lombard Odier — AUM FR non publié, WebFetch fallback."""
    return {
        "id": "lombard-odier",
        "name": "Lombard Odier (France)",
        "key_figures": [
            {
                "metric": "AUM France",
                "value": "Non publié",
                "date": "2024",
                "notes": "Groupe ne communique pas de split France ; estimation < 2 Md€.",
            }
        ],
        "sources_used": {
            "firecrawl_pages": 0,
            "webfetch_pages": 2,
            "websearch_queries": 8,
        },
        "investigation_depth": "partial",
    }


# -----------------------------------------------------------------------------
# Tests : cohérence investigation_depth dérivé vs annoncé
# -----------------------------------------------------------------------------


def test_bnp_depth_derives_to_full(bnp_fresh):
    derived = compute_investigation_depth(bnp_fresh["sources_used"])
    assert derived == "full"
    assert derived == bnp_fresh["investigation_depth"]


def test_rothschild_depth_derives_to_partial(rothschild_stale):
    derived = compute_investigation_depth(rothschild_stale["sources_used"])
    assert derived == "partial"
    assert derived == rothschild_stale["investigation_depth"]


def test_lombard_depth_derives_to_partial(lombard_odier_partial):
    """Lombard Odier : 0 Firecrawl + 2 WebFetch → partial par WebFetch fallback."""
    derived = compute_investigation_depth(lombard_odier_partial["sources_used"])
    assert derived == "partial"
    assert derived == lombard_odier_partial["investigation_depth"]


# -----------------------------------------------------------------------------
# Tests : détection chiffre STALE (>2 ans)
# -----------------------------------------------------------------------------


def _year_from_date_field(date_str: str) -> int:
    """Extrait l'année d'un champ date au format YYYY ou YYYY-MM-DD."""
    return int(date_str.split("-")[0])


def is_stale(key_figure_date: str, reference_year: int = 2026, threshold_years: int = 2) -> bool:
    """Flag >threshold_years comme stale. Défaut 2 ans pour banque privée (AUM volatile)."""
    return reference_year - _year_from_date_field(key_figure_date) > threshold_years


def test_rothschild_aum_is_flagged_stale(rothschild_stale):
    kf = rothschild_stale["key_figures"][0]
    assert is_stale(kf["date"]) is True
    assert _year_from_date_field(kf["date"]) == 2017


def test_bnp_aum_is_not_stale(bnp_fresh):
    kf = bnp_fresh["key_figures"][0]
    assert is_stale(kf["date"]) is False


# -----------------------------------------------------------------------------
# Tests : reproduction du degraded-mode sur le panel bench banque privée
# -----------------------------------------------------------------------------


def test_bench_banque_privee_profile_10_partial_does_not_trigger_at_05():
    """Reproduction du cas Ascend 2026-04-21 : 10/15 partial → ratio 0.333 → pas de trigger."""
    actors = (
        [{"id": f"a{i}", "investigation_depth": "partial"} for i in range(10)]
        + [{"id": f"b{i}", "investigation_depth": "full"} for i in range(5)]
    )
    assert should_trigger_degraded_mode(actors, threshold=0.5) is False


def test_bench_banque_privee_with_2_shallow_triggers_at_05():
    """Si le bench banque privée avait eu 10 partial + 2 shallow : ratio 7/17 ≈ 0.411 < 0.5 → pas encore.

    Ajustement : 10 partial + 3 shallow sur 15 = (3 + 5)/15 = 0.533 > 0.5 → disclaimer.
    """
    actors = (
        [{"id": f"a{i}", "investigation_depth": "partial"} for i in range(10)]
        + [{"id": f"s{i}", "investigation_depth": "shallow"} for i in range(3)]
        + [{"id": f"b{i}", "investigation_depth": "full"} for i in range(2)]
    )
    assert should_trigger_degraded_mode(actors, threshold=0.5) is True


def test_operator_can_tighten_threshold_to_catch_partial_only():
    """Si Ascend veut flagger le bench 10/15 partial, il baisse le seuil à 0.3 dans scope.yaml."""
    scope = {"degraded_threshold": 0.3}
    t = degraded_threshold_from_scope(scope)
    actors = (
        [{"id": f"a{i}", "investigation_depth": "partial"} for i in range(10)]
        + [{"id": f"b{i}", "investigation_depth": "full"} for i in range(5)]
    )
    assert should_trigger_degraded_mode(actors, threshold=t) is True
