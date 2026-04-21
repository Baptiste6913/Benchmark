# Prompt — Benchmark quick (DRAFT, exploration interne)

> ⚠ **DRAFT — NOT FOR CLIENT DELIVERY**
>
> Ce mode produit un livrable **interne d'exploration uniquement**. Pas de critic, pas
> de red-team, pas de validation niveau 4. **Ne jamais envoyer tel quel à un client ni
> en COPIL.**
>
> - Livrable client / COPIL → `prompts/benchmark-full.md`
> - Brief interne avec critic (sans red-team) → `prompts/benchmark-standard.md`
> - Dégrossir / scanner / préparer une réunion → ce fichier

Version allégée pour valider une hypothèse, identifier les acteurs majeurs d'un marché
ou préparer une réunion d'alignement. Timebox 20-40 minutes.

À utiliser quand : le consultant a besoin d'un scan initial avant une réunion,
pour dégrossir un marché, ou pour valider une hypothèse rapidement.

---

```
Démarre un benchmark QUICK (mode DRAFT exploration) selon workflows/market-benchmark.md.

CONTEXTE CLIENT
Client : {nom}
Marché : {description_courte}
Secteur régulé : {oui/non}

CAS D'USAGE
{1 à 3 cas d'usage maximum, formulation courte}

GRILLE DE SCORING
Grille : scoring-grids/{nom_grille}.json (pondérations : défaut)

MODE QUICK — OPTIMISATIONS
- 3 solutions par cas d'usage maximum (pas 5-10).
- Discovery : 4 requêtes web au lieu de 5-6.
- Investigators : WebSearch + WebFetch uniquement, PAS de Firecrawl (budget 0).
- Scoring : weighted-scorer appliqué en ligne (pas de critic, pas de red-team).
- SKIP critic.
- SKIP red-teaming.
- SKIP checklist pre-delivery niveau 4.
- Livrable : tableau markdown uniquement (PAS d'xlsx ni de docx).

TIMEBOX
20-40 minutes.

OBJECTIF
Livrer un draft défendable EN INTERNE pour dégrossir le marché, valider un axe,
préparer une réunion d'alignement. Ce draft NE VA PAS en production client.

GO.
```

---

## Quand ne pas utiliser le mode quick

| Besoin | Mode à utiliser |
|---|---|
| Livrable client / COPIL | `prompts/benchmark-full.md` |
| Brief interne Ascend avec critic | `prompts/benchmark-standard.md` |
| Secteur très régulé + décision engagée | `prompts/benchmark-full.md` |
| > 3 cas d'usage | `prompts/benchmark-standard.md` ou `benchmark-full.md` |
| Client qui paie pour un benchmark premium | `prompts/benchmark-full.md` |

**Règle** : tout livrable qui sort du périmètre Ascend interne passe par `benchmark-full.md`.
