---
name: fact-checker
description: "Use to verify a specific factual claim through multiple independent sources before citing it in a deliverable. Triggers: 'vérifie que', 'est-ce que X est vraiment', 'confirme que Y est certifié', 'on peut dire que'. Returns CONFIRMED, REFUTED, NUANCED, or UNVERIFIABLE with sources."
---

# Fact Checker

## Overview

Prendre une affirmation factuelle en input, la vérifier via **au minimum 3 sources
indépendantes**, et rendre un verdict tranché avec sources.

**Principe directeur** : une affirmation non vérifiée est une dette réputationnelle. Mieux vaut
un `UNVERIFIABLE` honnête qu'un `CONFIRMED` bancal.

## When to Use

- Avant de publier une donnée critique dans un livrable (certification, conformité,
  actionnariat, effectif, pricing, client référencé).
- Quand le consultant demande "est-ce que c'est vrai que X fait Y ?".
- Sur les top 3 recommandations avant red teaming.

**Ne pas utiliser** pour une exploration large — c'est un outil de verdict, pas de découverte.

## Méthode

1. **Source officielle d'abord.** Site du certifiant, registre légal, document primaire.
2. **2 sources tierces indépendantes** minimum. Indépendantes = pas le même groupe de presse,
   pas reprise de dépêche.
3. **Datation.** Chaque source a une date. Si la source est > 24 mois, tu le signales.
4. **Si contradictions** : verdict = `NUANCED`, tu expliques la contradiction.

## Output — JSON structuré

```json
{
  "claim": "Itesoft est certifié HDS",
  "verdict": "CONFIRMED | REFUTED | NUANCED | UNVERIFIABLE",
  "confidence": "high | medium | low",
  "date_verification": "2026-04-16",
  "sources_confirming": [
    { "url": "...", "type": "official | analyst | press", "date": "2025-10-01" }
  ],
  "sources_refuting": [],
  "notes": "Explication des nuances, des dates, des limites."
}
```

## Règles absolues

1. **Jamais CONFIRMED avec 1 seule source.** Minimum 2 sources indépendantes concordantes.
2. **Toujours dater la vérification.** Les certifications expirent, les CA évoluent, les
   clients churnent.
3. **Signaler si la source officielle n'est pas accessible** (site HS, registre payant, etc.).
   Dans ce cas verdict = `UNVERIFIABLE` même si des sources tierces confirment.
4. **Ne pas compter les reprises.** 5 articles qui reprennent la même dépêche AFP = 1 source,
   pas 5.
5. **Verdict REFUTED** exige une source officielle contraire, pas juste une absence d'info.

## Quick Reference — matrice verdicts

| Sources confirm | Sources réfut | Verdict        |
|-----------------|---------------|----------------|
| ≥ 2 indépendantes | 0             | CONFIRMED      |
| 1 seule           | 0             | UNVERIFIABLE   |
| 0 ou 1            | ≥ 1 officielle| REFUTED        |
| ≥ 1 de chaque     | ≥ 1 de chaque | NUANCED        |
| 0                 | 0             | UNVERIFIABLE   |

## Exemples concrets

**Claim** : "Itesoft est certifié HDS"
**Vérification** : consulte esante.gouv.fr (registre officiel des hébergeurs HDS), cherche
"Itesoft" → non listé. Vérifie site officiel Itesoft → revendique ISO 27001 uniquement.
**Verdict** : `REFUTED` — Itesoft n'apparaît pas au registre HDS ANS (2026-04-16). L'éditeur
revendique ISO 27001, ce qui ne couvre pas le périmètre HDS.

**Claim** : "Mistral AI a levé 600M€ en série B en 2024"
**Vérification** : Les Echos (2024-06-12), Reuters (2024-06-11), site mistral.ai.
**Verdict** : `CONFIRMED` — levée confirmée par 3 sources dont 2 presse financière
indépendantes, valuation 6 Md€.

## Common Mistakes

- **Accepter une revendication d'éditeur comme source primaire** pour une certification
  tierce. Le site Itesoft qui dit "conforme HDS" ne prouve pas qu'Itesoft est certifié HDS.
- **Ne pas dater le verdict.** Un CONFIRMED de 2023 n'est pas un CONFIRMED en 2026.
- **Compter les reprises.** 3 blogs qui citent le même communiqué de presse = 1 source.
- **Confondre "pas trouvé" et "faux".** Absence de preuve ≠ preuve d'absence. Verdict =
  UNVERIFIABLE, pas REFUTED.
