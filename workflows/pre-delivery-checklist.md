# Workflow — Checklist pre-delivery (niveau 4 CLAUDE.md)

**Obligatoire avant tout envoi client en mode Full.** Pas de contournement.

Ce document est la matérialisation concrète du niveau 4 des 4 niveaux de vérification
du `CLAUDE.md` — *"Validation humaine : signalement explicite des points à risque"*. Le
mainthread Claude Code la parcourt item par item à la fin d'un bench Full, coche ou
signale explicitement les exceptions. Le consultant (le consultant) relit la
checklist complétée avant envoi.

**Règle dure** : un item non coché et non signalé comme exception justifiée = pas de
livrable client. Mieux vaut retarder d'une journée que livrer un bench avec une source
unique non retraiangulée sur un chiffre structurant.

---

## Format d'usage

Copier ce fichier dans `examples/<mission>/pre-delivery-checklist.md`, cocher les
cases. Pour chaque item coché, la preuve est dans `bench.json` (cf. `docs/bench-json-
structure.md`). Pour chaque exception, remplir la case "exceptions signalées au
client" avec la justification.

---

## Bloc 1 — Sources

### 1.1 Chiffres-clés sourcés

- [ ] **Chaque `key_figures[].value` structurant** (CA, effectifs, CAPEX, dates de
      lancement, nombre de clients, qualifications) a au moins **1 `source_ids`**
      renseigné.
