---
name: market-scanner
description: "Use when the user needs to discover all relevant solutions on a given market or use case. Triggers: 'quelles solutions existent pour', 'benchmark de solutions', 'mapping du marché', 'landscape analysis', 'panorama éditeurs'. Produces an exhaustive list of vendors, startups, and open-source alternatives."
---

# Market Scanner

## Overview

À partir d'un cas d'usage ou d'une description de marché, produire une liste **exhaustive** de
10 à 30 solutions candidates (éditeurs commerciaux + open source + startups) avec leurs
métadonnées de découverte.

**Principe directeur** : on ne sait pas quelle est la meilleure solution tant qu'on n'a pas vu
large. Une exploration qui tient sur 3 résultats Google passe à côté de 80 % du marché.

## When to Use

- L'utilisateur demande un benchmark de marché.
- L'utilisateur cherche à cartographier un segment (RAG d'entreprise, IA conversationnelle,
  data gouvernance, OCR médical, etc.).
- Besoin d'une liste candidate avant tout scoring.

**Ne pas utiliser** :
- Si l'utilisateur a déjà une short-list nommée — passer directement à `vendor-deep-dive`.
- Pour des questions factuelles ponctuelles — utiliser `fact-checker`.

## Méthode — 5 angles obligatoires

Tu lances **au minimum 5 requêtes web sous angles différents** :

| # | Angle                               | Exemple de requête                                       |
|---|-------------------------------------|----------------------------------------------------------|
| 1 | Leaders mondiaux                    | "top RAG platforms enterprise 2025 Gartner"              |
| 2 | Acteurs français / européens        | "plateforme RAG France éditeur souverain 2025"           |
| 3 | Open source                         | "open source RAG framework production"                   |
| 4 | Startups récentes                   | "RAG startup seed series A 2024 2025"                    |
| 5 | Solutions transversales / adjacentes| "vector database enterprise search LLM platform"         |

Pour chaque angle : scan des 10 premiers résultats, extraction des noms de solutions citées.
Déduplication à la fin.

## Output — JSON structuré

```json
[
  {
    "nom": "string",
    "editeur": "string",
    "url": "https://...",
    "categorie": "RAG platform | Vector DB | LLM gateway | ...",
    "region_siege": "France | Europe | US | Canada | ...",
    "type_solution": "SaaS | Self-hosted | Open source | Hybrid",
    "source_decouverte": "Gartner MQ 2024 | G2 | recherche web angle 2 | ..."
  }
]
```

## Règles

1. **Jamais moins de 5 requêtes.** Si une requête ramène 0 résultat pertinent, tu en lances une
   autre sur le même angle avec une reformulation.
2. **Toujours inclure des acteurs FR/EU.** Si le marché est dominé par les US, tu le signales
   mais tu maintiens des candidats FR/EU dans la liste, même mineurs.
3. **Signaler explicitement la concentration** quand un marché est dominé par 1-2 acteurs
   (ex : Palantir sur la gouvernance data santé US).
4. **Dédupliquer correctement** : "Azure OpenAI" et "Microsoft Copilot" ne sont pas la même
   solution même si le même éditeur.

## Quick Reference

| Critère            | Seuil attendu              |
|--------------------|----------------------------|
| Nb requêtes web    | 5 minimum                  |
| Nb solutions brut  | 15-50                      |
| Nb solutions dedup | 10-30                      |
| % solutions FR/EU  | ≥ 20 % si marché permet    |
| % open source      | ≥ 10 % sauf niche fermée   |

## Common Mistakes

- **Se limiter aux 3 premiers résultats Google.** Tu passes à côté des challengers et des
  solutions régionales.
- **Oublier les solutions open source.** Sur presque tous les marchés IA/data, il existe une
  alternative open source sérieuse.
- **Confondre "solution" et "éditeur".** Un éditeur peut proposer 3 solutions distinctes
  (ex : Microsoft → Azure OpenAI, Copilot Studio, Fabric). Chacune est une entrée séparée.
- **Ne pas dater la découverte.** Le marché IA évolue trimestriellement — sans date, la liste
  périme vite.

## Anti-pattern

```
❌  "Je connais les 3 leaders, je saute l'étape de market-scanner."
✅  "Je lance 5 requêtes même si je crois connaître le marché. Les 6 derniers mois
    ont probablement vu émerger 2-3 acteurs que je ne connais pas."
```
