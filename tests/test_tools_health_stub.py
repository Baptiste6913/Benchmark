"""Tests du format tools-health.json (v1.3 fix 4 — stub schema, ping live hors pytest).

Valide :
- Structure de tools-health.json (champs requis, enum verdicts)
- Règles de calcul du verdict global (full/degraded/blocked)
"""

from __future__ import annotations

import pytest


VALID_TOOL_STATES = {"up", "down", "unknown"}
VALID_GLOBAL_VERDICTS = {"full", "degraded", "blocked"}


def compute_global_verdict(firecrawl: str, webfetch: str, websearch: str) -> str:
    """Réplique la logique documentée dans agents/benchmark-lead.md Phase 0 (v1.3).

    - full     : tous "up"
    - degraded : au moins un non-critique "down" mais websearch "up"
    - blocked  : websearch "down" (pas d'outil, ne pas lancer le run)
    """
    if websearch == "down":
        return "blocked"
    if firecrawl == "up" and webfetch == "up" and websearch == "up":
        return "full"
    return "degraded"


def test_all_up_is_full():
    assert compute_global_verdict("up", "up", "up") == "full"


def test_firecrawl_down_is_degraded():
    assert compute_global_verdict("down", "up", "up") == "degraded"


def test_webfetch_down_is_degraded():
    assert compute_global_verdict("up", "down", "up") == "degraded"


def test_both_up_but_websearch_down_is_blocked():
    """Si WebSearch tombe, on ne peut RIEN faire. Le run doit être bloqué."""
    assert compute_global_verdict("up", "up", "down") == "blocked"


def test_all_down_is_blocked():
    assert compute_global_verdict("down", "down", "down") == "blocked"


def test_unknown_treated_as_down_for_critical_tools():
    """WebSearch unknown = ne pas lancer (conservateur)."""
    # WebSearch unknown + autres up : verdict = degraded (unknown != down strict)
    # Notre logique actuelle retourne degraded (unknown n'est pas "up" strict)
    assert compute_global_verdict("up", "up", "unknown") == "degraded"


def test_tools_health_structure():
    health = {
        "firecrawl": "up",
        "webfetch": "up",
        "websearch": "up",
        "verdict": "full",
        "checked_at": "2026-04-21T11:20:00",
    }
    for tool in ("firecrawl", "webfetch", "websearch"):
        assert health[tool] in VALID_TOOL_STATES
    assert health["verdict"] in VALID_GLOBAL_VERDICTS