- [ ] **Chaque chiffre critique** (CAPEX > 50 M€, effectifs > 100 ETP, dates de
      qualification réglementaire, nombre d'utilisateurs) est **triangulé** : 2-3
      sources indépendantes concordantes.
- [ ] **Aucune source unique secondaire** n'est utilisée pour un chiffre qui va en
      slide COMEX **sans** flag "à retriangulér" dans `key_figures[].notes` ou
      `critic.blocking[]`.

### 1.2 Citations dirigeants

- [ ] **Chaque `flagship_quote`** a un `text`, un `author` précis (nom + titre),
      une `date`, et idéalement un `source_id` pointant vers la source primaire.
- [ ] **Aucune citation orpheline** (sans auteur identifié ou sans date) dans les
      fiches acteurs.

### 1.3 Hiérarchie des sources

- [ ] **Chaque source** dans `sources[]` a un `type` (`primary` / `secondary` /
      `specialised` / `regulatory` / `other`) et un `reliability` 1-5 renseigné.
- [ ] **Pour les affirmations de certification** (SecNumCloud, C5, HDS, ISO 27001,
      SOC 2, DORA), la source est soit `primary` soit `regulatory` avec
      `reliability >= 4`. Pas de blog SEO pour certifier une certification.

**Exceptions signalées au client** (bloc 1) :

```
(remplir ici les exceptions — chiffres non triangulés, citations sans date, etc.)
```

---

## Bloc 2 — Fraîcheur

### 2.1 Dates sur tout

- [ ] **Chaque `key_figures[]`** a une `date` renseignée (format YYYY, YYYY-MM ou
      YYYY-MM-DD).
- [ ] **Chaque source** a une `date` de publication.
- [ ] **Chaque fait daté** dans `actors[].context`, `actors[].strategy.*` et
      `transverse.ai_impact` est accompagné de sa date entre parenthèses.

### 2.2 Fenêtre < 24 mois

- [ ] **Toutes les sources** critiques datent de **moins de 24 mois** par rapport à
      la `meta.date` du bench. Les chiffres de marché volatils (pricing, effectifs,
      certifications en cours de renouvellement) datent de **moins de 12 mois**.
- [ ] **Toute source > 18 mois** qui reste dans le bench est **explicitement
      justifiée** dans `critic.warnings[]` (ex : "LEAP 10 M heures de vol, chiffre
      2021 structurant pour l'historique prédictif, à rafraîchir avant COMEX si
      possible").

### 2.3 Roadmap vs déployé

- [ ] **Pour chaque acteur**, la distinction `maturity_and_approach` entre *déployé
      production*, *commercialisé*, *pilote*, *roadmap* est explicite. Aucun
      "lancement" flou qui laisse croire que c'est déjà en prod alors que ça ne
      l'est pas.

**Exceptions signalées au client** (bloc 2) :

```
(ex : "LEAP 2021 repris car pas de renouvellement public — à rafraîchir")
```

---

## Bloc 3 — Red-team (mode Full)

### 3.1 Périmètre red-team

- [ ] **Les top 3 du classement** (`exec_summary.ranking[0..2]`) sont chacun passés
      au red-teamer. Preuve : `red_team.details_per_actor` contient une entrée pour
      chacun.
- [ ] **Chaque entrée red-team** a 3 personas × minimum 3 arguments contre chacun
      (= 9 arguments minimum par acteur red-teamé).
- [ ] **Chaque entrée red-team** a un `verdict` tranché (`TIENT LA ROUTE` / `À
      NUANCER` / `REFAIRE`) — pas de "peut-être".

### 3.2 Verdicts cohérents

- [ ] **`red_team.verdicts`** couvre au moins le top 3.
- [ ] **Chaque verdict `À NUANCER` ou `REFAIRE`** a une `alternative` proposée dans
      `red_team.details_per_actor`.

### 3.3 Propagation au livrable

- [ ] **Si un verdict est `REFAIRE`**, le top 3 a été recomposé (le #4 remonte), et
      le red-teamer a repassé sur le nouveau top 3.
- [ ] **Les `messages_to_comex`** de `red_team` sont repris explicitement dans la
      synthèse exécutive du livrable Word.

### 3.4 Angles morts des fiches

- [ ] **Chaque `actors[].blind_spots`** a au moins 3 items numérotés, avec
      `severity` renseignée.
- [ ] **Aucun blind_spot de severity `critical`** n'est laissé sans mention
      explicite dans le livrable client.

**Exceptions signalées au client** (bloc 3) :

```
(rare — le red-team est obligatoire en mode Full)
```

---

## Bloc 4 — Recommandations

### 4.1 Chiffrage honnête

- [ ] **Toute recommandation chiffrée** (€, ETP, mois, %, ratio) a soit un
      `source_ids` pointant vers une source réelle, soit un champ `caveats` qui dit
      explicitement **"hypothèse Ascend à cadrer lors d'une phase d'étude dédiée"**.
- [ ] **Aucun chiffre Ascend non étayé** ne figure dans le corps d'une
      recommandation (corps = ce qui entre en slide). Les fourchettes libres
      ("30-50 M€", "15-25 ETP") **doivent** être dans `caveats` avec qualification.

  > Règle héritée du run LISI v2 : R3 mentionnait "15-25 ETP sur 3 ans, 30-50 M€"
  > sans source. Le patch v2 a déplacé ces chiffres en caveats avec la formule
  > standard. Cette règle est désormais dure.

### 4.2 Traçabilité des reco

- [ ] **Chaque `recommendation.id`** est unique (`R1`, `R2`, …).
- [ ] **Chaque recommandation** a un `title` court et un `body` qui explique
      **pourquoi** (pas juste le **quoi**).

### 4.3 Caveat explicites

- [ ] **Chaque hypothèse non vérifiée** est entre parenthèses avec "*hypothèse*" ou
      "*à cadrer*". Pas d'affirmations au présent qui masquent une incertitude.

**Exceptions signalées au client** (bloc 4) :

```
(lister les recos qui restent chiffrées faute d'alternative, avec raison)
```

---

## Bloc 5 — Contradictions internes

### 5.1 Cohérence fiches / synthèse

- [ ] **Les 3 takeaways** de `exec_summary.three_takeaways` sont effectivement
      étayés par au moins 2 fiches acteurs.
- [ ] **Le `transverse.ai_impact`** est cohérent avec les `blind_spots` des fiches
      (pas de message "l'IA est une solution simple" dans le transverse si les
      fiches listent 8 angles morts critiques par acteur).

### 5.2 Cohérence scoring / verdicts

- [ ] **Chaque acteur du top 3** avec un `red_team_verdict = "REFAIRE"** a été
      sorti du top 3, ou son maintien est explicitement justifié dans `critic.
      warnings[]`.
- [ ] **Aucune incohérence poids** : `sum(actors[*].scoring[*].weight)` ≈ 1.0 ±
      0.01 pour chaque acteur (vérifié par `scripts/validate_bench.py`).
- [ ] **Les `weighted_score`** calculés à partir des `scoring[]` matchent ceux
      affichés dans `exec_summary.ranking` (±0.01).

### 5.3 Cohérence méthodo

- [ ] **La `grid_ref`** correspond au secteur traité (pas de `enterprise-saas.json`
      sur un bench santé, ni inversement sauf justification explicite).
- [ ] **Le `mode = "full"`** est bien renseigné dans `meta` — pas de livrable
      client envoyé à partir d'un bench.json en mode `quick` ou `standard`.

### 5.4 Cohérence synthèse vs fiches détaillées

Pour chaque acteur cité dans les enseignements structurants de la synthèse
exécutive, vérifier que la catégorisation utilisée (« by design »,
« remédiation », « hybride », etc.) est **cohérente avec le verdict red-team
et le scoring détaillé** de la fiche correspondante.

- [ ] **Un acteur « À NUANCER » au red-team** ne peut pas être cité en
      exemple pur dans une liste de synthèse (« by design (X, Y, Z) »)
      sans que la même phrase contienne un qualifier spécifique
      (« voie intermédiaire », « hybride », « souveraineté technologique
      incomplète »…).
- [ ] **Un acteur avec score < 4 sur indépendance_stack** ne peut pas être
      classé « by design pur » sans asterisk ni qualification.
- [ ] **Un verdict `REFAIRE`** doit être soit absent des exemples positifs de
      la synthèse, soit accompagné d'une mention explicite du verdict.

> Le test `tests/test_exec_summary_consistency.py` automatise cette règle
> (parse les takeaways, croise avec `actors[].red_team_verdict` et
> `scoring[]`). Il doit passer avant envoi client.

### 5.5 Cohérence des chiffres-clés intra-fiche

Pour chaque acteur, les chiffres mentionnés dans le contexte, les
`key_figures[]`, les justifications de scoring, les angles morts et la
flagship quote doivent être **cohérents**.

- [ ] Aucune paire "nombre similaire mais différent" avec la même unité
      dans le même acteur (ex. « 350 000 clients » dans le contexte vs
      « 350k clients » dans une justification = 350 000 et 370 000 donnent
      un écart de 5,7 %, à unifier).
- [ ] Toute fourchette (« 350 000-370 000 ») doit apparaître comme fourchette
      **partout** ou être résolue en valeur unique sourcée partout.
- [ ] Si deux chiffres divergent parce qu'ils sourcent des périmètres
      différents (ex. CA groupe vs CA filiale), le contexte doit le rendre
      explicite.

> Le test `tests/test_number_consistency.py` automatise cette règle. Il
> parcourt tous les champs textuels de chaque acteur, extrait les nombres
> suivis d'un mot-clé d'unité (clients, ETP, salariés, serveurs, …) et
> flag les paires avec écart relatif 3-20 %. Il doit passer avant envoi
> client.

**Exceptions signalées au client** (bloc 5) :

```
(ex : "la recommandation #2 dépend de la réponse donneur d'ordre sur ITAR — à
        valider en réunion miroir")
```

---

## Synthèse finale

Avant envoi :

- [ ] `scripts/validate_bench.py` retourne `[ ok ]` sur le `bench.json` final.
- [ ] Tous les items ci-dessus sont cochés **ou** explicitement dans "exceptions".
- [ ] Le consultant (le consultant) a relu la checklist complétée.
- [ ] Le partner (si pair review disponible — cf. Sprint 3 "Peer review workflow")
      a relu au minimum la synthèse exécutive et les recommandations.

**Date de validation niveau 4** : `YYYY-MM-DD`
**Consultant responsable** : `le consultant`
**Pair review (si applicable)** : `<nom>`
