# Workflow — Due diligence éditeur (approfondie)

Ce workflow est utilisé quand le consultant doit produire une **analyse 360° sur un seul éditeur**
— pas un benchmark. Exemple : "Avant qu'on signe avec Dedalus, fais-moi une DD complète".

Durée : 30 à 60 minutes.

## Pré-requis

- Nom de l'éditeur confirmé.
- URL officielle.
- Motif de la DD (pré-contractuel, due diligence M&A, évaluation stratégique).
- Périmètre d'évaluation (tout ou focus : financier, technique, conformité).

---

## Étape 1 — Cadrage

Tu alignes avec le consultant sur :

1. **Éditeur précis** : groupe vs filiale vs produit. "Dedalus" = groupe, "DxCare" = produit,
   "Dedalus Biologie" = BU. Le scope change tout.
2. **Type de DD** :
   - **Pré-contractuelle** : focus risques (conformité, souveraineté, santé financière).
   - **M&A / investissement** : focus exhaustif (tout).
   - **Audit stratégique** : focus positionnement + perspectives.
3. **Profondeur** : surface (15 min) / standard (30 min) / approfondie (60+ min).
4. **Livrables attendus** : note Word 3-5 pages, rapport 10 pages, ou simple fiche enrichie.

---

## Étape 2 — Fiche de base (skill `vendor-deep-dive`)

Applique le skill en mode complet, tous les champs. Pas d'abrégé.

Points à particulièrement soigner en DD :
- `economie.ca_2024` + évolution sur 3 ans si possible.
- `economie.levees_de_fonds` avec détail investisseurs.
- `economie.actionnariat_connu` avec pourcentages.
- `identite.effectif` avec évolution.

**Budget Firecrawl recommandé** : 3-4 scrapes (site produit + pricing + conformité + "à propos").

---

## Étape 3 — Analyse souveraineté (skill `sovereignty-analyzer`)

Obligatoire dès que l'éditeur traitera des données sensibles pour le client, même hors secteur
régulé. 4 couches complètes.

---

## Étape 4 — Analyse financière approfondie

Au-delà du `vendor-deep-dive` standard :

### 4.1 — Santé financière
- **FR** : Pappers → comptes annuels 3 ans. Observer CA, marge, trésorerie, fonds propres.
- **US/UK** : Crunchbase + presse financière + SEC si coté.
- Signaux faibles : plan social, départ de dirigeants clés, changement d'investisseurs,
  difficulté sur une levée.

### 4.2 — Dépendances et risques
- Dépendance à un client majeur (> 20 % du CA) → risque concentration.
- Dépendance à une technologie tierce critique (ex : revente OpenAI uniquement).
- Litiges publics (CNIL, justice, clients mécontents médiatisés).

### 4.3 — Perspectives
- Roadmap publique.
- Communication investisseurs si coté.
- Positionnement analystes (évolution du classement Gartner / Forrester / G2).

---

## Étape 5 — Analyse juridique légère

Check à la portée d'une recherche web :

- **Procédures en cours** : recherche "<éditeur> vs" ou "<éditeur> assigné" ou "<éditeur>
  lawsuit".
- **Sanctions CNIL** : cnil.fr / search sanctions.
- **Contrat type / CGU** : lecture rapide de la CGU publique — clauses abusives, limitation
  de responsabilité abusive, juridiction compétente non-UE.

Pour une DD approfondie avec enjeu contractuel, recommander un avocat en complément.

---

## Étape 6 — Red teaming (skill `red-teamer` sur 1 éditeur)

Lancé même sur un seul éditeur en DD. Les 3 personas posent leurs questions avec plus de
profondeur qu'en benchmark :

- **Skeptical Practitioner** : va jusqu'à chercher des REX négatifs (forums, G2 critiques,
  reviews Glassdoor pour indice culturel).
- **Adversarial Reviewer** : cherche activement la faille — le mauvais clients, le départ
  de cadres, la dette technique publiée sur GitHub.
- **Implementation Engineer** : scan des issues GitHub de l'éditeur, statuspage, status
  historique.

---

## Étape 7 — Livrable

Une note de due diligence structurée :

1. **Exec summary** — verdict en 5 lignes (GO / GO AVEC RÉSERVES / NO-GO).
2. **Identité et positionnement** — résumé fiche vendor-deep-dive.
3. **Analyse financière** — santé, dépendances, perspectives.
4. **Analyse conformité et souveraineté** — 4 couches + certifications.
5. **Analyse juridique** — litiges, CGU, points d'attention contrat.
6. **Red team** — conclusions des 3 personas.
7. **Risques identifiés** — liste priorisée (bloquants / majeurs / mineurs).
8. **Recommandation** — GO / GO AVEC RÉSERVES / NO-GO + conditions.
9. **Annexes** — toutes les sources avec niveau de fiabilité.

---

## Règles

1. **Profondeur > largeur.** Mieux vaut 2 données vérifiées à 100 % que 10 revendications non
   sourcées.
2. **Signaler les zones aveugles.** Si tu n'as pas pu vérifier un point critique, tu le dis.
3. **Recommandation tranchée.** Pas de "peut-être". GO, GO AVEC RÉSERVES, ou NO-GO.
4. **Ne jamais oublier le contexte client.** Une DD pour signer 50k€ n'est pas la même que
   pour 5M€.

---

## Budget indicatif

| Phase                    | DD surface (15 min) | DD standard (30 min) | DD approfondie (60+ min) |
|--------------------------|---------------------|----------------------|--------------------------|
| Fiche base               | 10 min              | 15 min               | 20 min                   |
| Souveraineté             | skip                | 5 min                | 10 min                   |
| Financier                | 2 min               | 5 min                | 15 min                   |
| Juridique                | skip                | 3 min                | 10 min                   |
| Red teaming              | skip                | 5 min                | 10 min                   |
| Livrable                 | 3 min               | 5 min                | 10 min                   |
