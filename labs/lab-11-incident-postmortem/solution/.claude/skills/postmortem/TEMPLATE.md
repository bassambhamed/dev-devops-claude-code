# Post-mortem — <titre court et factuel>

| | |
|---|---|
| **Date de l'incident** | AAAA-MM-JJ |
| **Durée** | HHhMM |
| **Sévérité** | S1 / S2 / S3 |
| **Services affectés** | |
| **Auteur du document** | (rôle, pas de nom) |
| **Statut** | Brouillon / En revue / Clôturé |

## 1. Résumé

<Trois lignes : quel a été l'impact pour l'utilisateur, combien de temps, et quelle en a
été la cause.>

## 2. Chronologie

| Heure (UTC) | Événement | Source |
|---|---|---|
| 00:00 | Déploiement de la version X | commit / pipeline |
| 00:00 | Premier symptôme technique | alerte / métrique |
| 00:00 | Premier impact utilisateur | ticket / log |
| 00:00 | Détection | alerte / signalement |
| 00:00 | Diagnostic établi | investigation |
| 00:00 | Action de rétablissement | commande |
| 00:00 | Service rétabli | métrique |

## 3. Impact

- **Durée d'indisponibilité :**
- **Requêtes en échec :**
- **Services affectés :**
- **Périmètre utilisateur :**

## 4. Cause racine

<La cause, étayée par une preuve citée.>

**Facteurs aggravants** (à ne pas confondre avec la cause) :
-

## 5. Ce qui a fonctionné / ce qui a manqué

| | Constat |
|---|---|
| ✅ A fonctionné | |
| ❌ A manqué | |

## 6. Actions correctives

| # | Action | Type | Propriétaire | Échéance | Critère de clôture |
|:---:|---|---|---|---|---|
| 1 | | Immédiate | | | |
| 2 | | De fond | | | |

## 7. Indicateurs

| Indicateur | Valeur | Méthode de calcul |
|---|---|---|
| MTTD (détection) | | premier symptôme → détection |
| MTTR (rétablissement) | | détection → service rétabli |

---

> Document **blameless** : aucune personne n'y est nommée. Les causes sont systémiques.
