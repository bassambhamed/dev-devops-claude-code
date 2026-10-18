---
name: postmortem
description: Rédige un post-mortem blameless après un incident sur l'ecommerce-app, à partir de la timeline, des preuves (logs, traces, métriques, commits) et des actions menées. À utiliser après le rétablissement du service, quand on demande un post-mortem, un retour d'expérience ou un compte rendu d'incident.
---

# Skill : postmortem

Objectif : transformer un incident en **apprentissage exploitable**, pas en document archivé.

## Structure imposée

Partir du [modèle](TEMPLATE.md) et le remplir dans `docs/postmortems/AAAA-MM-JJ-<titre-court>.md` :

1. **Résumé** — trois lignes : impact utilisateur, durée, cause en une phrase.
2. **Chronologie** — horodatée, avec la **source** de chaque horodatage (alerte, log, trace, commit).
3. **Impact quantifié** — durée, requêtes ou commandes affectées, montant concerné. Des chiffres.
4. **Cause racine** — distinguée des **facteurs aggravants** et des **facteurs de détection**
   (pourquoi a-t-on mis X minutes à voir le problème ?).
5. **Ce qui a fonctionné / ce qui a manqué** — détection, tests, revue, outillage, runbook.
6. **Actions** — tableau action | type (immédiate / de fond) | propriétaire (rôle) | échéance |
   critère de clôture. Au moins une action qui empêche la **récurrence** (test, contrôle, hook).
7. **Indicateurs** — MTTD et MTTR, avec la méthode de calcul.

## Garde-fous

- **Blameless** : aucun nom de personne ; un processus qui permet l'erreur est la cause.
- Aucune donnée client, aucun secret, aucune adresse interne.
- Aucune action sans propriétaire **et** échéance : sinon c'est une intention, pas une action.
- Aucune cause racine sans preuve citée : « indéterminée, investigation en cours » est acceptable.
