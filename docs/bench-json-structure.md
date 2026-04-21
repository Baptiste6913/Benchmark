# Structure canonique `bench.json`

**Introduit en v1.1.0.** Source de vérité unique d'un bench Ascend-Bench. À partir de
la v1.2.0 (Sprint 2), les livrables xlsx + docx sont générés à partir de ce JSON via
`lib/render.py`. Le MD reste un artefact intermédiaire — pas la source autoritative.

## Pourquoi une structure canonique ?

Avant la v1.1.0, chaque bench produisait un `.md` artisanal et un `.xlsx` via un script
Python ad-hoc (ex : `examples/generic-demo/_build_xlsx.py`). Conséquences :

- Impossible de **regénérer** automatiquement les livrables si la grille change.
- Impossible de **comparer** deux versions d'un bench (v1 LISI vs v2 LISI) de façon
  structurelle — il faut lire les diffs MD à la main.
- Impossible de **valider** programmatiquement qu'un bench est complet.
- Impossible de **partager** un bench entre consultants sans envoyer les scripts.

`bench.json` résout ces quatre points.

## Emplacement

- **Schéma** : `schemas/bench.schema.json` (JSON Schema Draft 2020-12).
- **Validator** : `scripts/validate_bench.py` (utilise `jsonschema`).
- **Exemple de référence** : `examples/generic-demo/bench.json`.

## Squelette

```jsonc
{
  "meta": { "client", "mission", "date", "version", "mode", "methodology", "consultant" },
  "grid_ref": "scoring-grids/<name>.json",
  "exec_summary": {
    "context": "…",
    "three_takeaways": ["…", "…", "…"],
    "weak_signals": ["…"],
    "ranking": [{ "rank", "actor_id", "weighted_score", "positioning" }]
  },
  "actors": [
    {
      "id": "slug-a-z-0-9",
      "name": "Nom complet",
      "positioning_one_liner": "…",
      "tldr": { "score", "verdict", "positioning", "stack_emblematique" },
      "context": "Paragraphe contexte + déclencheur",
      "flagship_quote": { "text", "author", "date", "source_id" },
      "strategy": { "infra", "models", "data_gov", "org" },
      "key_figures": [{ "metric", "value", "date", "source_ids" }],
      "maturity_and_approach": "…",
      "scoring": [
        { "criterion_id", "score", "weight", "justification", "source_ids",
          "revision_note": "optionnel si score révisé en red-team" }
      ],
      "weighted_score": 4.60,
      "rank": 1,
      "blind_spots": [{ "num", "text", "severity" }],
      "red_team_verdict": "OK | TIENT LA ROUTE | À NUANCER | REFAIRE | N/A",
      "information_gaps": ["…"],
      "added_in_version": "v2",        // optionnel — acteur ajouté tardivement
      "notes": "…"
    }
  ],
  "sources": [
    { "id", "actor_ref", "title", "author", "date", "url", "type", "reliability" }
  ],
  "critic": {
    "blocking": [{ "num", "text", "actor_ref" }],
    "warnings": [{ "num", "text" }],
    "observations": [{ "num", "text" }]
  },
  "red_team": {
    "patterns": ["…"],
    "verdicts": { "actor_id": "À NUANCER" },
    "messages_to_comex": ["…"],
    "details_per_actor": {
      "actor_id": {
        "persona_1_arguments": ["…"],
        "persona_2_arguments": ["…"],
        "persona_3_arguments": ["…"],
        "verdict": "…",
        "verdict_justification": "…",
        "alternative": "…",
        "impact_client": ["…"]
      }
    }
  },
  "transverse": {
    "patterns_communs": ["…"],
    "two_paths_table": {
      "dimensions": ["…"],
      "remediation": ["…"],
      "by_design": ["…"],
      "hybrid": ["…"]
    },
    "ai_impact": "…"
  },
  "recommendations": [
    { "id": "R1", "title": "…", "body": "…", "caveats": "…" }
  ]
}
```

