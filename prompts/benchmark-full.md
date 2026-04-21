# Prompt — Benchmark complet (bout-en-bout)

Copie-colle ce prompt dans Claude Code après avoir rempli les variables entre `{}`.
Déclenche automatiquement `workflows/market-benchmark.md` avec tous les agents et skills.

---

```
Démarre un benchmark de marché complet selon le workflow market-benchmark.md.

CONTEXTE CLIENT
Client : {nom_client_ou_secteur}
Marché : {description_marche}
Secteur régulé : {oui/non}
Mission : {nature_mission — typiquement "identification et priorisation de solutions IA
pour {cas_usage_global}"}

CAS D'USAGE À BENCHMARKER
{Liste à puces, 1 à 5 cas d'usage précis et non ambigus. Exemple :
- Agent conversationnel 24/7 pour bénéficiaires mutuelle (FAQ remboursement, contrat)
- Assistant IA pour gestionnaires back-office (résumé dossier, aide à la décision)
- RAG interne pour la direction (accès intelligent aux textes réglementaires)
}

GRILLE DE SCORING
Grille : scoring-grids/{nom_grille}.json
Pondérations : {préciser si modifiées par rapport au défaut, sinon "défaut grille"}

PÉRIMÈTRE ET CONTRAINTES
- Nombre de solutions par cas d'usage : {defaut 5-10}
- Périmètre géographique : {France / UE / Monde}
- Exclusions : {liste, ex : "éditeurs < 3 ans d'existence", "solutions sans HDS"}
- Must-have : {liste, ex : "support français", "déploiement on-prem possible"}
- Budget Firecrawl : {nombre de scrapes autorisés, defaut 20-30}
- Timebox total : {defaut 90 min}

LIVRABLES ATTENDUS
- bench.json canonique (source de vérité — voir schemas/bench.schema.json)
- Tableau Excel conforme templates/benchmark-output.xlsx.md
- Note de synthèse Word conforme templates/executive-brief.docx.md
- Rapport de benchmark markdown avec critic + red-teaming intégrés

MÉTHODOLOGIE
- Appliquer la méthodologie triple partage de la valeur Ascend (groupement /
  bénéficiaire / salarié) dans la note de synthèse si secteur mutualiste/santé.
- Souveraineté obligatoire (4 couches) pour chaque solution.
- Checkpoint utilisateur après la phase discovery (avant investigators).
- Rapport de critic obligatoire, items bloquants à traiter avant livraison.
- Red teaming sur top 3 obligatoire.

VALIDATION NIVEAU 4 (OBLIGATOIRE AVANT ENVOI CLIENT)
- Passer la checklist `workflows/pre-delivery-checklist.md` item par item
  (5 blocs : Sources, Fraîcheur, Red-team, Recommandations, Contradictions internes).
- Tout item non coché doit être signalé explicitement en "exception".
- `scripts/validate_bench.py <bench.json>` doit retourner `[ ok ]`.
- Pas de livrable client si un item obligatoire n'est pas coché et non justifié.

GO.
```

---

## Exemple rempli — cas FNMF (historique)

```
Démarre un benchmark de marché complet selon le workflow market-benchmark.md.

CONTEXTE CLIENT
Client : FNMF (Fédération Nationale de la Mutualité Française)
Marché : solutions IA pour l'écosystème mutualiste et santé
Secteur régulé : oui (santé, données de santé, RGPD renforcé)
Mission : identification et priorisation de solutions IA générative (GenAI) pour les
cas d'usage prioritaires du GT2-IA.

CAS D'USAGE À BENCHMARKER
- Agent conversationnel pour bénéficiaires (FAQ remboursement, garanties, contrat)
- Assistant IA gestionnaires back-office (résumé dossier, recherche semantique)
- RAG interne pour la direction (réglementation, études, textes mutualistes)
- Traduction / synthèse documents médicaux
- Détection de fraude / anomalies dans les remboursements

GRILLE DE SCORING
Grille : scoring-grids/health-ai.json
Pondérations : défaut grille (souveraineté 20%, conformité 20%, reste équilibré)

PÉRIMÈTRE ET CONTRAINTES
- Nombre de solutions par cas d'usage : 5-10
- Périmètre géographique : France + UE (leaders mondiaux uniquement à titre comparatif)
- Exclusions : aucune a priori
- Must-have : HDS ou compatible HDS, support français, conformité RGPD documentée
- Budget Firecrawl : 30 scrapes
- Timebox total : 90 min

LIVRABLES ATTENDUS
- Tableau Excel (couleurs FNMF : rouge #FF0000 sur headers)
- Note de synthèse Word 10 pages
- Rapport de benchmark avec méthodologie triple partage (groupement / bénéficiaire / salarié)

GO.
```
