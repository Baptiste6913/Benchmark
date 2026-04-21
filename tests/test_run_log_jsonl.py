"""Tests du format JSONL de outputs/<run_id>/run.log (v1.3 patch 8).

Valide :
- Chaque ligne = 1 JSON parseable
- Champs requis présents (ts, agent, event)
- Format ts ISO-ish
- Types d'event connus
"""

from __future__ import annotations

import json

import pytest


REQUIRED_EVENT_FIELDS = {"ts", "agent", "event"}

KNOWN_EVENT_TYPES = {
    "start", "end", "phase", "scope_ready", "tools_health_check",
    "solutions_found", "canonicalized", "pass1_start", "pass1_complete",
    "pass2_start", "pass2_complete", "dealbreaker_check", "scoring_complete",
    "report_written", "deliverables_written", "resumed", "rerun",
    "budget_exhausted", "error",
}


def parse_jsonl(text: str) -> list[dict]:
    events = []
    for i, line in enumerate(text.strip().split("\n"), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"Line {i} is not valid JSON: {e} — content: {line!r}") from e
    return events


SAMPLE_LOG = """\
{"ts":"2026-04-21T11:20:00","agent":"benchmark-lead","event":"scope_ready","mode":"standard"}
{"ts":"2026-04-21T11:22:00","agent":"mainthread","event":"phase","name":"discovery_start","parallel_agents":3}
{"ts":"2026-04-21T11:28:00","agent":"discoverer-a","event":"solutions_found","count":15}
{"ts":"2026-04-21T11:30:00","agent":"weighted-scorer","event":"dealbreaker_check","excluded":1,"passed":14}
{"ts":"2026-04-21T11:40:00","agent":"weighted-scorer","event":"scoring_complete","main":10,"a_approfondir":3,"insuffisants":1,"exclus":1}
{"ts":"2026-04-21T11:45:00","agent":"critic","event":"report_written","blocking":0,"warnings":3}
{"ts":"2026-04-21T11:48:00","agent":"render","event":"deliverables_written","xlsx":"deliverables/rid.xlsx","docx":"deliverables/rid.docx"}
"""


def test_sample_log_parses():
    events = parse_jsonl(SAMPLE_LOG)
    assert len(events) == 7


def test_every_event_has_required_fields():
    events = parse_jsonl(SAMPLE_LOG)
    for i, e in enumerate(events):
        missing = REQUIRED_EVENT_FIELDS - e.keys()
        assert not missing, f"Event #{i} missing {missing}: {e}"


def test_event_types_in_known_set_or_extensible():
    """Tous les types utilisés dans SAMPLE_LOG doivent être dans KNOWN_EVENT_TYPES."""
    events = parse_jsonl(SAMPLE_LOG)
    for e in events:
        # On accepte des extensions mais on exige que les types standards soient connus
        assert e["event"] in KNOWN_EVENT_TYPES, (
            f"Event type '{e['event']}' unknown — ajouter à KNOWN_EVENT_TYPES "
            "ou renommer pour respecter la taxonomie"
        )


def test_ts_format_iso_ish():
    events = parse_jsonl(SAMPLE_LOG)
    for e in events:
        ts = e["ts"]
        # ISO 8601 base check : 4 chiffres + "-" + 2 + "-" + 2 + "T"
        assert len(ts) >= 16, f"ts too short: {ts}"
        assert ts[4] == "-" and ts[7] == "-" and ts[10] == "T", (
            f"ts '{ts}' n'est pas au format ISO 8601 attendu"
        )


def test_malformed_jsonl_raises():
    bad = """{"ts":"2026-04-21","agent":"x","event":"y"}
not-a-json-line
{"ts":"2026-04-21","agent":"z","event":"w"}
"""
    with pytest.raises(ValueError) as exc:
        parse_jsonl(bad)
    assert "Line 2" in str(exc.value)


def test_empty_log_returns_empty_list():
    assert parse_jsonl("") == []
    assert parse_jsonl("   \n  \n") == []
