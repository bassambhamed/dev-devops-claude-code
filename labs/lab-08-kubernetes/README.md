# Lab 08 — Kubernetes

> **Durée :** 60 min · **Modules requis :** [05](../../modules/05-skills/), [07](../../modules/07-sous-agents/)
> · **Outils :** `k3d`, `kubectl`, Docker · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Monter un cluster k3d local, y déployer l'application **et sa base PostgreSQL**, avec un mot de
passe qui ne figure dans **aucun** fichier — puis provoquer trois pannes et les faire
diagnostiquer par un sous-agent qui ne peut rien modifier.

Le point technique central : la différence entre **readiness** et **liveness** quand un service
dépend d'une base.

## 2. Pré-requis

- [Lab 07](../lab-07-docker/) terminé : les quatre images `ecommerce-*:dev` existent localement.

```bash
k3d version && kubectl version --client && docker images | grep 'ecommerce-.*dev'
```

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **Skill** `k8s-bootstrap` | Créer le cluster, importer, appliquer, vérifier | Une procédure ordonnée, avec un arrêt obligatoire (le Secret) |
| **Sous-agent** `k8s-debug-pod` | Diagnostiquer un pod en échec, en lecture seule | 800 lignes d'events et de logs lues ailleurs ; aucune commande d'écriture possible |
| **Hook** `guard-destructive` (plugin) | Bloquer `kubectl delete ns`, `k3d cluster delete` | Une suppression de namespace emporte la base |
| **Hook** `session-start` (plugin) | Afficher le contexte kubectl courant | Ne jamais agir sur le mauvais cluster |

---

## 4. Déroulé pas-à-pas

### Étape 1 — Le cluster (10 min)

```bash
cd ~/lab-ecommerce && git switch -c deploy/k8s
cp -r "$FORMATION/labs/lab-08-kubernetes/solution/.claude/skills/k8s-bootstrap" .claude/skills/
claude
```
```text
> /plan Monte le cluster k3d de l'application à partir de k8s/k3d-cluster.yaml (cluster
  ecom-dev, 1 serveur, 2 agents, ingress sur le port 8081), puis importe les quatre images
  ecommerce-*:dev. Vérifie le contexte kubectl avant toute autre commande.
```

Regardez le message de démarrage de session : le hook `session-start` affiche le contexte kubectl.
Après création, il doit être `k3d-ecom-dev`.

### Étape 2 — Le Secret : par vous, hors session (5 min)

```bash
kubectl create namespace ecommerce
kubectl -n ecommerce create secret generic catalog-db --from-literal=password="$(openssl rand -hex 24)"
```

Personne — ni vous, ni l'agent — n'a vu la valeur. Le skill vérifie seulement que le Secret
**existe** (`kubectl get secret catalog-db`), jamais son contenu.

### Étape 3 — Les manifestes (20 min)

```text
> /plan Écris les manifestes k8s/ :
  - postgres.yaml : StatefulSet postgres:17-alpine à une réplique, Service headless, volume
    persistant 1 Gi, mot de passe lu dans le Secret catalog-db, readiness pg_isready,
    exécution non-root ;
  - catalog.yaml : ConnectionStrings__catalogdb composée dans le pod à partir du Secret (sans
    aucun mot de passe dans le fichier), readiness /health, liveness /alive ;
  - ordering, gateway, web : service discovery par services__<nom>__http__0 ;
  - ingress vers web. Requests et limits partout.
```

**Avant de valider, faites expliquer :**

```text
> Sur catalog, /health inclut un contrôle de la base (AddNpgsqlDbContext) et /alive non.
  Que se passe-t-il si PostgreSQL tombe ? Et si j'avais mis /health en liveness ?
```

Réponse attendue : base indisponible → Catalog **retiré du trafic** (readiness) mais **pas
redémarré** (liveness). Avec `/health` en liveness, une panne de base ferait redémarrer en boucle
des pods sains — et aggraverait l'incident.

Deux points du corrigé à remarquer :

- la chaîne de connexion est **composée** par Kubernetes avec la syntaxe `$(CATALOG_DB_PASSWORD)` ;
- `POSTGRES_PASSWORD` n'est lu **qu'à la première initialisation** du volume : changer le
  Secret ensuite ne change pas le mot de passe en base. (Gardez-le en tête : c'est l'incident B du
  [Lab 11](../lab-11-incident-postmortem/).)

### Étape 4 — Déployer et vérifier (10 min)

```text
> Applique les manifestes avec le skill k8s-bootstrap et vérifie chaque rollout.
```

```bash
kubectl -n ecommerce get pods
curl -s http://ecommerce.localhost:8081/products | grep -o 'All categories\|in stock' | sort | uniq -c
```

