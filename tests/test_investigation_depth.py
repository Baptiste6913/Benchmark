"""Tests du tag investigation_depth sur vendor-deep-dive (v1.3 fix 4).

Valide :
- Dérivation depth ∈ {full, partial, shallow} depuis sources_used
- Cas limite : firecrawl_pages=0 + webfetch_pages=0 → shallow
- Cas intermédiaire : firecrawl_pages=1 → partial
- Cas complet : firecrawl_pages>=2 → full
- Le cas 10/15 partial soulevé par ton prompt — doit produire un ratio pondéré 0.333
"""

from __future__ import annotations

import pytest

from lib._common import (
    VALID_INVESTIGATION_DEPTHS,
    compute_investigation_depth,
    should_trigger_degraded_mode,
)


# -----------------------------------------------------------------------------
# Dérivation investigation_depth depuis sources_used
# -----------------------------------------------------------------------------


def test_full_depth_requires_two_firecrawl_pages():
    assert compute_investigation_depth({"firecrawl_pages": 2, "webfetch_pages": 0, "websearch_queries": 3}) == "full"
    assert compute_investigation_depth({"firecrawl_pages": 5, "webfetch_pages": 0, "websearch_queries": 0}) == "full"


def test_partial_depth_with_one_firecrawl():
    assert compute_investigation_depth({"firecrawl_pages": 1, "webfetch_pages": 0, "websearch_queries": 2}) == "partial"


def test_partial_depth_with_webfetch_fallback():
    assert compute_investigation_depth({"firecrawl_pages": 0, "webfetch_pages": 3, "websearch_queries": 5}) == "partial"


def test_shallow_depth_when_only_websearch():
    assert compute_investigation_depth({"firecrawl_pages": 0, "webfetch_pages": 0, "websearch_queries": 5}) == "shallow"
    assert compute_investigation_depth({"firecrawl_pages": 0, "webfetch_pages": 1, "websearch_queries": 5}) == "shallow"


def test_shallow_when_sources_empty():
    assert compute_investigation_depth({}) == "shallow"
    assert compute_investigation_depth({"firecrawl_pages": 0}) == "shallow"


def test_valid_depths_enum():
    assert VALID_INVESTIGATION_DEPTHS == {"full", "partial", "shallow"}


# -----------------------------------------------------------------------------
# Cas limite soulevé par le prompt utilisateur : 10/15 partial (v1.3 Q2)
# -----------------------------------------------------------------------------


def _actors_with_depths(spec: dict) -> list[dict]:
    """spec = {'full': N, 'partial': M, 'shallow': K} → liste d'acteurs."""
    out = []
    for depth, n in spec.items():
        out.extend([{"id": f"a-{depth}-{i}", "investigation_depth": depth} for i in range(n)])
    return out


def test_10_of_15_partial_does_not_trigger_at_default_threshold():
    """Cas du prompt utilisateur Q2 : 10/15 partial seuls ne doivent PAS trigger.

    Formule v1.3 : (shallow + partial/2) / total = (0 + 10/2) / 15 = 5/15 = 0.333.
    Seuil défaut 0.5 → 0.333 < 0.5 → pas de disclaimer.
    """
    actors = _actors_with_depths({"full": 5, "partial": 10, "shallow": 0})
    assert should_trigger_degraded_mode(actors, threshold=0.5) is False


def test_10_partial_plus_3_shallow_triggers_at_default():
    """10 partial + 3 shallow sur 15 : ratio = (3 + 5) / 15 = 0.533 > 0.5 → disclaimer."""
    actors = _actors_with_depths({"full": 2, "partial": 10, "shallow": 3})
    assert should_trigger_degraded_mode(actors, threshold=0.5) is True


def test_stricter_threshold_triggers_earlier():
    """Seuil 0.3 : 10/15 partial suffit (ratio 0.333 > 0.3)."""
    actors = _actors_with_depths({"full": 5, "partial": 10, "shallow": 0})
    assert should_trigger_degraded_mode(actors, threshold=0.3) is True


def test_lenient_threshold_defers_trigger():
    """Seuil 0.7 : même 10 partial + 3 shallow (ratio 0.533) ne trigger pas."""
    actors = _actors_with_depths({"full": 2, "partial": 10, "shallow": 3})
    assert should_trigger_degraded_mode(actors, threshold=0.7) is False


def test_only_shallow_triggers():
    """Tout en shallow : ratio = 1.0 > tout seuil raisonnable."""
    actors = _actors_with_depths({"full": 0, "partial": 0, "shallow": 10})
    assert should_trigger_degraded_mode(actors, threshold=0.5) is True


def test_only_full_never_triggers():
    actors = _actors_with_depths({"full": 10, "partial": 0, "shallow": 0})
    assert should_trigger_degraded_mode(actors, threshold=0.5) is False


def test_empty_actors_does_not_trigger():
    assert should_trigger_degraded_mode([], threshold=0.5) is False


def test_missing_depth_counts_as_shallow_conservatism():
    """Un acteur sans investigation_depth est compté comme shallow (fail-safe)."""
    actors = [
        {"id": "a-full", "investigation_depth": "full"},
        {"id": "a-missing"},  # pas de depth
    ]
    # (1 shallow-ish + 0 partial/2) / 2 = 0.5 → strictement > 0.5 ? Non, > strict
    # Mais avec 1 missing et seuil 0.4, doit trigger
    assert should_trigger_degraded_mode(actors, threshold=0.4) is True
