# Lab 11 — Incident & post-mortem (scénario Dev et scénario DevOps)

> **Durée :** 45 à 60 min · **Modules requis :** [07](../../modules/07-sous-agents/), [08](../../modules/08-mcp/)
> · **Outils :** `git`, `dotnet` ; scénario B : `kubectl` · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Dérouler un incident complet — **détecter, investiguer, rétablir, empêcher la récurrence** — avec
la règle qui compte en astreinte : **l'agent investigue, l'humain agit**. Puis produire un
post-mortem *blameless* dont chaque action a un propriétaire et une échéance.

Deux scénarios, injectés par le formateur sans dire lequel :

| | Scénario **A — Dev** : un contrat cassé | Scénario **B — DevOps** : une rotation à moitié faite |
|---|---|---|
| Symptôme annoncé | « Des commandes sont enregistrées à 0,00 € » | « Le catalogue est vide et les commandes échouent » |
| Ce qui s'est passé | Un commit « cosmétique » renomme un champ JSON de Catalog ; les tests de chaque service restent **verts** | Le Secret de la base a changé, pas le mot de passe dans PostgreSQL |
| Où chercher | Logs structurés et traces (MCP Aspire), métrique `ecommerce.order.amount`, `git log` | Pods, events, logs (`kubectl`), historique des Secrets et des rollouts |
| Ce qui empêche la récurrence | Un **test de contrat**, retrouvé par `git bisect run` | Un **runbook de rotation** des deux côtés, et des migrations hors démarrage |

## 2. Pré-requis

- Scénario A : [Lab 04](../lab-04-postgresql/) et [Lab 10](../lab-10-observabilite/) parcours Dev
  (Catalog sur PostgreSQL, télémétrie métier, serveur MCP Aspire).
- Scénario B : [Lab 08](../lab-08-kubernetes/) ou [Lab 09](../lab-09-helm/) (application sur `ecom-dev`).
- Le hook d'audit actif (`/hooks`) **avant** l'incident, pas après.

**Formateur :** les scripts d'injection sont dans [`solution/trainer/`](solution/trainer/).

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **Sous-agent** `incident-analyst` | Timeline, trois hypothèses étayées, en lecture seule | Le bruit de l'investigation reste hors de la session qui doit décider |
| **Sous-agent** `api-contract-reviewer` (module 07) | Détecter un changement de contrat entre services | Un regard ciblé, indépendant |
| **MCP** Aspire (A) | Logs structurés et traces de l'application en cours | Les preuves sont dans la télémétrie, pas dans le code |
| **Skill** `gen-tests` | Écrire le test qui reproduit **avant** de corriger | Un correctif sans test revient |
| **Skill** `postmortem` | Le format d'équipe, blameless | Une doctrine de rédaction |
| **Hooks** `audit-log`, `guard-destructive` | Tracer l'investigation ; interdire l'action irréversible sous stress | Sous pression, à 3 h du matin, le hook ne fatigue pas |

---

## 4A. Scénario A — un contrat cassé (Dev)

### Détecter (5 min)

```bash
cd ~/lab-ecommerce && git pull && aspire run        # terminal 1
claude                                              # terminal 2
```

Passez deux commandes depuis l'interface. Constat : total `0,00 €`, et les prix du catalogue à
`$0.00`.

### Investiguer (15 min)

```text
> Incident : des commandes sont enregistrées à 0,00 €. Fais investiguer par incident-analyst :
  timeline, trois hypothèses classées avec leurs preuves. Utilise d'abord la télémétrie (serveur
  aspire : logs structurés d'ordering et de catalog, traces de création de commande), puis
  l'historique Git récent. Lecture seule.
```

Ce qu'on attend :
- les **logs structurés** montrent `Order … confirmed: 2 line(s), total 0` — pas d'exception ;
- l'histogramme `ecommerce.order.amount` s'effondre (le Lab 10 vient de servir) ;
- `git log --since` fait apparaître un commit `style(catalog): align product price naming…`.

Puis le regard ciblé :

```text
> Fais relire les 5 derniers commits par api-contract-reviewer : un contrat entre services
  a-t-il changé, et qui le consomme ?
```

