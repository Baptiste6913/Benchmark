---
name: source-credibility
description: "Use to evaluate the reliability of a source before citing it in a deliverable. Triggers: 'est-ce une source fiable', 'évalue cette source', 'on peut citer ça'. Returns a credibility score 1-5 and recommendations on whether the source is strong enough for the data point being asserted."
---

# Source Credibility

## Overview

Tagger chaque source utilisée avec un **niveau de fiabilité de 1 à 5**. Indispensable pour
savoir si une source est assez solide pour le type d'affirmation qu'elle appuie.

**Principe directeur** : toutes les sources ne se valent pas. Une certification tierce exige
une source primaire (niveau 5). Un ordre de grandeur marché peut se contenter d'un analyste
(niveau 4).

## When to Use

- À chaque fois qu'une source est citée dans `vendor-deep-dive` ou `fact-checker`.
- Avant publication du livrable, passe de contrôle sur toutes les sources du rapport.
- Quand le consultant demande "est-ce que cette source tient la route ?".

## Échelle de fiabilité (1-5)

| Niveau | Type                          | Exemples                                          |
|--------|-------------------------------|---------------------------------------------------|
| **5**  | Source primaire officielle    | esante.gouv.fr (HDS), CNIL, Pappers, Infogreffe, SEC filing, document PDF signé, site éditeur pour ses propres fonctionnalités |
| **4**  | Analyste reconnu              | Gartner Magic Quadrant, Forrester Wave, IDC, CB Insights, Xerfi |
| **3**  | Presse spécialisée tech       | Les Echos Tech, Usine Digitale, ZDNet, TechCrunch, 01net, Silicon.fr |
| **2**  | Presse généraliste            | Le Monde (article non spécialisé), Les Echos (hors Tech), BFM |
| **1**  | Blog, forum, avis isolé       | Medium perso, Reddit, G2 review unique, LinkedIn post |

## Règle clé : matching donnée ↔ niveau source

| Type de donnée                          | Niveau min requis |
|-----------------------------------------|-------------------|
| Certification tierce (HDS, ISO, SOC2)   | 5 (registre)      |
| Actionnariat, propriété capitalistique  | 5 (Pappers, SEC)  |
| Chiffre d'affaires, effectif            | 4-5 (Pappers + 1 tierce) |
| Nombre de clients                       | 3-4 (presse ou analyste) |
| Part de marché                          | 4 (analyste)      |
| Positionnement leader                   | 4 (MQ Gartner)    |
| Fonctionnalité produit                  | 5 (site éditeur)  |
| Cas d'usage client                      | 3-4 (case study + presse) |
| Tendance de marché                      | 3 (presse spé)    |

## Output — tagging

Sur chaque source, tu ajoutes :

```json
{
  "url": "...",
  "titre": "...",
  "date_publication": "2025-06-01",
  "niveau_fiabilite": 4,
  "justification_niveau": "Gartner MQ Data Governance 2025, référence analyste reconnue.",
  "suffisante_pour": ["positionnement leader", "part de marché"],
  "insuffisante_pour": ["certification HDS"]
}
```

## Anti-pattern critique

**Ne jamais accepter une affirmation commerciale de l'éditeur comme source primaire pour une
certification tierce.**

```
❌  Source : itesoft.com (niveau 5 car éditeur officiel)
    Donnée : "Itesoft certifié HDS"
    → FAUX raisonnement. Le site de l'éditeur est niveau 5 POUR SES PROPRES
      FONCTIONNALITÉS, pas pour des certifications tierces. Pour HDS il faut
      esante.gouv.fr.
```

## Common Mistakes

- **Surévaluer le site éditeur.** Niveau 5 oui, mais uniquement pour ses fonctionnalités.
  Pour tout ce qui est tiers (certif, prix de marché, comparatif concurrentiel), l'éditeur est
  niveau 2 (biaisé par construction).
- **Sous-évaluer les registres légaux.** Pappers, Infogreffe, CNIL, ANS, SEC sont niveau 5 —
  ce sont les sources les plus fiables qui existent.
- **Confondre popularité et fiabilité.** Un article très lu sur Medium reste niveau 1.
- **Ne pas dater.** Une source niveau 5 de 2019 peut être périmée (l'éditeur a perdu sa
  certification entre-temps).

## Quick Reference — cheat sheet matching

- Certif tierce → registre certifiant (5) ou attestation PDF signée (5).
- Actionnariat FR → Pappers / societe.com (5).
- Actionnariat US → SEC filings (5) ou Crunchbase premium (4).
- Leader position → Gartner / Forrester (4) ou Les Echos Tech (3).
- Pricing → site éditeur (5) ou demande commerciale (5) ou Vendr / analyst report (4).
