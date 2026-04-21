---
name: weighted-scorer
description: "Use when scoring a list of solutions against a weighted criteria grid. Triggers: 'score ces solutions', 'classe selon ces critères', 'applique la grille', 'produis le classement'. Takes a solutions list and a JSON grid as input, returns a ranked list with per-criterion justifications."
---

# Weighted Scorer

## Overview

Appliquer une **grille de scoring pondérée** (JSON) à une liste de solutions (issues de
`vendor-deep-dive`). Rendre un classement justifié, défendable critère par critère.

**Principe directeur** : le score n'est pas l'argument, la justification l'est. Un 4/5 sans
justification défendable est un 0/5 en réunion client.

## When to Use

- Après `vendor-deep-dive` + `sovereignty-analyzer` + `fact-checker`.
- Quand le consultant a validé la short-list à scorer.
- En entrée du `critic` (qui vérifie la cohérence du scoring).

## Inputs attendus

1. **Liste de solutions** (JSON array, output de vendor-deep-dive).
2. **Grille de scoring** (chemin vers un JSON de `scoring-grids/`, ou grille inline).

Si pas de grille fournie : demander à l'utilisateur, ne pas inventer une grille.

## Output — JSON structuré

```json
{
  "grille_utilisee": "health-ai.json",
  "date_scoring": "2026-04-16",
  "nombre_solutions": 10,
  "resultats": [
    {
      "rang": 1,
      "solution": "...",
      "score_pondere": 4.12,
      "scores_par_critere": [
        {
          "critere_id": "maturite",
          "note": 4,
          "ponderation": 0.15,
          "justification": "80+ clients, 8 ans d'existence, recul production.",
          "sources": ["https://..."]
        }
      ],
      "notes_ND": ["pricing_public"],
      "commentaire_general": "..."
    }
  ]
}
```

## Règles

1. **Justification obligatoire** pour chaque note, même 3/5. Si tu ne peux pas justifier,
   c'est un `N/D`.
2. **Pas de demi-points.** L'échelle est 1-5 entière. Si tu hésites entre 3 et 4, tu choisis
   le moins favorable et tu expliques pourquoi tu n'as pas mis plus haut.
3. **N/D exclut le critère de la moyenne pondérée.** Tu recalcules la pondération sur les
   critères notés (somme des poids notés = 1). Tu le signales dans `notes_ND`.
4. **Échelle définie dans la grille.** Chaque niveau (1-5) a un label et un `requires` dans
   le JSON. Tu t'y réfères, tu ne redéfinies pas.
5. **Cohérence inter-solutions.** Si solution A a 100 clients = 4/5 sur "maturité", solution B
   avec 150 clients ne peut pas être 3/5.

## Format grille JSON

```json
{
  "name": "health-ai",
  "description": "...",
  "criteria": [
    {
      "id": "maturite",
      "name": "Maturité de la solution",
      "weight": 0.15,
      "scale": [
        { "value": 1, "label": "< 10 clients, < 3 ans", "requires": "Nombre clients" },
        { "value": 3, "label": "30-80 clients, 5-8 ans", "requires": "Nombre clients + année" },
        { "value": 5, "label": "> 150 clients, > 8 ans, références citables", "requires": "..." }
      ]
    }
  ]
}
```

## Quick Reference — workflow

