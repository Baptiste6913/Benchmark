# Spec — Livrable Excel de benchmark

Ce document décrit la structure du fichier Excel de sortie standard d'un benchmark de marché
produit par le stack Ascend. À utiliser par l'agent benchmark-lead à la phase 7.1.

Le fichier est généré via la librairie `openpyxl` (ou équivalent). Nom de fichier suggéré :
`benchmark_{client}_{YYYY-MM-DD}.xlsx`.

---

## Structure — 5 onglets

### Onglet 1 — Synthèse

Tableau récapitulatif 1 page, prêt à présenter en COPIL.

Colonnes :
- Rang (1, 2, 3, ...)
- Solution
- Éditeur
- Région siège
- Score pondéré (2 décimales)
- Souveraineté (verdict : SOUVERAIN / MIXTE / NON-SOUVERAIN)
- Verdict red team (TIENT / À NUANCER / REFAIRE / N/A)
- Commentaire général (1 ligne)

Mise en forme :
- Headers : bold, fond coloré (rouge `#FF0000` pour FNMF, sinon couleur client ou bleu Ascend),
  police blanche.
- Conditional formatting sur `Score pondéré` : dégradé vert (4-5) / jaune (3-4) / rouge (<3).
- Freeze pane row 2.
- Filtres auto activés.

### Onglet 2 — Scoring détaillé

Matrice croisée solutions × critères.

Colonnes :
- Solution (A)
- Colonnes B à G : un critère par colonne (Maturité, Références, Conformité, Interop,
  Économie, Souveraineté) — ajuster selon grille utilisée.
- Colonne H : Pondération (affichée pour info)
- Colonne I : Score pondéré (formule Excel `=SUMPRODUCT(B2:G2,$B$1:$G$1)` adaptée)

Mise en forme :
- Row 1 : poids de chaque critère (pour que le client puisse ajuster).
- Conditional formatting sur chaque cellule de note (1-5) : dégradé couleur.
- N/D en cellule grise.
- Freeze pane colonne A + row 2.

### Onglet 3 — Fiches éditeurs

Une section par éditeur (10-20 éditeurs × ~30 lignes chacun). Format vertical (1 éditeur =
1 bloc).

Champs par éditeur (issus de `vendor-deep-dive`) :
- Identité (nom, siège, année, effectif)
- Produit (description, cas d'usage, architecture)
- Clients (nombre, références, secteurs)
- Certifications (tableau détaillé : nom, statut, date, source)
- Tech (stack, cloud, modèles, API, SSO)
- Économie (modèle, fourchette, CA, levées, actionnariat)
- Souveraineté (4 couches + verdict global)
- Points forts / faibles / trous info

Mise en forme :
- Séparateur visuel entre éditeurs (bordure épaisse).
- Liens hypertextes actifs vers les sources.

### Onglet 4 — Sources

Toutes les sources utilisées, taguées par `source-credibility`.

Colonnes :
- URL
- Titre / description
- Date publication
- Niveau fiabilité (1-5)
- Solution(s) concernée(s)
- Champ(s) sourcé(s)

Mise en forme :
- Conditional formatting sur `Niveau` : vert (5) à rouge (1).
- Filtres auto.
- Tri par défaut : niveau décroissant.

### Onglet 5 — Méthodologie

Texte long, explique la démarche pour que le client comprenne :
- Méthodologie de discovery (nombre de requêtes, angles).
- Méthodologie d'investigation (cross-check systematic, sources primaires).
- Grille de scoring utilisée + pondérations + explication de chaque niveau.
- Processus de critic et red-teaming.
- Dates : début / fin benchmark, date de vérification des certifications.
- Limitations et zones aveugles assumées.

Mise en forme :
- Texte justifié, police 11pt.
- Titres en gras, bleu.

---

## Règles transverses

1. **Police par défaut** : Calibri 11pt (ou charte client si fournie).
2. **Noms d'onglets** en français, courts : `Synthèse`, `Scoring`, `Fiches`, `Sources`,
   `Méthodologie`.
3. **Pas d'images** (ralentit l'Excel, risque de compatibilité).
4. **Formules Excel natives** uniquement (pas de macros VBA).
5. **Les cellules N/D sont colorées** (gris clair) et avec texte italique explicite.
6. **Les sources sont des hyperliens cliquables** dans tout le fichier.
7. **Ligne de pied de page** sur chaque onglet : "Benchmark produit par Ascend Partners —
   Ascend Research Stack v1.0 — {date}".

---

## Génération programmatique

L'agent benchmark-lead lance un script Python avec `openpyxl` qui consomme le JSON de sortie
du `weighted-scorer` + les fiches `vendor-deep-dive` + le rapport critic et produit le
fichier. Le script n'est pas inclus dans ce repo — à implémenter lors du premier benchmark
réel (génération ad hoc, puis factorisation).

Pour la v1 du stack, l'agent peut produire directement un XLSX via Python inline dans un bloc
de code Bash, tant que la structure respecte cette spec.
