# Workflow — Benchmark de marché (bout-en-bout)

Ce workflow décrit la mission type "benchmark de solutions X pour cas d'usage Y dans secteur Z"
réalisée pour un client Ascend. Durée totale : 45 à 90 minutes selon profondeur.

## Pré-requis

- Demande cadrée avec le client : cas d'usage, secteur, nombre de solutions cible, grille
  retenue (ou grille à créer).
- Accès Firecrawl MCP configuré (optionnel mais fortement recommandé).
- Grille de scoring JSON choisie dans `scoring-grids/`.

---

## Étape 1 — Cadrage client (avant lancement)

Avant de lancer le moindre agent, tu alignes avec l'utilisateur sur :

1. **Cas d'usage** — 1 à 5 cas d'usage précis. Exemple : "chatbot pour bénéficiaire mutuelle"
   est trop flou ; "agent conversationnel 24/7 qui répond aux questions de remboursement
   niveau 1 sur canaux web + mobile, intégré au CRM existant" est exploitable.
2. **Secteur** — détermine si `sovereignty-analyzer` est obligatoire et si une grille
   `regulated` doit être préférée à `enterprise-saas`.
3. **Grille de scoring** — référence à un JSON existant, ou co-création.
4. **Pondérations** — validation des poids de la grille avec le client (non négociable ensuite).
5. **Nombre de solutions cible** — 5 (quick), 10 (standard), 15+ (panorama).
6. **Contraintes** — exclusions (éditeurs bannis RSE/juridique), musts (éditeur FR seulement,
   cloud souverain uniquement, etc.), budget temps.

**Livrable intermédiaire** : 1 paragraphe de cadrage validé par l'utilisateur, sauvegardé en
début de rapport final.

---

## Étape 2 — Chargement / création de la grille

- Si grille existe dans `scoring-grids/` : la lire, présenter à l'utilisateur pour validation
  des poids.
- Si grille à créer : la construire à partir de `enterprise-saas.json` comme base, adapter les
  critères, soumettre à validation.
- **Règle** : poids total = 1.0 (somme des weights).

---

## Étape 3 — Cadrage (optionnel) avec `benchmark-lead`

Le mainthread peut dispatcher `benchmark-lead` en mode cadrage pour structurer la demande
et proposer un plan :

```
Agent({
  description: "Cadrage benchmark",
  subagent_type: "benchmark-lead",
  prompt: "Mode cadrage. Demande : <texte>. Produis plan + questions utilisateur + estimation N sub-agents."
})
```

**benchmark-lead ne dispatche aucun autre sub-agent** (limitation native Claude Code) — il
retourne le plan au mainthread qui exécute. Voir `workflows/orchestrate-benchmark.md`.

---

## Étape 4 — Revue de la short-list (checkpoint)

**Point d'arrêt obligatoire** après phase discovery. Le mainthread présente à l'utilisateur :

- Nombre de solutions identifiées (brut et après dédup).
- Répartition géographique (FR / UE / US / autre).
- Répartition commerciale vs open source.
- Solutions hésitantes (à inclure ou exclure).

**L'utilisateur valide** la short-list avant lancement des investigators (coût significatif).

---

## Étape 5 — Investigation et scoring

Le mainthread Claude Code dispatche en parallèle, **dans un seul message** :

- `investigator` × N (1 par solution short-listée, jusqu'à 15 en simultané).

Puis applique `weighted-scorer` (skill, en ligne — pas de sub-agent).

Puis dispatche `critic` × 1 séquentiellement.

**Si le critic remonte des items BLOQUANTS** : boucle de complétion — le mainthread
redispatch les investigators concernés, puis relance critic.

Détails : `workflows/orchestrate-benchmark.md`.

---

## Étape 6 — Red teaming

Une fois critic satisfait, le mainthread dispatche `red-teamer` × 1 sur les top 3.
Livrable : 3 personas × 3+ arguments contre + verdict tranché (TIENT / À NUANCER / REFAIRE).

**Si un verdict est REFAIRE** : le top 3 est ajusté (le #4 monte), le red-teamer repasse.

---

## Étape 7 — Production des livrables

### 7.1 — Tableau Excel (spec `templates/benchmark-output.xlsx.md`)
- 5 onglets : Synthèse, Scoring détaillé, Fiches éditeurs, Sources, Méthodologie.
- Formatage : headers couleur selon charte client, freeze panes, filtres
  auto, conditional formatting sur les notes.
- Formules : pondération dynamique (si le client veut modifier les poids en réunion).

### 7.2 — Note de synthèse exécutive (spec `templates/executive-brief.docx.md`)
- 10 pages max.
- Structure : exec summary (1 page) / méthodologie / top 5 + matrice / annexes.
- Styles Word cohérents avec la charte Ascend.

### 7.3 — Rapport de benchmark (markdown)
- Plan de cadrage initial.
- Rapport critic intégral.
- Rapport red-teamer intégral.
- Checklist de livraison (CLAUDE.md) cochée.

---

## Étape 8 — QA final

Checklist de sortie (copie de CLAUDE.md, adapter) :

- [ ] Toutes les données critiques sourcées niveau 4-5.
- [ ] Rapport critic traité (bloquants résolus).
- [ ] Red teaming passé sur top 3.
- [ ] Sources taguées par niveau.
- [ ] Souveraineté analysée si secteur régulé.
- [ ] Livrable Excel et Word conformes templates.
- [ ] Français correct (accents).
- [ ] Données client anonymisées si nécessaire.
- [ ] Aucun `N/D` sans justification.

---

## Itérations post-livraison

Le consultant présente en COPIL. Le client fait 3 types de retours :

1. **"Ajoutez la solution X"** → nouveau `investigator` en mode isolé, puis recalcul du
   scoring, puis mise à jour Excel.
2. **"Changez les poids"** → recalcul du `weighted-scorer` uniquement, régénération des
   livrables.
3. **"Vérifiez que Y est vraiment certifié"** → `fact-checker` ciblé, mise à jour fiche.

Le stack est conçu pour absorber ces itérations sans refaire tout le benchmark.

---

## Budget temps indicatif

| Phase                   | Durée        |
|-------------------------|--------------|
| Cadrage + grille        | 10-15 min    |
| Discovery parallèle     | 15 min       |
| Validation short-list   | 5 min        |
| Investigation parallèle | 20-30 min    |
| Scoring + critic        | 10 min       |
| Red teaming             | 10 min       |
| Livrables               | 10-15 min    |
| QA                      | 5 min        |
| **Total**               | **85-105 min** |

Pour un benchmark quick (5 solutions, pas de red teaming), compter 25-40 min.