1. Charger la grille JSON.
2. Vérifier que les poids somment à 1.0 (tolérance 0.01).
3. Pour chaque solution : pour chaque critère : lire le scale, choisir la note, justifier.
4. Agréger : `score_pondere = sum(note_i * weight_i) / sum(weight_notés)` (hors N/D).
5. Classer par score_pondere décroissant.
6. Appliquer les tie-breakers (en cas d'égalité, souveraineté puis maturité).

## Common Mistakes

- **Mettre 3/5 par défaut quand on ne sait pas.** C'est un biais massif qui rend tous les
  leaders ordinaires et tous les mauvais acceptables. Utiliser `N/D`.
- **Ne pas citer les sources dans la justification.** Le client demandera "d'où vient ce 4 ?".
  Réponse : la fiche vendor-deep-dive, colonne X, source Y.
- **Scorer sur des revendications marketing non vérifiées.** Une certification `revendiqué`
  n'est pas une certification. Elle se note comme absence.
- **Oublier de recalculer la pondération quand il y a des N/D.** Sans recalcul, les solutions
  avec plus de N/D sont artificiellement pénalisées ou avantagées.

---

## Phase 0 — Dealbreaker check (v1.3, fix 1)

**Nouvelle étape obligatoire avant le scoring pondéré** si `scope.yaml.dealbreakers` est non
vide. Le but : ne pas laisser un vendor qui viole une règle rédhibitoire (ex : pas d'hébergement
FR / UE pour un client secteur public) apparaître dans le classement principal à côté des
vendors conformes.

### Format dealbreakers dans `scope.yaml` (v1.1.1)

Les dealbreakers sont désormais une **liste d'objets structurés** (et non plus 3 catégories
fixes `certifications_requises` / `secteurs_exclus` / `editeurs_bannis` du format legacy v1.0) :

```yaml
dealbreakers:
  - id: db_hosting_eu
    criterion: hosting_region
    rule: "L'hébergement de production doit inclure au moins une région UE ou FR."
    verdict_if_violated: excluded
    source_required: true
    rationale: "Doctrine Cloud au centre (circulaire 5 juillet 2021)."
```

Format legacy v1.0 (liste de strings plate) : **auto-traduit** par `benchmark-lead` en cadrage,
avec flag `legacy_dealbreakers_translated: true` dans le scope.yaml.

### Logique Phase 0

Pour chaque vendor × règle dealbreaker :

1. Évaluer la règle à partir des données de la fiche `vendor-deep-dive`.
2. Verdict ∈ `{pass, violated, unknown}`.
3. Si `violated` et `verdict_if_violated == excluded` : vendor basculé dans le bucket
   `exclus_dealbreaker` **sans score pondéré** (pas de faux score de 2/5 pour donner
   l'illusion d'un classement).

### Buckets v1.3 (4 au lieu de 3)

| Bucket | Condition | Score pondéré ? |
|---|---|---|
| `exclus_dealbreaker` (**nouveau**) | Au moins 1 dealbreaker violated | Non — le vendor sort du ranking |
| `classement_principal` | Completeness ≥ 0.80 ET aucun dealbreaker violated | Oui |
| `a_approfondir` | 0.50 ≤ completeness < 0.80 | Oui, mais hors ranking principal |
| `donnees_insuffisantes` | Completeness < 0.50 | Non |

### Audit trail

Produire `outputs/<run_id>/scoring/dealbreaker-check.json` :

```json
{
  "executed": true,
  "rules_evaluated": [
    {"id": "db_hosting_eu", "rule": "...", "source_required": true}
  ],
  "vendors_excluded": [
    {
      "vendor_id": "vendor-a",
      "rule_violated": "db_hosting_eu",
      "evidence": "Hébergement AWS us-east-1 uniquement (page Architecture, consulté 2026-04-21)",
      "source_url": "https://vendor-a.com/architecture"
    }
  ],
  "vendors_pass": ["vendor-b", "vendor-c"],
  "vendors_unknown": [
    {"vendor_id": "vendor-d", "rule": "db_hosting_eu", "reason": "page architecture non trouvée"}
  ]
}
```

### Persistance dans `bench.json`

- `exec_summary.exclus_dealbreaker: [actor_id, ...]` (liste des exclus)
- Pour chaque actor exclu : `actors[i].dealbreaker_verdict: "violated"` +
  `actors[i].dealbreaker_violations: [{rule_id, evidence, source_id}]`
- Les acteurs `violated` n'ont pas de `weighted_score` ni de `rank`.

### Règles Phase 0

1. **Toujours exécuter si `scope.yaml.dealbreakers` non vide.** Ne pas "sauter" au motif que
   la mission est pressée.
2. **`source_required: true` → verdict `unknown` si pas de source.** Ne jamais supposer la
   conformité.
3. **Produire `dealbreaker-check.json`** même si `vendors_excluded` est vide (audit).
4. **Mention explicite dans le critic** : si un vendor `violated` apparaît dans
   `classement_principal` ou `a_approfondir`, le critic doit émettre un **SEV1**.
