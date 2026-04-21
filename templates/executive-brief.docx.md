# Spec — Note de synthèse exécutive (Word)

Ce document décrit la structure du Word de synthèse exécutive produit par le stack à la
phase 7.2 du workflow `market-benchmark.md`. Destinataire : comité de direction client,
COPIL, décideurs qui n'iront pas lire le tableau Excel.

Contrainte majeure : **10 pages maximum**. Tout ce qui dépasse va en annexe ou disparaît.

---

## Structure

### 1. Couverture (1 page)

- Titre : `Benchmark {nom_marché} — Synthèse exécutive`
- Sous-titre : `{nom_client} — {YYYY-MM-DD}`
- Logo Ascend Partners (placeholder si non fourni)
- Logo client (si autorisé)
- Ligne : `Document confidentiel — usage interne {client}`

### 2. Exec Summary (1 page)

Tout ce qui compte, en 1 page, pour un lecteur qui ne lira rien d'autre.

Structure :
- **Contexte en 3 lignes** : pourquoi ce benchmark, pour qui, dans quel calendrier.
- **Périmètre en 3 lignes** : cas d'usage, grille de scoring, nombre de solutions évaluées.
- **Top 3 recommandations** (tableau 3 lignes × 3 colonnes : solution / score / verdict red team).
- **Risques majeurs identifiés** (3-5 bullets).
- **Actions recommandées** (3-5 bullets court terme / moyen terme).

Pas de jargon technique. Lecteur cible : DG, DRH, direction stratégie.

### 3. Méthodologie (1 page)

Explication accessible :
- Comment les solutions ont été identifiées (discovery large).
- Comment elles ont été investiguées (multi-sources, cross-check).
- Comment elles ont été scorées (grille pondérée).
- Comment les recommandations ont été challengées (critic + red team).

Insister sur : **chaque donnée a été sourcée**, **les sources ont été classées par fiabilité**,
**les top 3 ont été remises en cause par un red teaming indépendant**.

Mention si applicable : **application de la méthodologie triple partage de la valeur Ascend**
(groupement / bénéficiaire / salarié).

### 4. Cartographie du marché (1 page)

Vue d'ensemble du marché évalué :
- Taille de marché et croissance (si connue).
- Géographie (FR / UE / US / autre) — diagramme ou tableau.
- Typologie des acteurs (pure players IA, éditeurs historiques, open source).
- Niveau de maturité du marché (émergent / en croissance / mature).

### 5. Top 5 recommandations détaillées (3-4 pages)

Une page par recommandation, format uniforme :

```
## #1 — {Nom solution}
Score pondéré : 4.3/5
Verdict red team : TIENT LA ROUTE

Pitch en 3 lignes
<phrase 1 — ce que c'est>
<phrase 2 — pour qui, pour quoi>
<phrase 3 — ce qui la différencie>

Points forts (3-4 bullets)
- ...

Points de vigilance (2-3 bullets issus du red team)
- ...

Pour aller plus loin
- Fiche détaillée : onglet 3 du tableau Excel.
- Sources principales : {3 URLs clés}.
```

### 6. Matrice comparative (1 page)

Visualisation des top 5-10 sur 2 axes :
- Axe X : `Maturité + Références` (moyenne)
- Axe Y : `Souveraineté + Conformité` (moyenne)
- Taille bulle : `Score pondéré global`
- Couleur : verdict red team (vert TIENT / orange NUANCER / rouge REFAIRE)

À défaut de génération auto, fournir un tableau à 2 dimensions que le consultant pourra
convertir en graphique PowerPoint.

### 7. Recommandations opérationnelles (1 page)

Plan d'action en 3 horizons :
- **Court terme (0-3 mois)** : pilotes à lancer, validation techniques, contacts à prendre.
- **Moyen terme (3-12 mois)** : déploiement cible, intégration SI, onboarding équipes.
- **Long terme (12+ mois)** : évolutions possibles, anticipations réglementaires (AI Act,
  etc.).

### 8. Annexes (1 page)

- Liste des solutions évaluées mais non retenues dans le top 5 (+ raison brève).
- Références méthodologiques.
- Glossaire (HDS, SecNumCloud, Cloud Act, FHIR, etc.).
- Contact référent Ascend.

---

## Règles de forme

1. **Police** : Calibri ou charte client (Arial, Times). 11pt corps, 14pt titres niveau 2,
   18pt titres niveau 1.
2. **Couleurs** : charte client si fournie ; sinon bleu Ascend + rouge pour alertes.
3. **Pas de tableau complexe** — la complexité va dans l'Excel.
4. **Visuels** : matrice en 6.1 doit être générée, même en fallback tableau.
5. **Page numérotée** en bas à droite.
6. **Header** : `Benchmark {marché} — {client} — Confidentiel`
7. **Footer** : `Ascend Partners — {date}`
8. **Export PDF** prévu — tester la pagination.

---

## Génération

Comme pour l'Excel, le Word est généré par l'agent benchmark-lead via un script Python
(`python-docx`) ou fallback manuel via copier-coller du markdown dans Word. En v1 du stack, la
version markdown suffit — le consultant importe dans Word pour la charte finale.

---

## Check final avant envoi

- [ ] Exec summary tient en 1 page.
- [ ] Les 3 top recommandations sont identifiées dès la page 2.
- [ ] Chaque recommandation a un pitch en 3 lignes compréhensible par un non-technicien.
- [ ] Les points de vigilance du red team sont intégrés dans chaque reco.
- [ ] Le plan d'action en 3 horizons est réaliste.
- [ ] Le français est irréprochable (accents, pluriels, formulations).
- [ ] Aucune donnée confidentielle client n'a été copiée par erreur d'un autre projet.
