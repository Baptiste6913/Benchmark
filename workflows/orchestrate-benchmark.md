# Workflow — Orchestration d'un benchmark (mainthread)

> **Ce workflow s'adresse au MAINTHREAD Claude Code** (la session dans laquelle le
> consultant tape son prompt). Les sub-agents Claude Code ne peuvent pas dispatcher
> d'autres sub-agents ; l'orchestration parallèle est donc assurée ici, par le mainthread.
>
> Si tu es un sub-agent qui lit ce fichier par erreur : tu n'as pas à orchestrer.
> Retourne ton livrable spécifique au mainthread.

## Vue d'ensemble

```
MAINTHREAD (toi)
  │
  ├── (optionnel) Agent(benchmark-lead)  →  plan de cadrage
  │
  ├── Agent(discoverer) × N en parallèle  →  short-list brute
  │   │  (timebox 15 min chacun)
  │   ▼
  ├── [CHECKPOINT UTILISATEUR] validation short-list
  │
  ├── Agent(investigator) × N en parallèle  →  fiches vendor
  │   │  (timebox 20 min chacun)
  │   ▼
  ├── Applique weighted-scorer (skill, en ligne)  →  scoring pondéré
  │
  ├── Agent(critic) × 1  →  rapport critique (bloquants / avertissements)
  │   │
  │   └── Si bloquants : retourne vers investigator ciblé, puis relance critic
  │
  ├── Agent(red-teamer) × 1  →  verdicts top 3 (TIENT / À NUANCER / REFAIRE)
  │
  ├── (optionnel) Agent(benchmark-lead) mode consolidation  →  synthèse exécutive
  │
  ├── Valide workflows/pre-delivery-checklist.md
  │
  └── lib/render.py bench.json  →  xlsx + docx  (à partir de v1.2.0)
```

## Étapes détaillées

### Étape 1 — Cadrage (optionnel mais recommandé)

Dispatche un sub-agent `benchmark-lead` en mode cadrage :

```
Agent({
  description: "Cadrage benchmark X",
  subagent_type: "benchmark-lead",
  prompt: "Mode cadrage. Demande utilisateur : <texte>. Produis plan + questions + estimation N sub-agents."
})
```

Tu valides le plan avec l'utilisateur avant tout dispatch d'investigators (coût).

### Étape 2 — Discovery parallèle

Pour chaque cas d'usage identifié, dispatche un `discoverer` :

```
Agent({
  description: "Scout marché X",
  subagent_type: "discoverer",
  prompt: "Cas d'usage : ... / Secteur : ... / Géographie : ... / Min solutions : 10 / Timebox : 15 min"
})
```

**Parallélisation obligatoire** : jusqu'à 10 discoverers en simultané si plusieurs cas
d'usage. Envoie tous les appels `Agent` dans le **même message** pour dispatch concurrent.

### Étape 3 — Checkpoint short-list

Tu agrèges les sorties des discoverers (dédup, merge). Tu présentes la short-list à
l'utilisateur. **Pas de dispatch investigator sans validation** — ça consomme du budget
Firecrawl.

### Étape 4 — Investigation parallèle

Pour chaque solution validée, dispatche un `investigator` :

```
Agent({
  description: "Investigator <solution>",
  subagent_type: "investigator",
  prompt: "Solution : ... / URL : ... / Grille : scoring-grids/<name>.json / Marché régulé : true|false / Budget Firecrawl : 2 / Timebox : 20 min"
})
```

**Parallélisation** : jusqu'à 15 investigators concurrents. Un seul message, plusieurs
tool calls.

### Étape 5 — Scoring pondéré (skill, en ligne)

Le mainthread (toi) applique le skill `weighted-scorer` à l'ensemble des fiches + la
grille. Ce n'est **pas** un sub-agent — tu le fais toi-même parce que c'est déterministe
et léger. Le skill te dit comment :
- rejeter les scorings N/D non justifiés,
- appliquer les tie-breakers,
- produire un tableau classé.

### Étape 6 — Critic séquentiel

Dispatche un unique sub-agent `critic` :

```
Agent({
  description: "Critic benchmark",
  subagent_type: "critic",
  prompt: "Voici les fiches investigator + le scoring pondéré + la grille. Produis ton rapport selon ton playbook."
})
```

Si le rapport remonte des **items bloquants** : boucle — relance les investigators
concernés pour combler les gaps, puis relance le critic jusqu'à ce qu'il n'y ait plus
de bloquants (ou que le mainthread accepte les bloquants restants en les documentant).

### Étape 7 — Red-teaming sur top 3

Dispatche un unique sub-agent `red-teamer` :

```
Agent({
  description: "Red-team top 3",
  subagent_type: "red-teamer",
  prompt: "Voici les fiches du top 3 + le contexte client. Applique 3 personas × 3 args par persona. Verdict tranché."
})
```

Si un verdict est **REFAIRE** : le top 3 est recomposé (le #4 remonte). Tu relances le
red-teamer sur le nouveau top 3 uniquement pour l'entrant.

### Étape 8 — Consolidation (optionnel)

Dispatche `benchmark-lead` en mode consolidation pour obtenir la synthèse exécutive +
la checklist de livraison cochée :

```
Agent({
  description: "Consolidation finale",
  subagent_type: "benchmark-lead",
  prompt: "Mode consolidation. Artefacts : <liste>. Applique workflows/pre-delivery-checklist.md."
})
```

### Étape 9 — Validation niveau 4

Tu passes en revue `workflows/pre-delivery-checklist.md` une par une. Exceptions explicitées.
Pas de livrable client si une case obligatoire n'est pas cochée (ou exception justifiée par écrit).

### Étape 10 — Rendu xlsx + docx

À partir de v1.2.0, tu appelles `lib/render.py` :

```bash
python -m lib.render bench.json --grid scoring-grids/<name>.json --out examples/<mission>/
```

Génère les deux livrables client. Pas de PowerPoint (le consultant le fait).

## Règles

1. **Parallélisation obligatoire** aux étapes 2 et 4. Un seul message = multiples tool calls.
2. **Checkpoint utilisateur** à l'étape 3 — la phase 4 consomme du budget Firecrawl.
3. **Budget Firecrawl** : 2 scrapes max par investigator, 30 investigators max par mois.
4. **Jamais de livrable sans critic + red-teamer en mode Full.** Quick/Standard peuvent
   sauter red-teamer (cf. `CLAUDE.md` section modes).
5. **Checklist pre-delivery obligatoire** avant tout envoi client — pas de contournement.

## Common mistakes

- **Orchestrer depuis un sub-agent** — impossible, sub-agents sont terminaux.
- **Dispatcher les investigators avant validation short-list** — brûle du budget.
- **Oublier `weighted-scorer`** en passant directement à critic — tie-breakers mal appliqués.
- **Un seul Agent dispatch par message** quand plusieurs sont indépendants — perte de parallélisme.
