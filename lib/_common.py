"""Chargement du bench + grille et primitives partagées par xlsx / docx.

Charte Ascend (référencée par la spec S2.3) centralisée ici pour éviter la
dérive entre les deux générateurs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


# -----------------------------------------------------------------------------
# Charte Ascend — couleurs en HEX RGB (6 chars, sans #)
# -----------------------------------------------------------------------------

ASCEND_PALETTE: dict[str, str] = {
    # Couleurs principales
    "page_bg":          "F7F5F0",  # crème (fond encadrés légers)
    "title_primary":    "3D1D08",  # brun foncé (titres principaux, signature Ascend)
    "accent_primary":   "CA3F31",  # rouge brique Ascend (numérotation, verdict REFAIRE)
    "accent_secondary": "CBB57E",  # beige doré (séparateurs, verdict À NUANCER)
    "brun_clair":       "BC997A",  # brun clair (texte secondaire, métadonnées, footer)
    "bleu_petrole":     "0E5876",  # bleu pétrole (contraste ponctuel, citation)
    "box_bg_neutral":   "EEEBE3",  # fond encadrés neutre
    "box_bg_warm":      "FBF1ED",  # crème soutenue (En bref, citation)
    "white":            "FFFFFF",
    "black":            "000000",
}

# Polices — primaire en premier, fallback système en second
ASCEND_FONTS = {
    "title":  ["Signifier", "Georgia"],      # serif, pour les titres
    "body":   ["Söhne", "Calibri"],          # sans-serif, pour le corps
}


# -----------------------------------------------------------------------------
# Chargement bench + grille
# -----------------------------------------------------------------------------


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_grid_path(bench: dict, bench_path: Path, explicit_grid: Path | None = None) -> Path:
    """Résout le chemin de la grille.

    Priorité : explicit_grid > bench.meta.grid_ref (relatif au repo root).
    """
    if explicit_grid is not None:
        return explicit_grid
    grid_ref = bench.get("grid_ref")
    if not grid_ref:
        raise ValueError("bench.grid_ref absent ; fournir grid_path explicite.")
    # grid_ref est typiquement "scoring-grids/foo.json" relatif au repo root.
    # On remonte depuis bench_path pour trouver le repo root.
    current = bench_path.resolve().parent
    for _ in range(6):
        candidate = current / grid_ref
        if candidate.exists():
            return candidate
        current = current.parent
    raise FileNotFoundError(f"Grille {grid_ref} introuvable en remontant depuis {bench_path}.")


# -----------------------------------------------------------------------------
# Contexte exploité par les générateurs
# -----------------------------------------------------------------------------


@dataclass
class BenchContext:
    """Bundle bench + grille pour les générateurs xlsx/docx.

    Les générateurs ne lisent jamais les JSON directement — ils passent par
    ce contexte qui expose des helpers idempotents.
    """

    bench: dict
    grid: dict
    bench_path: Path
    grid_path: Path

    # Dérivés, calculés au chargement
    criteria: list[dict] = field(default_factory=list)
    actors_by_rank: list[dict] = field(default_factory=list)
    sources_by_id: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls, bench_path: Path, grid_path: Path | None = None) -> "BenchContext":
        bench = load_json(bench_path)
        actual_grid_path = resolve_grid_path(bench, bench_path, grid_path)
        grid = load_json(actual_grid_path)
        ctx = cls(
            bench=bench,
            grid=grid,
            bench_path=bench_path,
            grid_path=actual_grid_path,
            criteria=grid.get("criteria", []),
            actors_by_rank=sorted(bench.get("actors", []), key=lambda a: a.get("rank", 999)),
            sources_by_id={s["id"]: s for s in bench.get("sources", []) if isinstance(s, dict)},
        )
        return ctx

    # ---- Helpers ----

    def criterion_ids(self) -> list[str]:
        return [c["id"] for c in self.criteria]

    def criterion_by_id(self, cid: str) -> dict:
        for c in self.criteria:
            if c["id"] == cid:
                return c
        raise KeyError(f"critère '{cid}' introuvable dans la grille {self.grid_path.name}")

    def criterion_display(self, c_or_id) -> str:
        """Retourne le libellé d'affichage d'un critère.

        Priorité : `label_fr` > `name` > `id`. Permet de distinguer l'ID
        technique ASCII des grilles (immuable, snake_case) du libellé accentué
        affiché en livrable.
        """
        c = c_or_id if isinstance(c_or_id, dict) else self.criterion_by_id(c_or_id)
        return c.get("label_fr") or c.get("name") or c.get("id", "")

    def actor_score(self, actor: dict, criterion_id: str) -> int | None:
        for row in actor.get("scoring", []):
            if row.get("criterion_id") == criterion_id:
                return row.get("score")
        return None

    def actor_justification(self, actor: dict, criterion_id: str) -> str:
        for row in actor.get("scoring", []):
            if row.get("criterion_id") == criterion_id:
                return row.get("justification", "")
        return ""

    def mode(self) -> str:
        return self.bench.get("meta", {}).get("mode", "")

    def consultant(self) -> str:
        return self.bench.get("meta", {}).get("consultant", "")

    def client(self) -> str:
        return self.bench.get("meta", {}).get("client", "")

    def mission(self) -> str:
        return self.bench.get("meta", {}).get("mission", "")

    def date(self) -> str:
        return self.bench.get("meta", {}).get("date", "")

    def version(self) -> str:
        return self.bench.get("meta", {}).get("version", "")


# -----------------------------------------------------------------------------
# Mapping verdict → couleur Ascend
# -----------------------------------------------------------------------------


def criterion_display(c: dict) -> str:
    """Version libre du helper (sans BenchContext). label_fr > name > id."""
    return c.get("label_fr") or c.get("name") or c.get("id", "")


def verdict_palette(verdict: str | None) -> dict:
    """Retourne un dict {bg, fg} en hex pour un verdict donné.

    Utilisé par xlsx (code couleur de cellule) et docx (fond d'encadré).
    """
    if not verdict or verdict == "N/A":
        return {"bg": ASCEND_PALETTE["page_bg"], "fg": ASCEND_PALETTE["brun_clair"]}
    v = verdict.upper()
    if "REFAIRE" in v:
        return {"bg": ASCEND_PALETTE["box_bg_warm"], "fg": ASCEND_PALETTE["accent_primary"]}
    if "NUANCER" in v:
        return {"bg": ASCEND_PALETTE["box_bg_neutral"], "fg": ASCEND_PALETTE["accent_secondary"]}
    if "TIENT" in v or v == "OK":
        return {"bg": ASCEND_PALETTE["box_bg_neutral"], "fg": ASCEND_PALETTE["bleu_petrole"]}
    return {"bg": ASCEND_PALETTE["page_bg"], "fg": ASCEND_PALETTE["brun_clair"]}


def score_color(score: int | float | None) -> str:
    """Retourne un code couleur hex selon le score (1-5).

    <3 rouge, 3-3.9 orange, ≥4 vert. Les tons sont adoucis par rapport au
    standard Excel pour rester dans la charte Ascend (pas de vert sapin criard).
    """
    if score is None:
        return "F8F7F3"
    if score < 3:
        return "F4C7C1"   # rouge doux
    if score < 4:
        return "F2DAB8"   # orange doux
    return "CFE0C3"       # vert doux


# Score limites et poids
# -----------------------------------------------------------------------------
# Dealbreaker helpers (v1.3 fix 1)
# -----------------------------------------------------------------------------


VALID_DEALBREAKER_VERDICTS = {"pass", "violated", "unknown"}


def get_excluded_actors(bench: dict) -> list[str]:
    """Retourne les actor_id de exec_summary.exclus_dealbreaker (ou []).

    Source de vérité : exec_summary.exclus_dealbreaker (liste d'IDs). Sinon,
    fallback sur les actors[] qui ont dealbreaker_verdict == "violated".
    """
    exec_ = bench.get("exec_summary") or {}
    explicit = exec_.get("exclus_dealbreaker")
    if isinstance(explicit, list):
        return list(explicit)
    return [
        a["id"] for a in bench.get("actors", [])
        if a.get("dealbreaker_verdict") == "violated"
    ]


def has_dealbreakers_configured(scope: dict) -> bool:
    """True si scope.yaml.dealbreakers contient au moins une règle structurée."""
    db = scope.get("dealbreakers") or []
    if not isinstance(db, list):
        return False
    return any(isinstance(rule, dict) and rule.get("id") for rule in db)


def translate_legacy_dealbreakers(scope: dict) -> dict:
    """Auto-traduit le format legacy v1.0 (3 catégories de strings) vers v1.1.1 (objets).

    Legacy : {certifications_requises: [...], secteurs_exclus: [...], editeurs_bannis: [...]}
    → v1.1.1 : {dealbreakers: [{id, criterion, rule, verdict_if_violated, ...}, ...]}
    Mutate le dict retourné (copy), ajoute legacy_dealbreakers_translated: true.
    """
    new_scope = dict(scope)
    rules: list[dict] = []
    for cert in scope.get("certifications_requises") or []:
        rules.append({
            "id": f"db_cert_{cert.lower().replace(' ', '_')}",
            "criterion": "certifications",
            "rule": f"Certification '{cert}' requise.",
            "verdict_if_violated": "excluded",
            "source_required": True,
        })
    for sector in scope.get("secteurs_exclus") or []:
        rules.append({
            "id": f"db_sector_excl_{sector.lower().replace(' ', '_')}",
            "criterion": "sector_experience",
            "rule": f"Solutions dédiées au secteur '{sector}' exclues.",
            "verdict_if_violated": "excluded",
            "source_required": False,
        })
    for editeur in scope.get("editeurs_bannis") or []:
        rules.append({
            "id": f"db_vendor_banned_{editeur.lower().replace(' ', '_')}",
            "criterion": "vendor_identity",
            "rule": f"Éditeur '{editeur}' banni.",
            "verdict_if_violated": "excluded",
            "source_required": False,
        })
    if rules:
        new_scope["dealbreakers"] = rules
        new_scope["legacy_dealbreakers_translated"] = True
    return new_scope


# -----------------------------------------------------------------------------
# Score / poids (idempotent)
# -----------------------------------------------------------------------------


def weighted_total(actor: dict) -> float:
    """Re-calcule le score pondéré d'un acteur depuis ses scoring[] entries.

    Assure que le weighted_score stocké est cohérent avec les composants.
    Raise si weights absents ou somme != 1.0 (±0.01).
    """
    rows = actor.get("scoring", [])
    weights = [r.get("weight") for r in rows]
    scores = [r.get("score") for r in rows]
    if any(w is None for w in weights):
        raise ValueError(f"actor {actor.get('id')} a des scoring[] sans weight — impossible de recalculer")
    total_w = sum(weights)
    if abs(total_w - 1.0) > 0.01:
        raise ValueError(f"actor {actor.get('id')} — somme des weights = {total_w:.3f} (attendu ≈ 1.0)")
    return sum(s * w for s, w in zip(scores, weights))


# -----------------------------------------------------------------------------
# Run persistence (v1.3 patch 8 — Option A additive)
# -----------------------------------------------------------------------------


import re as _re

RUN_ID_RE = _re.compile(r"^(\d{8})-(\d{4})-([a-z0-9]{1,40})-([a-z0-9][a-z0-9-]{0,39})$")


def parse_run_id(run_id: str) -> dict:
    """Parse un run_id YYYYMMDD-HHMM-<client-slug>-<usecase-slug>.

    Retourne {"date": "YYYYMMDD", "time": "HHMM", "client_slug": "...", "usecase_slug": "..."}
    Raise ValueError si format invalide.

    Convention v1.3 : client_slug est un **seul mot** (pas de tiret interne) pour lever
    l'ambiguïté avec usecase_slug qui, lui, peut contenir des tirets. Exemples valides :
    `20260421-1120-ascend-banque-privee-fr` → client=ascend, usecase=banque-privee-fr.
    """
    m = RUN_ID_RE.match(run_id)
    if not m:
        raise ValueError(
            f"run_id '{run_id}' invalide — format attendu : "
            "YYYYMMDD-HHMM-<client-slug>-<usecase-slug> "
            "(slugs kebab-case ASCII, max 40 chars chacun)"
        )
    return {
        "date": m.group(1),
        "time": m.group(2),
        "client_slug": m.group(3),
        "usecase_slug": m.group(4),
    }


def run_output_layout(run_id: str) -> dict:
    """Retourne les chemins canoniques d'un run (sans les créer).

    Les clés correspondent aux producers documentés dans docs/run-persistence.md.
    """
    from pathlib import Path as _Path
    base = _Path("outputs") / run_id
    return {
        "root": base,
        "scope": base / "scope.yaml",
        "discovery_dir": base / "discovery",
        "factsheets_dir": base / "factsheets",
        "scoring_dir": base / "scoring",
        "scoring_dealbreaker": base / "scoring" / "dealbreaker-check.json",
        "scoring_scores": base / "scoring" / "scores.json",
        "scoring_grid_used": base / "scoring" / "grid-used.json",
        "reviews_dir": base / "reviews",
        "reviews_critic": base / "reviews" / "critic-report.md",
        "reviews_red_team": base / "reviews" / "red-team-report.md",
        "deliverables_dir": base / "deliverables",
        "bench_json": base / "bench.json",
        "firecrawl_ledger": base / "firecrawl-ledger.json",
        "tools_health": base / "tools-health.json",
        "blocked_urls": base / "blocked-urls.json",
        "run_log": base / "run.log",
    }


# -----------------------------------------------------------------------------
# Investigation depth + degraded mode (v1.3 fix 4)
# -----------------------------------------------------------------------------


VALID_INVESTIGATION_DEPTHS = {"full", "partial", "shallow"}

# Default threshold for degraded-mode disclaimer.
# The formula is (shallow + partial/2) / total > threshold. Overridable via
# scope.yaml.degraded_threshold to accommodate missions where shallow is expected
# (regulated markets with private AUM).
DEFAULT_DEGRADED_THRESHOLD = 0.5


def compute_investigation_depth(sources_used: dict) -> str:
    """Dérive investigation_depth ∈ {full, partial, shallow} du comptage sources.

    Convention :
    - `full`    : firecrawl_pages >= 2 (au moins P1 + 1 page P2)
    - `partial` : firecrawl_pages == 1 OU webfetch_pages >= 2 (fallback OK)
    - `shallow` : aucun Firecrawl ET < 2 WebFetch — seulement WebSearch / snippets
    """
    fc = int((sources_used or {}).get("firecrawl_pages", 0))
    wf = int((sources_used or {}).get("webfetch_pages", 0))
    if fc >= 2:
        return "full"
    if fc == 1 or wf >= 2:
        return "partial"
    return "shallow"


def degraded_threshold_from_scope(scope: dict) -> float:
    """Lit scope.yaml.degraded_threshold avec clamp [0, 1], défaut 0.5 (Q2 v1.3)."""
    raw = scope.get("degraded_threshold", DEFAULT_DEGRADED_THRESHOLD)
    try:
        t = float(raw)
    except (TypeError, ValueError):
        return DEFAULT_DEGRADED_THRESHOLD
    if t < 0.0:
        return 0.0
    if t > 1.0:
        return 1.0
    return t


def should_trigger_degraded_mode(actors: list[dict], threshold: float = DEFAULT_DEGRADED_THRESHOLD) -> bool:
    """Formule pondérée v1.3 (Q2) : (shallow + partial/2) / total > threshold.

    Args:
        actors: liste d'acteurs (chacun doit avoir investigation_depth).
        threshold: seuil [0, 1]. Défaut 0.5.

    Returns:
        True si le bench doit basculer en mode dégradé (disclaimer obligatoire).
    """
    if not actors:
        return False
    counts = {"full": 0, "partial": 0, "shallow": 0, "missing": 0}
    for a in actors:
        depth = a.get("investigation_depth")
        if depth not in VALID_INVESTIGATION_DEPTHS:
            counts["missing"] += 1
        else:
            counts[depth] += 1
    total = len(actors)
    # missing = shallow conservatism : on le compte comme shallow pour ne pas
    # masquer silencieusement le fait qu'une fiche n'a pas été instrumentée
    weighted_shallow = counts["shallow"] + counts["missing"] + counts["partial"] / 2.0
    ratio = weighted_shallow / total
    return ratio > threshold


def degraded_mode_disclaimer_text(threshold: float, actors: list[dict]) -> str:
    """Construit le texte du disclaimer (fin inséré dans exec_summary si trigger)."""
    counts = {"full": 0, "partial": 0, "shallow": 0}
    for a in actors:
        d = a.get("investigation_depth", "shallow")
        if d in counts:
            counts[d] += 1
    total = len(actors)
    weighted = counts["shallow"] + counts["partial"] / 2.0
    ratio = weighted / total if total else 0.0
    return (
        f"Ce bench a été produit en MODE DEGRADE. "
        f"{counts['partial']}/{total} fiches en investigation_depth=partial et "
        f"{counts['shallow']}/{total} en shallow. "
        f"Ratio pondéré (shallow + partial/2) / total = {ratio:.2f}, "
        f"au-dessus du seuil configuré {threshold:.2f}. "
        "Les recommandations de ce bench doivent être considérées comme "
        "indicatives et re-triangulées avant toute diffusion client."
    )
