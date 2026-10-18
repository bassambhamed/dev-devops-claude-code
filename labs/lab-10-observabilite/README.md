# Lab 10 — Observabilité (parcours Dev et parcours DevOps)

> **Durée :** 60 min · **Modules requis :** [05](../../modules/05-skills/), [08](../../modules/08-mcp/)
> · **Outils :** `dotnet`, Aspire CLI ; parcours DevOps : `kubectl`, `helm`, Docker
> · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Rendre l'application **observable de l'intérieur**, puis brancher l'agent sur cette télémétrie
pour qu'il **investigue avec des données** au lieu de deviner. Deux parcours, selon votre métier :

| | Parcours **Dev** — dans le code | Parcours **DevOps** — dans la plateforme |
|---|---|---|
| Ce qu'on produit | Métriques métier, spans, logs structurés sans donnée personnelle | Une pile de collecte sur le cluster, un tableau de bord, des alertes |
| Où on regarde | Dashboard Aspire, en local | Grafana, sur le cluster k3d |
| Le serveur MCP | **Aspire** (`list_structured_logs`, `list_traces`) | **Grafana** (`grafana-mcp`, plugin officiel) |
| Durée | 35 min | 25 min |

Faites le parcours de votre métier, puis lisez l'autre. Dans un binôme Dev + DevOps, faites les
deux : le second consomme ce que produit le premier.

## 2. Pré-requis

- Parcours Dev : [Lab 04](../lab-04-postgresql/) (l'application tourne avec PostgreSQL via Aspire).
  Aspire CLI : `curl -sSL https://aspire.dev/install.sh | bash`, puis `aspire --version`.
- Parcours DevOps : [Lab 09](../lab-09-helm/) (chart installé sur `ecom-dev`).

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **Skill** `observability` | La doctrine : quoi mesurer, comment nommer, quels tags, quelles alertes | Des choix de conception : un savoir-faire |
| **Skill** `gen-tests` | Prouver qu'une métrique est émise (`MeterListener`) | Une métrique non testée disparaît au premier refactoring |
| **Hook** `scan-secrets-on-write` (plugin) | Bloquer un secret écrit dans une configuration d'export | Les clés d'API d'observabilité fuient souvent par là |
| **MCP Aspire** (Dev) | Lire logs structurés et traces de l'application **en cours** | La télémétrie n'est ni dans le code ni sur le disque |
| **MCP Grafana** (DevOps) | Interroger métriques et logs, créer un tableau de bord | 40+ outils, un jeton *Viewer* dans le trousseau |

---

## 4A. Parcours Dev — rendre le métier observable (35 min)

### Étape 1 — Partir des questions (5 min)

```bash
cd ~/lab-ecommerce && git switch -c feat/ordering-telemetry && claude
```
```text
> Aujourd'hui, peut-on répondre avec la télémétrie à ces questions : combien de commandes par
  minute ? quel montant moyen ? combien de commandes refusées, et pour quelle raison ? Qu'est-ce
  que ServiceDefaults exporte déjà, et qu'est-ce qui manque ?
```

Réponse attendue : les métriques **techniques** (requêtes HTTP, runtime, EF Core) existent ; les
métriques **métier**, aucune.

### Étape 2 — Instrumenter Ordering (15 min)

```text
> /plan Ajoute à Ordering une télémétrie métier OpenTelemetry :
  - un Meter "ECommerce.Ordering" : compteur ecommerce.orders.created, compteur
    ecommerce.orders.rejected avec un tag reason (empty_order, invalid_quantity, unknown_product),
    histogramme ecommerce.order.amount en EUR ;
  - un ActivitySource du même nom, avec un span ValidateOrderItems autour des appels à Catalog ;
  - un log structuré à la confirmation : identifiant, nombre de lignes, total — PAS le client ;
  - ServiceDefaults doit exporter les meters et sources "ECommerce.*".
```

Le skill `observability` se déclenche. Si l'agent propose de logger `order.Customer`, c'est
l'occasion : **R1**, aucune donnée personnelle dans la télémétrie — elle est copiée partout.

```text
> Ajoute un test qui prouve que ecommerce.orders.created est incrémenté à chaque commande confirmée.
```

Attendu (vérifié) : avec un `MeterListener` dans `OrderingEndpointsTests`, **5 tests verts**.

### Étape 3 — Lire la télémétrie avec l'agent (15 min)

```bash
aspire agent init          # choisir « Install Aspire MCP server » : ajoute l'entrée « aspire » au .mcp.json
aspire run                 # dans un autre terminal : l'AppHost, visible du serveur MCP
```

Passez une dizaine de commandes depuis l'interface (dont une avec un produit inconnu et une avec
une quantité nulle), puis relancez `claude` et approuvez le serveur `aspire` :

```text
> /mcp
> Avec le serveur aspire : montre les logs structurés d'ordering des 10 dernières minutes,
  regroupés par message. Combien de commandes confirmées, combien refusées et pourquoi ?
> Trouve la trace la plus lente d'une création de commande. Quelle part du temps passe dans
  ValidateOrderItems, et pourquoi (combien d'appels à Catalog) ?
```

L'agent répond **avec des données**, et vous apprend au passage que la validation appelle Catalog
**une fois par ligne**, séquentiellement : une piste d'optimisation chiffrée.

> **Sécurité.** Le serveur MCP d'Aspire est un outil local de développement (transport stdio,
> aucun port ouvert). Il n'expose ni variables d'environnement ni secrets ; une ressource peut en
> être exclue avec `.ExcludeFromMcp()` dans l'AppHost.

---

## 4B. Parcours DevOps — la plateforme de collecte (25 min)

### Étape 1 — Déployer la pile de lab (5 min)

