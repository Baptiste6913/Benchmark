"""Tests du disclaimer degraded-mode paramétrable (v1.3 fix 4, Q2 user).

Valide :
- Lecture de scope.yaml.degraded_threshold avec clamp [0, 1]
- Défaut 0.5 quand absent ou invalide
- Texte du disclaimer contient les chiffres vérifiables
"""

from __future__ import annotations

import pytest

from lib._common import (
    DEFAULT_DEGRADED_THRESHOLD,
    degraded_mode_disclaimer_text,
    degraded_threshold_from_scope,
)


# -----------------------------------------------------------------------------
# Lecture du seuil depuis scope.yaml
# -----------------------------------------------------------------------------


def test_default_threshold_when_scope_empty():
    assert degraded_threshold_from_scope({}) == DEFAULT_DEGRADED_THRESHOLD
    assert DEFAULT_DEGRADED_THRESHOLD == 0.5


def test_threshold_from_scope_explicit():
    assert degraded_threshold_from_scope({"degraded_threshold": 0.3}) == 0.3
    assert degraded_threshold_from_scope({"degraded_threshold": 0.7}) == 0.7


def test_threshold_clamped_below_zero():
    assert degraded_threshold_from_scope({"degraded_threshold": -0.5}) == 0.0


def test_threshold_clamped_above_one():
    assert degraded_threshold_from_scope({"degraded_threshold": 1.5}) == 1.0


def test_threshold_invalid_falls_back_to_default():
    assert degraded_threshold_from_scope({"degraded_threshold": "not-a-number"}) == 0.5
    assert degraded_threshold_from_scope({"degraded_threshold": None}) == 0.5


# -----------------------------------------------------------------------------
# Disclaimer text
# -----------------------------------------------------------------------------


def test_disclaimer_includes_counts():
    actors = [
        {"investigation_depth": "partial"} for _ in range(10)
    ] + [
        {"investigation_depth": "shallow"} for _ in range(3)
    ] + [
        {"investigation_depth": "full"} for _ in range(2)
    ]
    text = degraded_mode_disclaimer_text(0.5, actors)
    assert "MODE DEGRADE" in text
    assert "10/15" in text
    assert "3/15" in text
    # Ratio pondéré : (3 + 10/2) / 15 = 8/15 ≈ 0.53
    assert "0.53" in text
    assert "0.50" in text  # seuil


def test_disclaimer_text_warns_about_client_diffusion():
    actors = [{"investigation_depth": "shallow"} for _ in range(5)]
    text = degraded_mode_disclaimer_text(0.5, actors)
    assert "re-triangulées" in text or "re-triangulees" in text or "triangul" in text
