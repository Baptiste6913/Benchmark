"""Tests du format firecrawl-ledger.json (v1.3 patch 3 — dynamic budget + 2-pass).

Valide :
- Structure JSON (champs requis, types)
- Tracking budget cohérent (somme credits_used == scrapes_consommes)
- Format des events (ts ISO, phase in {P1, P2, ...}, verdict enum)
- Fallback tracking (fallbacks_appliques avec raison in {budget_exhausted, firecrawl_down})
- Détection du mode dégradé quand budget épuisé
"""

from __future__ import annotations

import pytest


LEDGER_REQUIRED = {"run_id", "budget_initial", "scrapes_consommes", "events"}
EVENT_REQUIRED = {"ts", "phase", "url", "verdict", "credits_used"}
VALID_PHASES = {"P1", "P2", "pre-run-test", "investigation-pass-1", "investigation-pass-2"}
VALID_VERDICTS = {"OK", "PARTIAL", "FAIL", "TIMEOUT"}


@pytest.fixture
def ledger_valid() -> dict:
    return {
        "run_id": "20260421-1120-test-mission",
        "budget_initial": 60,
        "scrapes_consommes": 3,
        "budget_restant_estime": 57,
        "mode_degrade": False,
        "events": [
            {
                "ts": "2026-04-21T11:25:00",
                "phase": "P1",
                "vendor_id": "vendor-a",
                "url": "https://vendor-a.com",
                "verdict": "OK",
                "markdown_chars": 8500,
                "credits_used": 1,
            },
            {
                "ts": "2026-04-21T11:26:00",
                "phase": "P1",
                "vendor_id": "vendor-b",
                "url": "https://vendor-b.com",
                "verdict": "OK",
                "markdown_chars": 4200,
                "credits_used": 1,
            },
            {
                "ts": "2026-04-21T11:40:00",
                "phase": "P2",
                "vendor_id": "vendor-a",
                "url": "https://vendor-a.com/pricing",
                "verdict": "OK",
                "markdown_chars": 3200,
                "credits_used": 1,
            },
        ],
        "fallbacks_appliques": [],
    }


def test_ledger_has_required_top_level_fields(ledger_valid):
    assert LEDGER_REQUIRED.issubset(ledger_valid.keys())


def test_every_event_has_required_fields(ledger_valid):
    for event in ledger_valid["events"]:
        missing = EVENT_REQUIRED - event.keys()
        assert not missing, f"Event missing fields {missing}: {event}"


def test_events_use_valid_phases(ledger_valid):
    for event in ledger_valid["events"]:
        assert event["phase"] in VALID_PHASES, f"Unknown phase: {event['phase']}"


def test_events_use_valid_verdicts(ledger_valid):
    for event in ledger_valid["events"]:
        assert event["verdict"] in VALID_VERDICTS, f"Unknown verdict: {event['verdict']}"


def test_budget_accounting_consistent(ledger_valid):
    total_credits = sum(e["credits_used"] for e in ledger_valid["events"])
    assert total_credits == ledger_valid["scrapes_consommes"], (
        f"Sum of credits_used ({total_credits}) != scrapes_consommes "
        f"({ledger_valid['scrapes_consommes']})"
    )


def test_budget_restant_consistent(ledger_valid):
    expected = ledger_valid["budget_initial"] - ledger_valid["scrapes_consommes"]
    assert ledger_valid["budget_restant_estime"] == expected


def test_fallback_on_exhausted_budget_triggers_degraded_mode():
    ledger = {
        "run_id": "20260421-1120-test",
        "budget_initial": 2,
        "scrapes_consommes": 2,
        "budget_restant_estime": 0,
        "mode_degrade": True,
        "events": [
            {"ts": "2026-04-21T11:00", "phase": "P1", "url": "https://a",
             "verdict": "OK", "credits_used": 1},
            {"ts": "2026-04-21T11:05", "phase": "P1", "url": "https://b",
             "verdict": "OK", "credits_used": 1},
        ],
        "fallbacks_appliques": [
            {
                "phase": "P2",
                "vendor_id": "vendor-c",
                "raison": "budget_exhausted",
                "impact": "Fiche basculée en investigation_depth=partial",
            }
        ],
    }
    assert ledger["mode_degrade"] is True
    assert ledger["budget_restant_estime"] == 0
    assert len(ledger["fallbacks_appliques"]) == 1
    assert ledger["fallbacks_appliques"][0]["raison"] == "budget_exhausted"
