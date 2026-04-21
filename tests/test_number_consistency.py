"""Item 5 du hotfix — cohérence des chiffres-clés intra-fiche.

Pour chaque acteur, extrait les nombres significatifs mentionnés dans
`context`, `key_figures[].value`, `scoring[].justification`, `flagship_quote.text`,
`strategy.*`, `blind_spots[].text`. Normalise en valeur entière (350k → 350000,
"350 000" → 350000). Regroupe par unité proche (clients, ETP, salariés, …).
Pour chaque paire de valeurs avec la même unité, flag si l'écart relatif est
dans la zone [3%, 20%] — zone typique des incohérences "350k vs 370k" où les
deux chiffres sourcent des agrégats légèrement différents.

Règle formalisée dans workflows/pre-delivery-checklist.md § 5.5.

Pré-hotfix : Dassault contexte "~370 000 clients" vs justification "350k clients"
→ flag (écart 5,7 %). Post-hotfix : unifié à ~370 000 → pas de flag.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
LISI_BENCH = REPO_ROOT / "examples" / "generic-demo" / "bench.json"


@pytest.fixture(scope="module")
def bench() -> dict:
    return json.loads(LISI_BENCH.read_text(encoding="utf-8"))


UNIT_KEYWORDS = [
    "clients",
    "utilisateurs",
    "users",
    "etp",
    "salariés",
    "salaries",
    "employés",
    "collaborateurs",
    "serveurs",
    "datacenters",
    "heures de vol",
]


def _parse_number_str(s: str) -> int | None:
    s = s.replace("\u00A0", " ").strip()
    s_low = s.lower()
    if s_low.endswith("k"):
        try:
            return int(s[:-1].replace(" ", "").replace(",", ".").split(".")[0]) * 1000
        except ValueError:
            return None
    try:
        return int(s.replace(" ", ""))
    except ValueError:
        return None


# Match "350 000", "350k", "350K" (mais pas "350" tout seul ni "€350")
NUMBER_PATTERN = re.compile(
    r"(?<![\d€])(\d{1,3}(?:[ \u00A0]\d{3})+|\d{1,6}[kK])(?=[^\d]|$)"
)


def _extract_numbers_with_unit(text: str) -> list[tuple[int, str, str]]:
    """Retourne la liste (value, unit, snippet) pour chaque nombre détecté
    suivi dans les 40 chars d'un UNIT_KEYWORD."""
    out: list[tuple[int, str, str]] = []
    for m in NUMBER_PATTERN.finditer(text):
        raw = m.group(1)
        value = _parse_number_str(raw)
        if value is None or value < 1000:
            continue
        # Look at up to 40 chars after the number for a unit
        after = text[m.end(): m.end() + 60].lower()
        unit = None
        for kw in UNIT_KEYWORDS:
            if kw in after:
                unit = kw
                break
        if unit is None:
            continue
        snippet = text[max(0, m.start() - 20): min(len(text), m.end() + 60)]
        out.append((value, unit, snippet.strip()))
    return out


def _collect_actor_text(actor: dict) -> list[tuple[str, str]]:
    """Retourne [(where, text), ...] pour tous les champs textuels d'un acteur."""
    chunks = []
    if actor.get("context"):
        chunks.append(("context", actor["context"]))
    for i, fig in enumerate(actor.get("key_figures", []) or []):
        val = fig.get("value")
        if isinstance(val, str):
            chunks.append((f"key_figures[{i}].value", val))
    for i, row in enumerate(actor.get("scoring", []) or []):
        if row.get("justification"):
            chunks.append((f"scoring[{i}:{row.get('criterion_id')}].justification", row["justification"]))
    strat = actor.get("strategy") or {}
    for k, v in strat.items():
        if isinstance(v, str):
            chunks.append((f"strategy.{k}", v))
    for i, bs in enumerate(actor.get("blind_spots", []) or []):
        if bs.get("text"):
            chunks.append((f"blind_spots[{i}]", bs["text"]))
    fq = actor.get("flagship_quote") or {}
    if fq.get("text"):
        chunks.append(("flagship_quote.text", fq["text"]))
    ma = actor.get("maturity_and_approach")
    if ma:
        chunks.append(("maturity_and_approach", ma))
    return chunks


def test_no_similar_but_different_numbers_per_actor(bench: dict) -> None:
    problems: list[str] = []

    for actor in bench.get("actors", []):
        aid = actor.get("id", "?")
        # Collect all (value, unit, where, snippet) tuples
        findings: list[tuple[int, str, str, str]] = []
        for where, text in _collect_actor_text(actor):
            for value, unit, snippet in _extract_numbers_with_unit(text):
                findings.append((value, unit, where, snippet))

        # Group by unit and detect close-but-different pairs
        by_unit: dict[str, list] = {}
        for v, u, w, s in findings:
            by_unit.setdefault(u, []).append((v, w, s))

        for unit, entries in by_unit.items():
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    v1, w1, s1 = entries[i]
                    v2, w2, s2 = entries[j]
                    if v1 == v2:
                        continue
                    lo, hi = sorted([v1, v2])
                    delta = (hi - lo) / lo
                    if 0.03 <= delta <= 0.20:
                        problems.append(
                            f"actor '{aid}' unit='{unit}' : {w1}={v1} vs {w2}={v2} (écart {delta:.1%})"
                        )

    assert not problems, (
        "Chiffres-clés intra-fiche incohérents — voir règle § 5.5 :\n  - "
        + "\n  - ".join(problems)
    )