En environnement Development, Catalog applique ses migrations au démarrage : acceptable avec une
réplique. Faites expliquer pourquoi ce n'est **pas** acceptable avec trois (et ce qu'on ferait :
un `Job` de migration, revu, avant le déploiement).

### Étape 5 — Trois pannes, un sous-agent (15 min)

Provoquez chaque panne **vous-même** (l'agent n'a pas à casser votre cluster), puis demandez le
diagnostic **sans dire ce que vous avez fait**.

**Panne A — image inexistante**
```bash
kubectl -n ecommerce set image deployment/ordering ordering=ecommerce-ordering:v99
```
```text
> Le service ordering ne répond plus. Diagnostique.
```
Attendu : `ImagePullBackOff`, tag inexistant ; correctif proposé, **non appliqué**.

**Panne B — mémoire insuffisante**
```bash
kubectl -n ecommerce set resources deployment/gateway --limits=memory=24Mi
```
```text
> Le gateway redémarre en boucle. Diagnostique.
```
Attendu : `OOMKilled` dans `Last State`.

**Panne C — la base disparaît**
```bash
kubectl -n ecommerce scale statefulset/postgres --replicas=0
```
```text
> Le catalogue ne répond plus mais ses pods ne redémarrent pas. Pourquoi ?
```
Attendu : readiness de Catalog en échec (`/health` → 503, contrôle de la base), liveness OK,
**0 redémarrage** : exactement le comportement voulu à l'étape 3.

À chaque fois, le sous-agent `k8s-debug-pod` doit **citer la preuve** (event ou ligne de log)
avant de conclure. Vérifiez avec `/context` que votre session n'a pas absorbé les logs. Puis
demandez-lui de corriger lui-même : il **ne peut pas** (outils en lecture seule).

Restaurez entre chaque panne :

```bash
kubectl -n ecommerce rollout undo deployment/ordering
kubectl -n ecommerce rollout undo deployment/gateway
kubectl -n ecommerce scale statefulset/postgres --replicas=1
```

### Étape 6 — Ce que l'agent ne supprimera pas (5 min)

```text
> On a fini : supprime le namespace ecommerce.
```

**Refusé** par `guard-destructive`. Le namespace contient le volume de la base : c'est à vous de
décider, hors session.

---

## 5. Livrable

```
k8s/
├── k3d-cluster.yaml     # ecom-dev, ingress sur 8081
├── namespace.yaml
├── postgres.yaml        # StatefulSet + Service headless + volume ; mot de passe via Secret
├── catalog.yaml         # chaîne de connexion composée depuis le Secret ; readiness ≠ liveness
├── ordering.yaml · gateway.yaml · web.yaml
└── ingress.yaml
.claude/skills/k8s-bootstrap/SKILL.md
(cluster) Secret catalog-db — créé à la main, jamais versionné
```

## 6. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| Aucun mot de passe dans un fichier (R1) | Secret créé à la main ; `$(VAR)` dans le manifeste | Contrôle |
| L'agent n'affiche pas un Secret | Skill + sous-agent : interdits explicites | Consigne |
| Le diagnostic ne modifie rien | `k8s-debug-pod` sans outil d'écriture | Contrôle |
| Pas de suppression de namespace, de PVC ou de cluster (R2) | Hook `guard-destructive` + `deny` | Contrôle |
| Le bon cluster | Hook `session-start` + vérification du contexte par le skill | Contrôle + consigne |

## 7. Pour aller plus loin

- Remplacez `Migrate()` au démarrage par un `Job` qui exécute un *migration bundle*
  (`dotnet ef migrations bundle`), lancé avant le rollout.
- Ajoutez `readOnlyRootFilesystem: true` aux conteneurs .NET, avec un `emptyDir` sur `/tmp` — et
  vérifiez que l'application démarre toujours.
- Ajoutez une `NetworkPolicy` : seul `catalog` peut joindre `postgres:5432`.
- Faites générer un runbook d'astreinte pour chacune des trois pannes.

## 8. La limite révélée

Sept fichiers, des valeurs répétées (ports, ressources, variables de service discovery), et
aucun moyen simple de déployer **la même** application en staging avec deux réplicas et plus de
mémoire. Chaque environnement deviendrait une copie à maintenir à la main.

> **→ [Lab 09 — Helm](../lab-09-helm/)**

## Corrigé

```bash
cp -r "$FORMATION/labs/lab-08-kubernetes/solution/k8s" ~/lab-ecommerce/
cp -r "$FORMATION/labs/lab-08-kubernetes/solution/.claude/skills/k8s-bootstrap" ~/lab-ecommerce/.claude/skills/
```

Vérifications faites : les 16 ressources passent `kubeconform` en mode strict (schémas
Kubernetes 1.33). Les manifestes n'ont **pas** été exécutés sur un cluster lors de la rédaction :
la première passe en formation se fait avec le formateur.
