# Prompt — Benchmark standard (interne Ascend)

> **Mode intermédiaire** entre `benchmark-quick` (draft) et `benchmark-full` (livrable client).
>
> Passage au critic obligatoire, **pas** de red-team. Destiné à un **brief interne Ascend**
> ou à un **draft avancé** avant la version finale client. Livrable xlsx + docx générable,
> mais sans checklist pre-delivery niveau 4 cochée.
>
> - Explorer / dégrossir → `prompts/benchmark-quick.md`
> - Livrable client / COPIL → `prompts/benchmark-full.md`

Timebox 45-60 minutes. Bon compromis profondeur / vitesse pour un consultant qui veut
un draft défendable en interne avant de l'affiner en mode full pour le client.

À utiliser quand : le consultant prépare un brief interne, valide un périmètre
avec un partner, ou produit une v1 avancée avant la passe finale full.

---

```
Démarre un benchmark STANDARD (mode interne Ascend) selon workflows/market-benchmark.md.

CONTEXTE CLIENT
Client : {nom}
Marché : {description_courte}
Secteur régulé : {oui/non}
Mission : {nature de la préparation — "brief interne avant proposition", "draft v1",
           "validation périmètre partner", etc.}

CAS D'USAGE
{1 à 5 cas d'usage, même niveau de précision que benchmark-full}

GRILLE DE SCORING
Grille : scoring-grids/{nom_grille}.json
Pondérations : {préciser si modifiées, sinon "défaut grille"}

PÉRIMÈTRE ET CONTRAINTES
- Nombre de solutions par cas d'usage : {defaut 4-6}
- Périmètre géographique : {France / UE / Monde}
- Exclusions : {liste}
- Must-have : {liste}
- Budget Firecrawl : {defaut 10-15 scrapes}

MODE STANDARD — DIFFÉRENCES vs FULL
- Red teaming : SKIP (pas de personas × arguments contre sur top 3).
- Checklist pre-delivery niveau 4 : NON obligatoire (peut rester informelle).
- Livrables : xlsx + docx, mais marqués DRAFT - INTERNAL USE en en-tête.
- Critic : obligatoire (bloquants + avertissements, comme full).

MÉTHODOLOGIE
- Appliquer la méthodologie triple partage de la valeur Ascend si secteur
  mutualiste/santé.
- Souveraineté obligatoire (4 couches) pour chaque solution en secteur régulé.
- Checkpoint utilisateur après discovery (avant investigators).
- Rapport critic obligatoire, items bloquants à traiter avant fin de run.

TIMEBOX
45-60 minutes.

OBJECTIF
Livrer une v1 interne avec critic. Le red-teaming et la validation niveau 4
seront ajoutés en mode full avant envoi client.

GO.
```

---

## Quand passer au mode full

| Déclencheur | Action |
|---|---|
| Le draft standard part en COPIL client | Relancer en `benchmark-full.md` sur le même panel, ne regénérer que red-team + checklist. |
| Un item bloquant du critic pointe un risque reco | Mode full obligatoire avant toute recommandation finale. |
| Le partner demande un red-team | Mode full. |
| La reco top 3 engage budget > 500 k€ ou impact stratégique | Mode full obligatoire. |
