# Lab 09 — Packaging Helm

> **Durée :** 30 à 45 min (variable d'ajustement de J4) · **Modules requis :** [05](../../modules/05-skills/)
> · **Outils :** `helm`, `kubectl`, `k3d` · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Transformer les sept manifestes du [Lab 08](../lab-08-kubernetes/) en **un chart paramétrable**,
avec des values par environnement — et apprendre la règle d'or de Helm : **on relit le rendu, pas
le template**. Le chart prépare aussi le [Lab 10](../lab-10-observabilite/) : un paramètre
`otel.endpoint` branche l'export OpenTelemetry de tous les services.

## 2. Pré-requis

- [Lab 08](../lab-08-kubernetes/) terminé (cluster `ecom-dev`, Secret `catalog-db`).
- `helm version`.

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **Skill** `helm-package` | La convention de chart de l'équipe | Paramétrer sans dupliquer demande des choix : un savoir-faire |
| **Mode Plan** | Valider la structure des values avant les templates | La structure des values *est* l'API du chart |
| **`/code-review`** + sous-agent | Relire templates **et** rendu | Une erreur de template ne se voit que dans le rendu |
| **Hook** `guard-destructive` | Bloquer `helm uninstall` | Une désinstallation emporte la base si le chart la fournit |

---

## 4. Déroulé pas-à-pas

### Étape 1 — Concevoir les values (10 min)

```bash
cd ~/lab-ecommerce && git switch -c deploy/helm
cp -r "$FORMATION/labs/lab-09-helm/solution/.claude/skills/helm-package" .claude/skills/
claude
```
```text
> /plan Transforme k8s/ en chart helm/ecommerce. Avant d'écrire un template, propose la
  structure de values.yaml : tag d'image, ressources par défaut et par service, autoscaling,
  ingress, base (Secret existant, PostgreSQL fourni ou externe), endpoint OpenTelemetry
  optionnel, et la liste des services avec leurs dépendances de service discovery.
  Une boucle range sur les services, aucune valeur en dur dans templates/.
```

Discutez la structure **avant** de valider : c'est l'API du chart.

### Étape 2 — Générer et valider (10 min)

```bash
helm lint helm/ecommerce
helm lint helm/ecommerce -f helm/ecommerce/values-preprod.yaml
helm template ecommerce helm/ecommerce -n ecommerce -f helm/ecommerce/values-dev.yaml > /tmp/dev.yaml
```
```text
> Compare @/tmp/dev.yaml avec les manifestes de @k8s/ : liste précisément ce qui diffère et
  dis si une différence est une régression (probe perdue, variable manquante, securityContext
  absent, mot de passe apparu en clair).
```

### Étape 3 — Deux environnements, et le piège du rendu (10 min)

```bash
helm template ecommerce helm/ecommerce -n ecommerce -f helm/ecommerce/values-preprod.yaml > /tmp/preprod.yaml
diff <(grep -E 'kind:|replicas:|cpu|memory' /tmp/dev.yaml) <(grep -E 'kind:|replicas:|cpu|memory' /tmp/preprod.yaml)
```
```text
> values-preprod.yaml demande 2 réplicas pour gateway et web. Vérifie dans le RENDU que c'est
  bien appliqué. Si non, explique pourquoi, et dis si c'est un bug ou un comportement voulu.
```

**Ce que le rendu révèle** (constaté sur le corrigé) : en preprod l'autoscaling est activé, le
template n'écrit donc **pas** `replicas` dans les Deployments — c'est le HPA (min 2) qui décide.
Les `replicas: 2` de `values-preprod.yaml` sont **sans effet**. Pas un bug, mais une valeur
trompeuse : à documenter ou à supprimer. C'est exactement le genre d'écart qu'on ne voit qu'en
relisant le rendu.

### Étape 4 — Installer, prudemment (10 min)

```bash
helm upgrade --install ecommerce helm/ecommerce -n ecommerce \
  -f helm/ecommerce/values-dev.yaml --dry-run | head -40
```

Puis, **vous-même**, une fois le dry-run relu :

```bash
helm upgrade --install ecommerce helm/ecommerce -n ecommerce -f helm/ecommerce/values-dev.yaml
helm -n ecommerce status ecommerce
```

> Les ressources créées au Lab 08 par `kubectl apply` ne sont pas gérées par Helm : l'installation
> les refuserait. Supprimez-les d'abord, vous-même — le volume de la base (PVC) et le Secret sont
> conservés et seront repris par le chart :
> `kubectl -n ecommerce delete deployment,service,statefulset,hpa,ingress --all`

### Étape 5 — La revue (5 min)

```text
> /code-review
> Relis le chart : valeurs en dur restantes, conditions manquantes, et tout paramètre de
  sécurité (securityContext, ressources, Secret) qu'un values mal rempli pourrait contourner.
```

---

## 5. Livrable

```
helm/ecommerce/
├── Chart.yaml                       # version du chart incrémentée
├── values.yaml · values-dev.yaml · values-preprod.yaml
└── templates/
    ├── _helpers.tpl · deployment.yaml · service.yaml · hpa.yaml · ingress.yaml
    ├── postgres.yaml                # désactivable : database.postgres.enabled
    └── NOTES.txt                    # rappelle le Secret à créer
.claude/skills/helm-package/SKILL.md
```

## 6. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| Aucun secret dans les values (R1) | `database.existingSecret` ; `$(VAR)` dans le template | Contrôle |
| Pas d'upgrade sans dry-run relu (R2, R4) | Skill + `ask` sur `helm upgrade` | Consigne + permission |
| Pas de `helm uninstall` par l'agent (R2) | Hook `guard-destructive` | Contrôle |
| Le rendu est comparé, pas supposé (R4) | `helm template` + diff | Revue |

## 7. Pour aller plus loin

- Ajoutez des tests Helm (`templates/tests/`) qui appellent `/health` du gateway, et lancez `helm test`.
- Rendez `replicas` et `autoscaling` exclusifs dans le schéma des values (`values.schema.json`).
- Branchez le `cd.yml` du [Lab 06](../lab-06-ci-cd/) sur `helm upgrade --install --atomic`.

## 8. La limite révélée

L'application tourne, packagée et paramétrée. Mais quand un utilisateur dira « les commandes sont
fausses depuis 14 h », qu'aurez-vous pour répondre ? Ni métrique métier, ni trace exploitable, ni
tableau de bord : vous découvrirez le problème par les plaintes.

> **→ [Lab 10 — Observabilité](../lab-10-observabilite/)**

## Corrigé

```bash
cp -r "$FORMATION/labs/lab-09-helm/solution/helm" ~/lab-ecommerce/
cp -r "$FORMATION/labs/lab-09-helm/solution/.claude/skills/helm-package" ~/lab-ecommerce/.claude/skills/
```

Vérifications faites : `helm lint` sans erreur pour les trois jeux de values ; rendus dev,
preprod et « OTel + base externe » valides pour `kubeconform` en mode strict (35 ressources) ;
mot de passe absent de tout rendu (seule la référence au Secret apparaît).
