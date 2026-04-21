# Exemple — generic-demo (synthétique public)

Ce dossier contient un **bench entièrement synthétique** qui sert d'exemple de rendu pour le stack Ascend-Bench.

## Contenu

- `bench.json` — bench canonique, 4 éditeurs fictifs (Acme Cloud, Nova Industries, Demo Hybrid Systems, Sample Legacy Corp) avec scoring sur la grille `lisi-souverainete.json`.
- `bench.xlsx` — rendu Excel 3 onglets (Matrice, Détails, Sources) — généré par `python -m lib.render`.
- `bench.docx` — rendu Word avec charte graphique Ascend — généré par `python -m lib.render`.

## Usage

Ce bench est référencé par les tests pytest du repo pour :

- Valider le schéma `bench.schema.json` via `scripts/validate_bench.py`.
- Tester les fonctions de render dans `lib/_xlsx.py` et `lib/_docx.py`.
- Servir de fixture pour les tests de non-régression (`test_render_docx_no_blank_pages.py`, `test_label_fr_in_outputs.py`, etc.).

## ⚠️ Avertissement

**Tous les éléments sont fictifs** :

- Noms d'éditeurs (Acme Cloud, Nova Industries, Demo Hybrid Systems, Sample Legacy Corp) — inventés.
- Chiffres (CA, effectifs, CAPEX, nombre de clients) — inventés.
- Citations attribuées à des dirigeants — fictives.
- URLs sources (`example.com/...`) — placeholders.

Ne PAS utiliser ce bench comme référence méthodologique pour une mission réelle. Il sert uniquement à démontrer la structure du livrable produit par le stack.

## Régénérer les livrables

Après édition du `bench.json` :

```bash
python -m lib.render examples/generic-demo/bench.json
```

Deux fichiers sont (re)générés dans ce dossier : `bench.xlsx` + `bench.docx`.