## Champs obligatoires vs optionnels

**Obligatoires au niveau racine** : `meta`, `grid_ref`, `actors`, `sources`.

**Obligatoires par acteur** : `id`, `name`, `weighted_score`, `rank`, `scoring`.

**Conditionnellement obligatoires** (selon le mode) :

| Mode     | `critic` | `red_team` | `transverse` | Checklist pre-delivery |
|----------|----------|------------|--------------|------------------------|
| quick    | optionnel| non        | optionnel    | non                    |
| standard | **oui**  | non        | **oui**      | non                    |
| full     | **oui**  | **oui**    | **oui**      | **oui (externe au JSON)** |

Le validateur `scripts/validate_bench.py` vérifie aujourd'hui le schéma JSON et quelques
règles croisées (références source_id, actor_id, somme des poids par acteur). Les règles
par mode ne sont **pas encore durcies** — prévu en Sprint 2.

## Règles croisées validées

Le validator `scripts/validate_bench.py` complète le JSON Schema avec :

- Chaque `source_id` référencé dans `actors[].key_figures[].source_ids`,
  `actors[].scoring[].source_ids` ou `actors[].flagship_quote.source_id` doit exister
  dans `sources[]`.
- Chaque `actor_id` dans `exec_summary.ranking`, `red_team.verdicts`,
  `red_team.details_per_actor` ou `critic.*.actor_ref` doit exister dans `actors[]`.
- Si `actors[].scoring[].weight` est fourni pour tous les critères d'un acteur, la somme
  doit être proche de 1.0 (±0.01).

## Exemple complet

`examples/generic-demo/bench.json` est le bench LISI v2 migré dans cette
structure. Il sert de test de non-régression : si tu ajoutes ou modifies le schéma,
ce fichier doit rester valide (ou on migre explicitement).

Commande de validation :

```bash
python scripts/validate_bench.py examples/generic-demo/bench.json
# → [ ok ] ... conforme au schéma — mode=full, 6 acteur(s), 44 source(s).
```

## Convention d'IDs

- `actor.id` : slug kebab-case ASCII (`^[a-z0-9][a-z0-9-]*$`). Ex : `dassault`,
  `schwarz-digits`, `amundi-alto`.
- `source.id` : slug kebab-case. Convention : `<actor-slug>-<numéro>`. Ex : `dassault-1`,
  `ovh-10`. Globales/transverses : préfixe `global-`.
- `recommendation.id` : `R1`, `R2`, … (`^R[0-9]+$`).
- `critic_item.num`, `blind_spot.num` : entier positif, continu dans sa section.

## Migration depuis un ancien bench (MD + XLSX)

Pour migrer un bench existant vers `bench.json` (ex : FNMF GT2-IA) :

1. Copier `examples/generic-demo/bench.json` comme template.
2. Remplir `meta`, `grid_ref`, `exec_summary`.
3. Pour chaque acteur du MD : créer l'objet dans `actors[]`.
4. Pour chaque source de l'annexe : créer l'objet dans `sources[]`.
5. Lancer `python scripts/validate_bench.py <bench.json>`.
6. Corriger les erreurs jusqu'à ce que le validator retourne `[ ok ]`.
7. Committer avec un message `migrate: <mission> from markdown to bench.json`.

À partir de la v1.2.0 (Sprint 2), étape 7bis : `python -m lib.render bench.json` pour
regénérer xlsx + docx. Les deux doivent être bit-for-bit reproductibles à partir du JSON.

## Roadmap

- **v1.1.0 (actuel)** : structure + schéma + validator + exemple LISI migré.
- **v1.2.0 (Sprint 2)** : générateur `lib/render.py` qui produit xlsx + docx à partir de
  `bench.json`. Workflow `rescore-after-change.md` qui recalcule et régénère en une
  commande.
- **v1.3.0+ (Sprint 3+)** : durcissement des règles par mode, CI qui valide tous les
  `examples/*/bench.json`, outil de diff structurel entre deux versions d'un bench.
