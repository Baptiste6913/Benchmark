# Workflow — Rescore après changement

> Introduit en v1.2.0. Prérequis : `bench.json` canonique (v1.1.0, S1.6),
> `lib/render.py` (S2.1-S2.3), `scripts/rescore.py` (S2.5).

Ce workflow adresse **trois cas concrets** observés en production :

1. **Changement de grille** — le client ajuste les pondérations (ex : "mettez 30%
   sur la souveraineté au lieu de 25%"). Sans outillage, il fallait relancer tout
   le bench à la main.
2. **Révision d'un score** — le red-team fait tomber un 5/5 à 4/5 (cas réel LISI v2
   sur OVHcloud `indépendance_stack`). Sans outillage, il fallait reclasser à la
   main et regénérer xlsx + docx à la main.
3. **Ajout ou retrait d'un acteur** — un acteur manquant est remonté en v2 (cas
   réel LISI v2 avec OVHcloud). Sans outillage, chaque artefact était modifié à la
   main.

Avec `rescore.py`, chaque cas se fait en **une commande**.

---

## Cas 1 — Changement de grille (poids)

**Contexte** : le client remonte que le critère `traction_resultats` doit peser
20% au lieu de 15%, en rééquilibrant sur `ampleur_investissement` qui passe de
15% à 10%.

**Étapes** :

1. Créer la nouvelle grille. Copier l'existante sous un nouveau nom :

   ```bash
   cp scoring-grids/lisi-souverainete.json scoring-grids/lisi-souverainete-v2.json
   # Ouvrir et ajuster les weights. Doit toujours sommer à 1.0.
   ```

2. Valider la nouvelle grille :

   ```bash
   python scripts/validate_grid.py scoring-grids/lisi-souverainete-v2.json
   ```

3. Rescore le bench avec la nouvelle grille + génération DIFF + rendu complet :

   ```bash
   python scripts/rescore.py examples/generic-demo/bench.json \
       --new-grid scoring-grids/lisi-souverainete-v2.json \
       --output examples/generic-demo/bench-v3.json \
       --diff-against examples/generic-demo/bench.json \
       --render
   ```

4. Le script produit :
   - `bench-v3.json` avec weighted_score recalculés + classement mis à jour
   - `DIFF.md` qui liste tout ce qui a changé (classement, scores, poids par
     critère)
   - `bench-v3.xlsx` et `bench-v3.docx` générés depuis le nouveau JSON

5. Valider le nouveau bench :

   ```bash
   python scripts/validate_bench.py examples/generic-demo/bench-v3.json
   ```

**Temps typique** : 2-5 minutes, vs 1-2 heures à la main.

---

## Cas 2 — Révision manuelle d'un ou plusieurs scores

**Contexte** : le red-team impose "le 5/5 sur OVHcloud `indépendance_stack` est
inflationniste → 4/5". Le scoring change, donc le `weighted_score` doit être
recalculé, le classement aussi (OVH peut descendre d'un cran).

**Étapes** :

1. Éditer `bench.json` à la main pour changer le ou les scores. Exemple :

   ```jsonc
   // dans actors[] → id: "ovhcloud" → scoring[]
   {
     "criterion_id": "independance_stack",
     "score": 4,                     // était 5
     "weight": 0.25,
     "justification": "...",
     "revision_note": "5 initial révisé à 4 après red-team v2 — dépendances VMware/NVIDIA/SambaNova."
   }
   ```

2. Rescore (sans `--new-grid` : on garde la grille existante, on recalcule juste
   les weighted_score) :

   ```bash
   python scripts/rescore.py examples/generic-demo/bench.json \
       --output examples/generic-demo/bench-v3.json \
       --diff-against examples/generic-demo/bench.json \
       --render
   ```

3. Même livrables : bench-v3.json + DIFF.md + xlsx + docx.

**Note** : si tu modifies en place (pas de `--output`), le bench.json d'origine
est overwrite. Ajoute `--diff-against bench-v1.json` AVANT d'écraser pour garder
trace.

---

## Cas 3 — Ajout ou retrait d'un acteur

**Contexte** : LISI v2 a demandé d'ajouter OVHcloud au panel après red-team v1.

**Étapes** :

1. Éditer manuellement `bench.json` pour ajouter (ou retirer) un acteur dans
   `actors[]`. Respecter la structure canonique — voir
   `docs/bench-json-structure.md`. Inclure tous les champs obligatoires :
   - `id`, `name`, `scoring[]` complet (un score par critère de la grille),
     `weighted_score` (sera recalculé), `rank` (sera recalculé)
   - Pour marquer un ajout tardif : `added_in_version: "v2"` et
     `notes: "Ajouté en v2 après recommandation red-team v1."`

2. Ajouter aussi les nouvelles sources dans `sources[]` avec des IDs propres
   (kebab-case, préfixe par l'acteur).

3. Rescore pour recalculer classement et livrables :

   ```bash
   python scripts/rescore.py examples/generic-demo/bench.json \
       --diff-against examples/generic-demo/bench-v1-snapshot.json \
       --render
   ```

4. Valider :

   ```bash
   python scripts/validate_bench.py examples/generic-demo/bench.json
   ```

**Temps typique** : ~30 minutes de rédaction pour la nouvelle fiche acteur +
2 minutes de script, vs plusieurs heures à la main pour propager les
changements dans MD + XLSX.

---

## Reproduction exacte du run LISI v2

Le run LISI v2 est reproductible aujourd'hui en une commande, à condition
d'avoir :

- Le bench v1 snapshot (avant ajout OVH + révision score) : conservé dans
  `examples/generic-demo/bench-v1-snapshot.json` (à créer au moment
  d'une révision future).
- Le bench v2 final : `examples/generic-demo/bench.json`.

```bash
# Simuler la révision v2 à partir du snapshot v1
python scripts/rescore.py examples/generic-demo/bench.json \
    --diff-against examples/generic-demo/bench-v1-snapshot.json \
    --render
```

---

## Règles et garde-fous

1. **Toujours valider avant de render** : le validator `validate_bench.py`
   attrape une incohérence de somme de poids, un source_id orphelin, etc.
   `rescore.py` recalcule ; il ne valide pas.
2. **Always use `--diff-against`** quand tu écrases un bench existant — c'est
   ta trace d'audit pour le COMEX.
3. **Bump de version automatique** : `rescore.py` incrémente `meta.version`
   (ex : `2.0 → 2.1`). Pour garder l'ancienne version, passe `--no-bump-version`.
4. **N'ajoute pas d'acteur via rescore.py** — le script recalcule et reclasse,
   il ne construit pas de fiche. L'ajout doit passer par l'éditeur humain sur
   le JSON (avec investigator sub-agent si besoin pour produire la fiche).
5. **Mode Full obligatoire pour les livrables client** : après un rescore, si
   c'est pour le client, repasser la checklist `pre-delivery-checklist.md`.
