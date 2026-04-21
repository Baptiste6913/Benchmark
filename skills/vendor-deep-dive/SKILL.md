---
name: vendor-deep-dive
description: "Use when producing a comprehensive factsheet on a specific software vendor. Triggers: 'fiche éditeur', 'due diligence de X', 'analyse approfondie de l éditeur Y', 'tout savoir sur X'. Requires web search and ideally firecrawl MCP access to the vendor official site."
---

# Vendor Deep Dive

## Overview

Produire une **fiche éditeur de 1 page** avec tous les attributs clés sourcés individuellement.
C'est le cœur de tout benchmark : la qualité de la fiche détermine la qualité du scoring final.

**Principe directeur** : chaque champ de la fiche doit être défendable face à un client qui
demande "d'où vient cette info ?".

## When to Use

- Juste après `market-scanner`, une fiche par solution retenue.
- En entrée d'un `weighted-scorer` (le scoring lit les fiches).
- En mode "due diligence" pour creuser un éditeur unique.

**Ne pas utiliser** pour les questions factuelles ponctuelles — `fact-checker` suffit.

## Méthode

1. **Site officiel d'abord.** Si tu as accès à Firecrawl MCP, scrape 2 pages max :
   page produit + page pricing/conformité/certifications. Sans Firecrawl, WebFetch sur
   les mêmes pages.
2. **Cross-check web search.** Pour chaque revendication officielle (clients, certifs, CA),
   tu cherches une confirmation tierce (presse, analyste, registre officiel).
3. **Entreprise** : LinkedIn (effectif), societe.com / Pappers (CA, dirigeants, actionnariat
   pour les FR), Crunchbase (levées de fonds).
4. **Conformité** : site officiel du certifiant (ANS pour HDS, CNIL, ISO) quand possible.

## Output — JSON structuré

```json
{
  "identite": {
    "nom_solution": "...",
    "nom_editeur": "...",
    "siege_social": "...",
    "annee_creation": 2020,
    "effectif": 120,
    "site_web": "https://...",
    "sources": [{ "url": "...", "niveau_fiabilite": 5 }]
  },
  "produit": {
    "description_courte": "...",
    "cas_usage_principaux": ["..."],
    "modules": ["..."],
    "architecture_type": "SaaS | Self-hosted | Hybride",
    "sources": []
  },
  "clients": {
    "nombre_clients_declares": 80,
    "clients_references_citables": ["..."],
    "secteurs_representes": ["..."],
    "sources": []
  },
  "certifications": [
    {
      "nom": "HDS",
      "statut": "certifié | en cours | revendiqué | non",
      "organisme": "LNE",
      "date_obtention": "2023-06",
      "date_verification_claude": "2026-04-16",
      "source_url": "https://...",
      "niveau_fiabilite": 5
    }
  ],
  "tech": {
    "stack_ia": "...",
    "cloud_provider": "...",
    "modeles_utilises": ["..."],
    "api_publique": true,
    "sso_support": ["SAML", "OIDC"],
    "sources": []
  },
  "economie": {
    "modele_tarifaire": "par utilisateur | par volume | forfait | freemium",
    "fourchette_tarifaire": "...",
    "ca_2024": "Non communiqué",
    "levees_de_fonds": [],
    "actionnariat_connu": "...",
    "sources": []
  },
  "souverainete": {
    "remplir_via": "sovereignty-analyzer"
  },
  "points_forts": ["..."],
  "points_faibles": ["..."],
  "trous_information": ["..."]
}
```

## Règles de fiabilité

- **Chaque donnée** a un `source_url` et un `niveau_fiabilite` (1-5, voir `source-credibility`).
- **Champ `certifications`** : jamais noter "certifié" sur la seule base d'une page marketing.
  Exige site du certifiant ou document PDF officiel.
- **Revendication marketing ≠ certification.** Si l'éditeur écrit "compatible HDS" sans être
  certifié, statut = `revendiqué`, pas `certifié`.
- **Données financières** : effectif et CA exigent 2 sources indépendantes ou 1 source
  registre officiel (Pappers, Infogreffe).

## Quick Reference — statut certification

| Statut         | Preuve requise                                                    |
|----------------|-------------------------------------------------------------------|
| `certifié`     | URL du registre certifiant OU attestation PDF officielle datée    |
| `en cours`     | Déclaration publique datée + engagement vers certifiant nommé     |
| `revendiqué`   | L'éditeur le dit mais pas de preuve tierce trouvée                |
| `non`          | Absence confirmée (checké le registre du certifiant)              |
| `N/D`          | Pas cherché ou info manquante, à remonter                         |

## Common Mistakes

- **Inventer un effectif.** LinkedIn estime ; Pappers tranche. Si les deux divergent, tu
  écris "80 (LinkedIn) / 120 (Pappers 2024-12)".
- **Confondre ISO 27001 et HDS.** Ce ne sont pas les mêmes certifications, ni les mêmes
  périmètres. L'ISO 27001 n'autorise pas à héberger des données de santé.
- **Prendre la page "clients" d'un éditeur pour argent comptant.** Une logo wall n'est pas
  une liste de clients actifs — certains logos datent de 5 ans.
- **Oublier les trous d'information.** Le champ `trous_information` est obligatoire : il dit
  au critic où chercher.
