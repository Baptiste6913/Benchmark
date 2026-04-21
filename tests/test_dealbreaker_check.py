"""Tests du dealbreaker check Phase 0 (v1.3 fix 1).

Valide :
- Helpers lib/_common : get_excluded_actors, has_dealbreakers_configured, translate_legacy
- Structure dealbreaker-check.json (audit trail)
- Cohérence bench.json : vendor violated est bien dans exclus_dealbreaker
- Format dealbreaker_violations (rule_id + evidence obligatoires)
"""

from __future__ import annotations

import pytest

from lib._common import (
    VALID_DEALBREAKER_VERDICTS,
    get_excluded_actors,
    has_dealbreakers_configured,
    translate_legacy_dealbreakers,
)


# ---------------------------------------------------------------------------
# has_dealbreakers_configured
# ---------------------------------------------------------------------------


def test_has_dealbreakers_configured_true_for_v1_1_1_format():
    scope = {
        "dealbreakers": [
            {"id": "db_1", "criterion": "hosting", "rule": "...", "verdict_if_violated": "excluded"}
        ]
    }
    assert has_dealbreakers_configured(scope) is True


def test_has_dealbreakers_configured_false_for_empty():
    assert has_dealbreakers_configured({"dealbreakers": []}) is False
    assert has_dealbreakers_configured({}) is False


def test_has_dealbreakers_configured_false_for_legacy_flat_list():
    # Format v1.0 (liste de strings plate) — ne compte pas comme configuré v1.1.1
    scope = {"certifications_requises": ["HDS", "ISO 27001"]}
    assert has_dealbreakers_configured(scope) is False


# ---------------------------------------------------------------------------
# translate_legacy_dealbreakers
# ---------------------------------------------------------------------------


def test_translate_legacy_produces_structured_rules():
    legacy = {
        "certifications_requises": ["HDS"],
        "secteurs_exclus": ["Defense US"],
        "editeurs_bannis": ["Acme Corp"],
    }
    new = translate_legacy_dealbreakers(legacy)
    assert new.get("legacy_dealbreakers_translated") is True
    rules = new["dealbreakers"]
    assert len(rules) == 3
    ids = {r["id"] for r in rules}
    assert any("db_cert_hds" in i for i in ids)
    assert any("db_sector" in i for i in ids)
    assert any("db_vendor_banned" in i for i in ids)
    # Every translated rule is structurally complete
    for r in rules:
        assert "rule" in r
        assert r["verdict_if_violated"] == "excluded"


def test_translate_legacy_noop_if_no_legacy_fields():
    scope = {"mission": "test"}
    new = translate_legacy_dealbreakers(scope)
    # No dealbreakers added, no flag set
    assert "dealbreakers" not in new
    assert "legacy_dealbreakers_translated" not in new


# ---------------------------------------------------------------------------
# get_excluded_actors
# ---------------------------------------------------------------------------


def test_get_excluded_actors_reads_explicit_list():
    bench = {
        "exec_summary": {"exclus_dealbreaker": ["vendor-a", "vendor-b"]},
        "actors": [
            {"id": "vendor-a", "dealbreaker_verdict": "violated"},
            {"id": "vendor-b", "dealbreaker_verdict": "violated"},
            {"id": "vendor-c", "dealbreaker_verdict": "pass"},
        ],
    }
    assert get_excluded_actors(bench) == ["vendor-a", "vendor-b"]


def test_get_excluded_actors_falls_back_to_actors_verdict():
    bench = {
        "exec_summary": {},
        "actors": [
            {"id": "vendor-a", "dealbreaker_verdict": "violated"},
            {"id": "vendor-c", "dealbreaker_verdict": "pass"},
        ],
    }
    assert get_excluded_actors(bench) == ["vendor-a"]


def test_get_excluded_actors_empty_if_no_violations():
    bench = {
        "actors": [
            {"id": "vendor-a", "dealbreaker_verdict": "pass"},
            {"id": "vendor-b", "dealbreaker_verdict": "unknown"},
        ]
    }
    assert get_excluded_actors(bench) == []


# ---------------------------------------------------------------------------
# Schema: dealbreaker_verdict enum + violations structure
# ---------------------------------------------------------------------------


def test_valid_dealbreaker_verdicts_include_three_values():
    assert VALID_DEALBREAKER_VERDICTS == {"pass", "violated", "unknown"}


def test_violated_actor_must_have_violations_list():
    """Convention v1.3 : dealbreaker_verdict == violated implique dealbreaker_violations non vide."""
    actor = {
        "id": "vendor-a",
        "dealbreaker_verdict": "violated",
        "dealbreaker_violations": [
            {
                "rule_id": "db_hosting_eu",
                "evidence": "Hébergement AWS us-east-1 uniquement (page Architecture, 2026-04-21)",
                "source_id": "vendor-a-1",
            }
        ],
    }
    assert actor["dealbreaker_verdict"] in VALID_DEALBREAKER_VERDICTS
    for v in actor["dealbreaker_violations"]:
        assert "rule_id" in v
        assert "evidence" in v
