# Prompt — Due diligence sur un seul éditeur

Copie-colle ce prompt pour lancer une DD ciblée sur un éditeur unique.
Déclenche `workflows/vendor-due-diligence.md`.

---

```
Lance une due diligence éditeur selon le workflow vendor-due-diligence.md.

ÉDITEUR CIBLE
Nom : {nom_editeur}
Groupe / produit précis : {si groupe multi-BU, préciser laquelle}
URL officielle : {url}
Secteur d'activité : {description courte}

CONTEXTE DE LA DD
Motif : {pré-contractuel / M&A / audit stratégique / évaluation fournisseur}
Client concerné : {nom_client_Ascend ou "interne"}
Enjeu financier : {fourchette d'engagement envisagé — détermine la profondeur}
Usage client envisagé : {quelles données, quels volumes, quel criticité}

PROFONDEUR
{surface (15 min) / standard (30 min) / approfondie (60+ min)}

PÉRIMÈTRE
- Fiche base (vendor-deep-dive) : OUI (obligatoire)
- Souveraineté 4 couches : {OUI si données sensibles / SKIP sinon}
- Financier approfondi : {OUI si DD M&A / enjeu > 500k€}
- Juridique (litiges, CGU) : {OUI si enjeu contractuel fort}
- Red teaming 3 personas : {OUI si DD pré-contractuelle / SKIP si simple fiche}

LIVRABLE ATTENDU
Note de due diligence structurée :
- Exec summary avec verdict GO / GO AVEC RÉSERVES / NO-GO
- Sections : identité / financier / conformité-souveraineté / juridique / red team
- Risques priorisés
- Recommandation tranchée avec conditions

BUDGET FIRECRAWL
{2 par défaut pour surface, 4 pour standard, 6 pour approfondie}

GO.
```
