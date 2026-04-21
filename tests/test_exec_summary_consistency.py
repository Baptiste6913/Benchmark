"""Item 4 du hotfix — cohérence synthèse exécutive / fiches détaillées.

Lint : pour chaque acteur mentionné dans `exec_summary.three_takeaways[]`,
extraire la catégorisation appliquée (« by design », « remédiation »,
« hybride »…) et la confronter au scoring et au verdict red-team de la fiche.

Règles :
- Un acteur de verdict « À NUANCER » ou « REFAIRE » cité en bloc « by design »
  (sans asterisk ni nuance) → warning bloquant.
- Un acteur avec score `independance_stack` < 4 cité en « by design pur » →
  warning bloquant.

Ce test lit directement `bench.json` (pas les livrables) — c'est un linter
du contenu source de vérité, conforme à la checklist pre-delivery niveau 4
(bloc 5 : Contradictions internes → 5.4).

Test échoue sur le bench.json pré-hotfix item 4 (OVHcloud cité en by design
alors que verdict À NUANCER et score indep_stack = 4).
Passe après reformulation du takeaway.
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


def _actors_in_by_design_list(takeaway: str) -> list[str]:
    """Extrait les acteurs cités dans une liste « By design (X, Y, Z) » d'un takeaway."""
    pattern = re.compile(r"by\s+design\s*\(([^)]+)\)", re.IGNORECASE)
    matches = pattern.findall(takeaway)
    names: list[str] = []
    for m in matches:
        for piece in re.split(r"[,;/]", m):
            name = piece.strip()
            if name:
                names.append(name)
    return names


# Qualifiers qui signalent au lecteur que la catégorisation n'est pas pure.
# Si l'un apparaît dans le takeaway, on considère que le contexte accepte
# la nuance et le test ne flag pas l'incohérence.
# Qualifiers spécifiques à la catégorisation elle-même — doivent nommer ou
# désigner l'acteur dans un rôle distinct de "by design pur". Les mots
# génériques ("compromis", "mais", "avec") sont exclus car trop ambigus.
STRONG_QUALIFIERS = [
    "intermédiaire",
    "intermediaire",
    "juridictionnel",
    "incomplète technologique",
    "souveraineté technologique incomplète",
    "représente une voie",
    "represente une voie",
    "voie intermédiaire",
    "voie intermediaire",
    "nuancer dans le texte",
    "à nuancer pur",
    "avec asterisk",
    "hybride",
]


def _is_qualified_for(takeaway: str, actor_name: str) -> bool:
    """Vrai si au moins UNE phrase du takeaway contient à la fois le nom de
    l'acteur ET un STRONG_QUALIFIER.

    Un qualifier dans une autre phrase (ex: « Thalès est hybride ») ne protège
    PAS OVHcloud dans « by design (OVHcloud, Dassault, Schwarz) ».
    """
    sentences = re.split(r"[.!?]\s+", takeaway)
    name_low = actor_name.lower()
    for s in sentences:
        s_low = s.lower()
        if name_low not in s_low:
            continue
        for q in STRONG_QUALIFIERS:
            if q in s_low:
                return True
    return False


def _actors_in_remediation_list(takeaway: str) -> list[str]:
    pattern = re.compile(r"rem[éeè]diation[^()]*\(([^)]+)\)", re.IGNORECASE)
    matches = pattern.findall(takeaway)
    names: list[str] = []
    for m in matches:
        for piece in re.split(r"[,;/]", m):
            name = piece.strip()
            if name:
                names.append(name)
    return names


def _find_actor_by_name(bench: dict, mentioned: str) -> dict | None:
    """Retourne l'acteur dont `name` contient `mentioned` (insensible casse)."""
    for actor in bench.get("actors", []):
        name = actor.get("name", "").lower()
        if mentioned.lower() in name:
            return actor
    return None


def _score_for(actor: dict, criterion_id: str) -> float | None:
    for row in actor.get("scoring", []):
        if row.get("criterion_id") == criterion_id:
            return float(row.get("score"))
    return None


def test_no_a_nuancer_actor_in_unqualified_by_design_list(bench: dict) -> None:
    """Un acteur « À NUANCER » / « REFAIRE » ne doit pas être cité en liste
    « by design (...) » sans qu'un qualifier spécifique à cet acteur
    (« voie intermédiaire », « hybride », « souveraineté technologique
    incomplète », etc.) soit présent dans le même takeaway."""
    takeaways = (bench.get("exec_summary") or {}).get("three_takeaways", [])
    problems = []
    for idx, t in enumerate(takeaways):
        for mentioned in _actors_in_by_design_list(t):
            actor = _find_actor_by_name(bench, mentioned)
            if actor is None:
                continue
            verdict = (actor.get("red_team_verdict") or "").upper()
            if not ("NUANCER" in verdict or "REFAIRE" in verdict):
                continue
            if _is_qualified_for(t, mentioned):
                continue   # le takeaway nuance déjà cet acteur — OK
            problems.append(
                f"takeaway #{idx+1} : '{mentioned}' dans 'by design' sans qualification, "
                f"verdict red-team = {verdict!r}"
            )
    assert not problems, (
        "Incohérence synthèse / red-team — ajouter une qualification dans le texte "
        "(ex: « voie intermédiaire », « hybride ») :\n  - "
        + "\n  - ".join(problems)
    )


def test_no_low_independance_actor_in_unqualified_by_design_list(bench: dict) -> None:
    """Un acteur avec independance_stack < 4 ne doit pas être cité en « by design (...) »
    sans qualifier spécifique."""
    takeaways = (bench.get("exec_summary") or {}).get("three_takeaways", [])
    problems = []
    for idx, t in enumerate(takeaways):
        for mentioned in _actors_in_by_design_list(t):
            actor = _find_actor_by_name(bench, mentioned)
            if actor is None:
                continue
            score = _score_for(actor, "independance_stack")
            if score is None or score >= 4:
                continue
            if _is_qualified_for(t, mentioned):
                continue
            problems.append(
                f"takeaway #{idx+1} : '{mentioned}' en 'by design' sans qualification, "
                f"independance_stack = {score}/5 (< 4)"
            )
    assert not problems, (
        "Incohérence synthèse / scoring indépendance stack :\n  - "
        + "\n  - ".join(problems)
    )


def test_takeaway_parser_smoke(bench: dict) -> None:
    """Sanity-check du parser : au moins un takeaway mentionne 'by design' ou 'remédiation'."""
    takeaways = (bench.get("exec_summary") or {}).get("three_takeaways", [])
    found = False
    for t in takeaways:
        if _actors_in_by_design_list(t) or _actors_in_remediation_list(t):
            found = True
            break
    assert found, "Aucun takeaway ne cite de catégorisation — le parser est-il correct ?"