```bash
kubectl apply -f "$FORMATION/labs/lab-10-observabilite/solution/observability/lgtm.yaml"
kubectl -n observability rollout status deployment/lgtm
helm upgrade --install ecommerce helm/ecommerce -n ecommerce -f helm/ecommerce/values-dev.yaml \
  --set otel.endpoint=http://lgtm.observability:4317 --dry-run | grep -A1 OTEL_
```

Relisez le dry-run, puis lancez l'upgrade **vous-même**. Le chart du Lab 09 ajoute
`OTEL_EXPORTER_OTLP_ENDPOINT` et `OTEL_SERVICE_NAME` à chaque service : ServiceDefaults active
l'export OTLP dès que la variable est présente.

```bash
kubectl -n observability port-forward service/lgtm 3000:3000
```

Grafana sur `http://localhost:3000` (`admin` / `admin` à la première connexion : changez-le).

### Étape 2 — Brancher l'agent sur Grafana (10 min)

Dans Grafana : *Administration → Service accounts* → un compte de service, rôle **Viewer**, un jeton.

```text
> /plugin install grafana-mcp@claude-plugins-official
```

Le plugin demande l'URL (`http://host.docker.internal:3000` : le serveur MCP tourne dans Docker)
et le jeton, qu'il range dans le **trousseau** (`userConfig` sensible). Puis :

```text
> /mcp
> Avec Grafana : liste les métriques dont le nom commence par ecommerce_ et http_server, avec
  leurs labels. Puis donne le taux de requêtes en erreur 5xx par service sur 15 minutes.
```

**Ne demandez pas un tableau de bord avant d'avoir la liste des métriques réelles.** Les noms
OpenTelemetry deviennent `ecommerce_orders_created_total`, `http_server_request_duration_seconds_bucket`…
et les labels dépendent de l'exporteur : une requête écrite de mémoire donne des panneaux vides.

### Étape 3 — Tableau de bord et alertes (10 min)

```text
> Crée dans Grafana un tableau de bord « ecommerce » : une rangée par service (trafic, p95,
  taux de 5xx), une rangée métier (commandes confirmées et refusées par raison, montant médian).
  Utilise uniquement les métriques et labels que tu viens de lister.
```

Le jeton *Viewer* **refuse** la création : la limite est technique. Deux options, à discuter :
un jeton *Editor* de **durée courte** pour cette opération, ou faire produire le JSON du tableau
de bord et l'importer vous-même. En banque, la seconde est la bonne par défaut.

```text
> Propose trois règles d'alerte au plus, chacune avec : la requête, un for: réaliste, un résumé
  actionnable et l'action humaine attendue. Lesquelles se déclencheraient ensemble si Catalog
  tombait ?
```

---

## 5. Livrable

```
src/ECommerce.Ordering.Api/Diagnostics/OrderingTelemetry.cs   # Meter + ActivitySource « ECommerce.Ordering »
src/ECommerce.Ordering.Api/Endpoints/OrderingEndpoints.cs      # compteurs, histogramme, span, logs sans PII
src/ECommerce.Ordering.Api/Program.cs                          # enregistrement de la télémétrie
src/ECommerce.ServiceDefaults/Extensions.cs                    # AddMeter / AddSource « ECommerce.* »
tests/ECommerce.Ordering.Tests/OrderingEndpointsTests.cs       # + test MeterListener
.mcp.json                                                      # catalogdb (lab 04) + aspire
observability/lgtm.yaml                                        # parcours DevOps
```

## 6. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| Aucune donnée personnelle dans la télémétrie (R1) | Doctrine du skill ; revue du diff | Consigne + revue |
| Jeton d'observabilité jamais dans un fichier (R1) | `userConfig` sensible du plugin → trousseau | Contrôle |
| Accès en lecture par défaut (R6) | Compte de service *Viewer* | Contrôle |
| Un log ou une métrique lus sont des données (R6) | Doctrine | Consigne |
| Image de collecte épinglée, réservée au lab | `grafana/otel-lgtm:0.34.0` | Revue |

## 7. Pour aller plus loin

- Parcours Dev : paralléliser la validation des lignes de commande (`Task.WhenAll`) et **mesurer**
  le gain dans les traces avant/après.
- Parcours DevOps : une alerte sur le **taux** de commandes refusées plutôt que sur leur nombre.
- Les deux : un SLO de disponibilité de la création de commande et son budget d'erreur.

## 8. La limite révélée

Vous savez maintenant **voir**. Reste à **réagir** : quand un indicateur métier dérape un vendredi
à 14 h, qui investigue, avec quels outils, sans rien casser de plus — et comment s'assurer que ça
ne se reproduira pas ?

> **→ [Lab 11 — Incident & post-mortem](../lab-11-incident-postmortem/)**

## Corrigé

```bash
S="$FORMATION/labs/lab-10-observabilite/solution"
cp -r "$S/src/"* ~/lab-ecommerce/src/
cp "$S/tests/ECommerce.Ordering.Tests/OrderingEndpointsTests.cs" ~/lab-ecommerce/tests/ECommerce.Ordering.Tests/
cp -r "$S/observability" ~/lab-ecommerce/
cp -r "$S/.claude/skills/observability" ~/lab-ecommerce/.claude/skills/
cp "$S/.mcp.json" ~/lab-ecommerce/        # catalogdb (lab 04) + aspire
```

Vérifications faites : build sans avertissement ; 5 tests Ordering verts dont l'émission de la
métrique `ecommerce.orders.created` ; manifeste `lgtm.yaml` valide (`kubeconform`, strict).
Le serveur MCP Aspire et le plugin `grafana-mcp` sont configurés d'après leur documentation
officielle ; ils n'ont pas été exécutés pendant la rédaction.