> **Pourquoi aucun test n'a rougi.** Les tests de Catalog relisent la réponse avec **la même**
> classe `Product` : renommer le champ des deux côtés passe. Ceux d'Ordering parlent à un **faux**
> Catalog, figé sur l'ancien contrat. Chaque service est vert ; leur assemblage est faux.
> (Vérifié : les 9 + 5 tests restent verts après l'injection.)

### Prouver, puis rétablir (10 min)

**D'abord le test qui reproduit**, avant tout correctif :

```text
> Écris un test de contrat dans ECommerce.Catalog.Tests qui lit le JSON BRUT de
  GET /api/products/1 (sans passer par la classe Product) et exige les champs id, name, price,
  availableStock — ceux que consomment Ordering et Web. Ne le committe pas.
```

Il doit **échouer** sur `HEAD`. Puis laissez Git trouver le coupable — le test, non committé,
reste présent à chaque étape de la bissection :

```bash
git bisect start HEAD <commit-d-avant-l-incident>
git bisect run sh -c 'dotnet test tests/ECommerce.Catalog.Tests --filter "FullyQualifiedName~CatalogContractTests" > /dev/null 2>&1'
git bisect reset
```

Résultat attendu (vérifié) : `style(catalog): align product price naming with front conventions`
est désigné comme *first bad commit*.

**Rétablir** — c'est vous qui décidez, l'agent propose :

```text
> Quelle est l'action de rétablissement la plus sûre, et son risque ?
```

Un `git revert` du commit fautif (jamais un `reset --hard` sur une branche partagée — le hook le
bloquerait de toute façon), le test de contrat committé **avec** le revert, `/ship`.

---

## 4B. Scénario B — une rotation à moitié faite (DevOps)

### Détecter et investiguer (15 min)

```text
> Incident : le catalogue est vide et les commandes échouent depuis quelques minutes.
  Fais investiguer par incident-analyst sur le namespace ecommerce : pods, events, logs du pod
  qui a crashé (--previous), historique des rollouts. Lecture seule. Ne m'affiche aucun Secret.
```

Ce qu'on attend :
- `catalog` en `CrashLoopBackOff` ; dans les logs `--previous` : `28P01: password authentication
  failed for user "catalog_app"` au moment de la migration de démarrage ;
- `postgres` sain ;
- les **métadonnées** du Secret — jamais sa valeur — montrent une modification récente :
  `kubectl -n ecommerce get secret catalog-db --show-managed-fields -o jsonpath='{.metadata.managedFields[*].time}'`.

Hypothèse retenue : le Secret a changé, le mot de passe du rôle en base non — `POSTGRES_PASSWORD`
n'est lu **qu'à la première initialisation** du volume (le Lab 08 l'avait annoncé).

### Rétablir — par vous (10 min)

Deux options ; l'agent les présente, **vous** choisissez et exécutez. La plus propre : aligner la
base sur le nouveau Secret, sans jamais afficher la valeur :

```bash
NEW="$(kubectl -n ecommerce get secret catalog-db -o jsonpath='{.data.password}' | base64 -d)"
printf "ALTER ROLE catalog_app PASSWORD :'pw';\n" | \
  kubectl -n ecommerce exec -i postgres-0 -- psql -U catalog_app -d catalogdb -v pw="$NEW"
unset NEW
kubectl -n ecommerce rollout restart deployment/catalog
kubectl -n ecommerce get pods -w
```

> **En astreinte, la tentation est de laisser l'agent corriger pour gagner deux minutes.** C'est
> précisément le moment où la règle R2 protège : sous stress, personne ne relit correctement une
> commande proposée. Et ici, la correction manipule un secret : ni l'agent ni la session n'ont à
> le voir.

---

## 5. Pour les deux scénarios — le post-mortem (15 min)

```text
> Rédige le post-mortem de l'incident avec le skill postmortem, dans
  docs/postmortems/<date>-<titre>.md : timeline sourcée, impact chiffré (commandes concernées,
  durée), cause racine distinguée des facteurs aggravants et de détection, ce qui a marché et
  manqué, actions avec propriétaire (rôle) et échéance, MTTD et MTTR.
```

**Le critère de qualité :** au moins une action **empêche la récurrence** de façon vérifiable :

| Scénario | Action de fond attendue |
|---|---|
| A | Le test de contrat dans la CI ; le sous-agent `api-contract-reviewer` dans `/ship` ; une alerte sur le montant médian des commandes |
| B | Un runbook (ou un skill) de rotation qui change **la base puis le Secret** ; les migrations dans un `Job`, plus au démarrage |

Un post-mortem qui se termine par « il faudrait améliorer le monitoring » n'a servi à rien.

Enfin, la trace :

```bash
jq -r '"\(.ts) \(.tool) \(.command // .file // "-")"' ~/.claude/audit/$(date -u +%F).jsonl | tail -30
```

La chronologie exacte de l'investigation : la pièce qu'un auditeur DORA demandera.

---

## 6. Livrable

```
docs/postmortems/AAAA-MM-JJ-<titre>.md                 # blameless, actions assignées
tests/ECommerce.Catalog.Tests/CatalogContractTests.cs  # scénario A : le test qui manquait
(scénario B) un runbook de rotation, dans docs/ ou en skill
~/.claude/audit/*.jsonl                                # la trace de l'investigation
```

## 7. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| L'agent n'agit pas sur un système en incident (R2) | Sous-agents en lecture seule + `guard-destructive` | Contrôle |
| Aucun secret affiché (R1) | Interdits du sous-agent ; la valeur ne transite que dans votre shell | Consigne + pratique |
| Blameless | Règle du skill `postmortem` ; `git log` lu pour le commit, pas l'auteur | Consigne |
| Traçabilité complète (R5) | Hook `audit-log` | Contrôle |
| Aucune conclusion sans preuve | Format imposé d'`incident-analyst` | Consigne |

## 8. Pour aller plus loin

- Rejouez l'autre scénario, et comparez le MTTR avec et sans le sous-agent.
- Transformez le runbook du scénario B en skill `rotate-db-password` avec
  `disable-model-invocation: true` : seul un humain le déclenche.
- Faites produire par l'agent, à partir du post-mortem, le ticket de chaque action (MCP Atlassian ou GitHub issues).

## Corrigé

```bash
cp "$FORMATION/labs/lab-11-incident-postmortem/solution/tests/ECommerce.Catalog.Tests/CatalogContractTests.cs" \
   ~/lab-ecommerce/tests/ECommerce.Catalog.Tests/
mkdir -p ~/lab-ecommerce/docs/postmortems
cp "$FORMATION/labs/lab-11-incident-postmortem/solution/docs/postmortems/TEMPLATE.md" ~/lab-ecommerce/docs/postmortems/
```

Vérifications faites (scénario A) : après injection, les suites Catalog (9 tests) et Ordering
(5 tests) restent vertes ; le test de contrat échoue sur `HEAD` ; `git bisect run` désigne le commit
injecté. Le scénario B a été vérifié pour sa syntaxe et sa garde de contexte kubectl, pas exécuté sur cluster.
