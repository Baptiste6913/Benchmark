"""Tests de l'arborescence outputs/<run_id>/ et du format run_id (v1.3 patch 8).

Valide :
- Regex run_id : YYYYMMDD-HHMM-<client-slug>-<usecase-slug>
- parse_run_id extrait les 4 composants
- run_output_layout retourne les chemins canoniques documentés dans docs/run-persistence.md
- bench.json peut vivre dans examples/ OU dans outputs/<run_id>/ (Option A)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lib._common import parse_run_id, run_output_layout


VALID_RUN_IDS = [
    "20260421-1120-ascend-banque-privee-fr",
    "20260503-0900-acme-gt2-ia-conv",
    "20260614-1500-interne-veille-ai-ops",
    "20260117-2359-dgfip-ia-conv-n1",
]

INVALID_RUN_IDS = [
    "2026-04-21-1120-ascend-test",           # date with separators
    "20260421-1120-Ascend-test",             # uppercase in slug
    "20260421-1120-ascend_test_snake",       # snake_case
    "20260421-1120--double-dash",            # empty client slug
    "20260421-1120-ascend-" + "x" * 41,       # usecase > 40 chars
    "2026042-1120-ascend-test",              # date too short
    "",                                       # empty
]


@pytest.mark.parametrize("rid", VALID_RUN_IDS)
def test_parse_run_id_valid(rid):
    parsed = parse_run_id(rid)
    assert set(parsed.keys()) == {"date", "time", "client_slug", "usecase_slug"}
    assert len(parsed["date"]) == 8
    assert len(parsed["time"]) == 4


@pytest.mark.parametrize("rid", INVALID_RUN_IDS)
def test_parse_run_id_rejects_invalid(rid):
    with pytest.raises(ValueError):
        parse_run_id(rid)


def test_parse_run_id_extracts_slugs():
    p = parse_run_id("20260421-1120-ascend-banque-privee-fr")
    assert p["date"] == "20260421"
    assert p["time"] == "1120"
    assert p["client_slug"] == "ascend"
    assert p["usecase_slug"] == "banque-privee-fr"


def test_run_output_layout_returns_expected_paths():
    layout = run_output_layout("20260421-1120-ascend-test")
    expected_keys = {
        "root", "scope", "discovery_dir", "factsheets_dir", "scoring_dir",
        "scoring_dealbreaker", "scoring_scores", "scoring_grid_used",
        "reviews_dir", "reviews_critic", "reviews_red_team",
        "deliverables_dir", "bench_json", "firecrawl_ledger",
        "tools_health", "blocked_urls", "run_log",
    }
    assert set(layout.keys()) == expected_keys


def test_run_output_layout_paths_under_outputs_root():
    layout = run_output_layout("20260421-1120-ascend-test")
    root = layout["root"]
    assert root == Path("outputs") / "20260421-1120-ascend-test"
    assert str(layout["bench_json"]).endswith("20260421-1120-ascend-test/bench.json")
    assert str(layout["run_log"]).endswith("20260421-1120-ascend-test/run.log")
    assert str(layout["scoring_dealbreaker"]).endswith("scoring/dealbreaker-check.json")


def test_run_output_layout_accepts_ascii_kebab_slugs_up_to_40_chars():
    long_usecase = "a" * 40
    rid = f"20260421-1120-client-{long_usecase}"
    layout = run_output_layout(rid)
    assert str(layout["root"]).endswith(rid)
