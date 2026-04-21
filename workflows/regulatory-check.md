# Workflow — Check réglementaire (HDS / RGPD / AI Act / sectoriel)

Ce workflow répond à une question précise : **"Est-ce que la solution X est conforme à Y ?"**
Court (15-30 min), focus sur `sovereignty-analyzer` + `fact-checker`.

## Pré-requis

- Nom de la solution et éditeur.
- Cadre réglementaire visé (HDS, RGPD, AI Act, DORA, NIS2, CE MDR, PCI DSS, ...).
- Périmètre d'usage client (quelles données traitées, où, par qui).

---

## Étape 1 — Cadrage de la question

Questions à clarifier avant de chercher :

1. **Quel cadre précis ?** Pas juste "conforme RGPD" mais "conforme RGPD pour traitement
   données de santé côté groupement mutualiste dans le cadre du Règlement Santé FR".
2. **Quel périmètre produit ?** La solution entière ou un module précis ? Certains modules
   peuvent être certifiés et d'autres non.
3. **Quel usage client envisagé ?** Le client va-t-il utiliser la fonctionnalité concernée par
   la certif ?
4. **Quel niveau d'exigence ?** Présomption de conformité (déclaration) vs certification
   tierce vs audit externe.

---

## Étape 2 — Identification du référentiel

Pour chaque cadre, le référentiel faisant foi :

| Cadre          | Référentiel / Registre faisant foi                         | Niveau source |
|----------------|------------------------------------------------------------|---------------|
| HDS            | esante.gouv.fr → liste des hébergeurs certifiés HDS        | 5             |
| RGPD           | CNIL (texte + sanctions) + documentation DPO éditeur       | 5             |
| AI Act (UE)    | Commission UE + autorité nationale (CNIL pour la France)   | 5             |
| DORA           | EBA / AMF / ACPR                                           | 5             |
| NIS2           | ANSSI + ministère concerné par secteur                     | 5             |
| CE MDR         | Base Eudamed                                               | 5             |
| ISO 27001      | Site certifiant (BSI, AFNOR Cert, LNE, Bureau Veritas, ...)| 5             |
| SOC 2          | Rapport attestable auditeur                                | 5             |
| PCI DSS        | Liste PCI Security Standards Council                       | 5             |
| SecNumCloud    | ANSSI — liste des offres qualifiées                        | 5             |

---

## Étape 3 — Fact check sur la revendication éditeur

Applique `fact-checker` sur chaque revendication :

1. L'éditeur revendique-t-il explicitement la conformité ?
2. Si oui, quelle preuve cite-t-il ? (attestation, numéro de certif, organisme)
3. Cette preuve est-elle vérifiable sur le référentiel officiel ?

Trois scénarios :

| Scenario                                            | Verdict                                    |
|-----------------------------------------------------|--------------------------------------------|
| Éditeur revendique + preuve au référentiel officiel | **CONFIRMED**                              |
| Éditeur revendique + pas de preuve au référentiel   | **REFUTED** ou **UNVERIFIABLE** selon cas |
| Éditeur ne revendique pas                           | **REFUTED** (absence = non conforme)       |

**Attention à la nuance `revendiqué` vs `certifié`** : un éditeur peut écrire "compatible HDS"
sans être lui-même certifié (s'il passe par un hébergeur tiers certifié). Cette architecture
est légitime mais à expliciter : "HDS via hébergeur OVH HDS" n'est pas "HDS directement".

---

## Étape 4 — Analyse souveraineté (si applicable)

Certaines réglementations imposent implicitement des exigences de souveraineté :

- **HDS** : donnée de santé française, hébergement France ou UE exigé, éviter Cloud Act.
- **DORA** : finance, exigences de résilience et de souveraineté des dépendances critiques.
- **NIS2** : secteurs essentiels, exigences de maîtrise de la chaîne d'approvisionnement.
- **Directive ministres français "Cloud au centre"** : cloud souverain pour États / OIV.

Lance `sovereignty-analyzer` sur les 4 couches si le cadre impose ou suggère cette analyse.

---

## Étape 5 — Périmètre et limites

Distinguer clairement :

- **Certifications directes** (l'éditeur lui-même est certifié).
- **Certifications indirectes** (l'éditeur s'appuie sur un tiers certifié — OVH HDS, AWS
  PCI DSS, etc.).
- **Présomption de conformité** (l'éditeur déclare, personne ne certifie).
- **Conformité contractuelle** (contrat client prévoit des clauses, rien de plus).

Ces 4 niveaux donnent des garanties très différentes. Le client doit le savoir.

---

## Étape 6 — Livrable

Note courte (1-2 pages) :

```markdown
# Check réglementaire — <solution> vs <cadre>
Date : 2026-04-16
Analyste : <Claude via Ascend Research Stack>

## Question
<Question précise posée par le client>

## Verdict
**CONFIRMED | REFUTED | NUANCED | UNVERIFIABLE**

<Justification en 3-5 lignes>

## Preuves
- [Source officielle 1] — <URL + date>
- [Source officielle 2] — <URL + date>
- [Source éditeur] — <URL + date>

## Périmètre et limites
- La certification couvre : <périmètre>
- Elle ne couvre pas : <zones exclues>
- Validité : <dates>
- Via tiers ou directe : <préciser>

## Points d'attention pour le client
1. <...>
2. <...>
3. <...>

## Recommandation
<Conditions d'usage recommandées + risques résiduels>
```

---

## Règles

1. **Source officielle obligatoire.** Jamais valider une conformité sans consulter le
   référentiel faisant foi.
2. **Date de vérification systématique.** Les certifications expirent.
3. **Distinguer direct / indirect.** Hébergeur HDS ≠ solution HDS.
4. **Signaler les hors-périmètre.** Si la certif couvre le module A mais pas B, le dire.
5. **Pas de "globalement conforme".** Verdict tranché par cadre.

## Common Mistakes

- **Confondre "conformité" et "certification".** RGPD = conformité (pas de certification
  universelle). HDS = certification (registre tenu par l'ANS).
- **Prendre la liste clients d'un éditeur comme preuve.** Le fait qu'une mutuelle utilise
  l'éditeur ne prouve pas que le produit est HDS — elle peut avoir fait un contrat dérogatoire.
- **Oublier la date d'expiration.** Les certifications HDS, ISO, SOC 2 ont une durée de
  validité. Check la date.
