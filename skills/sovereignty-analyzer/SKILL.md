---
name: sovereignty-analyzer
description: "Use for markets in regulated sectors (health, defense, public, finance) to analyze the full sovereignty stack of a solution. Triggers: 'analyse de souveraineté', 'dépendances US', 'Cloud Act', 'solution souveraine', 'RGPD extraterritorial'. Produces a 4-layer analysis with a global verdict."
---

# Sovereignty Analyzer

## Overview

Pour chaque éditeur, analyser **4 couches de souveraineté** et rendre un verdict global
(SOUVERAIN / MIXTE / NON-SOUVERAIN). Obligatoire dès qu'on travaille pour un client en
secteur régulé (santé, finance, défense, public).

**Principe directeur** : la souveraineté ne se revendique pas, elle se démontre. Un éditeur
français qui fait tourner ses modèles sur Azure US **n'est pas souverain** — même si son
marketing le dit.

## When to Use

- Tout benchmark en secteur régulé (automatique).
- Tout benchmark impliquant des données sensibles (personnelles, santé, défense, IP).
- Quand le client mentionne Cloud Act, souveraineté, indépendance stratégique, RGPD
  extraterritorial.

## Les 4 couches à analyser

### Couche 1 — Propriété capitalistique
- Siège social de la maison mère.
- Structure actionnariale : qui détient le capital, à quels pourcentages.
- Cotation en bourse (laquelle) ou privée.
- Présence de fonds US / chinois / non-UE dans le capital.
- Golden share d'État, droits de véto.

**Sources** : Pappers / Infogreffe (FR), Companies House (UK), SEC (US), bilans annuels.

### Couche 2 — Hébergement des données
- Cloud provider utilisé (Azure, AWS, GCP, OVH, Scaleway, 3DS Outscale, ...).
- Localisation physique des datacenters utilisés par la solution.
- Applicabilité du **Cloud Act** (tout provider de droit US, même avec des DC en UE).
- Certification HDS si données de santé.
- Possibilité de déploiement on-premise.

### Couche 3 — Modèles IA utilisés
- Fournisseurs des modèles : OpenAI, Anthropic, Mistral, Meta/Llama, Cohere, propriétaire, ...
- Où tournent les inférences (pays, provider).
- Provenance des données d'entraînement.
- Si fine-tuning : où, sur quelle infra.

### Couche 4 — Dépendances techniques
- APIs critiques externes (Stripe, Twilio, Salesforce, ...).
- Briques de sécurité (Okta, Auth0, Cloudflare, ...).
- Sous-traitants clés (dev offshore, support, ...).
- Librairies open source avec gouvernance critique (ex : dépendance à un seul mainteneur US).

## Output — JSON structuré

```json
{
  "editeur": "...",
  "date_analyse": "2026-04-16",
  "couche_1_capital": {
    "siege": "Paris, France",
    "actionnariat_principal": [
      { "actionnaire": "Fondateurs", "pct": 55, "nationalite": "FR" },
      { "actionnaire": "Fonds Accel (US)", "pct": 30, "nationalite": "US" }
    ],
    "cotation": "Non coté",
    "risque": "Moyen — présence fonds US 30%",
    "sources": []
  },
  "couche_2_hebergement": {
    "cloud_principal": "Azure France Central",
    "cloud_act_applicable": true,
    "certif_HDS": "non",
    "on_premise_possible": false,
    "risque": "Élevé — Azure est de droit US, Cloud Act applicable même en France",
    "sources": []
  },
  "couche_3_modeles": {
    "modeles_utilises": ["GPT-4o (OpenAI)", "Mistral Large"],
    "inference_location": "US (OpenAI) + France (Mistral)",
    "risque": "Élevé — GPT-4o implique traitement US",
    "sources": []
  },
  "couche_4_dependances": {
    "apis_critiques": ["Stripe (US)", "Auth0 (US)"],
    "risque": "Moyen",
    "sources": []
  },
  "verdict_global": "NON-SOUVERAIN",
  "verdict_justification": "Siège FR mais 30% capital US, cloud Azure (Cloud Act), modèles principaux US. Éditeur français de façade, chaîne technique US.",
  "alternatives_plus_souveraines": ["Editeur X (modèle Mistral + cloud OVH)"]
}
```

## Matrice de verdict global

| C1 Capital | C2 Cloud        | C3 Modèles      | C4 Deps | Verdict         |
|------------|-----------------|-----------------|---------|-----------------|
| FR/UE      | UE non-Cloud Act| UE              | UE      | SOUVERAIN       |
| FR/UE      | Cloud Act ou UE mixte | UE mixte  | UE      | MIXTE           |
| Non-UE ou  | Cloud Act       | US              | US      | NON-SOUVERAIN   |

Un seul élément US critique (cloud principal Cloud Act, modèle principal US) suffit à basculer
en MIXTE ou NON-SOUVERAIN. C'est la règle du maillon faible.

## Règle absolue

**Un éditeur français dont les modèles tournent sur Azure US n'est PAS souverain.** Tu le dis.
Même si son marketing claim "solution souveraine". Le marketing n'est pas un argument.

## Common Mistakes

- **Accepter "cloud France" sans vérifier le provider.** Azure France Central reste Azure
  (droit US, Cloud Act). Seuls OVH, Scaleway, 3DS Outscale, Clever Cloud, Numspot, Bleu et S3ns
  sont de droit français.
- **Oublier la couche modèles.** Un éditeur FR/cloud souverain qui utilise GPT-4 en backend
  n'est pas souverain sur la donnée inférée.
- **Confondre RGPD et souveraineté.** Une solution peut être RGPD-compliant ET Cloud Act
  applicable. Le RGPD ne protège pas du Cloud Act.
- **Prendre le mot "souverain" pour argent comptant.** Demande la preuve sur les 4 couches.

## Quick Reference — providers cloud par statut

**Droit français** : OVH, Scaleway, 3DS Outscale, Clever Cloud, Numspot, Bleu (JV Orange /
Capgemini / Microsoft — en instance SecNumCloud), S3ns (JV Thales / Google — en instance).

**Droit US, Cloud Act** : AWS, Azure, GCP, Oracle Cloud, IBM Cloud, Alibaba (même les régions
FR/UE).
