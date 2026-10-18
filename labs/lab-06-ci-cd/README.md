# Lab 06 — Pipeline CI/CD

> **Durée :** 60 min · **Modules requis :** [05](../../modules/05-skills/) et l'[annexe — l'agent sans terminal](../../modules/annexe-agent-sans-terminal/)
> · **Outils :** `gh`, `dotnet` · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Produire la chaîne d'intégration et de livraison de l'application : build, tests **contre un vrai
PostgreSQL** (Testcontainers), script SQL des migrations en artefact, déploiement en deux étages
**avec un gate humain** avant la production — et une **revue assistée par Claude** en mode
headless, qui commente chaque PR sans rien décider.

## 2. Pré-requis

- [Lab 01](../lab-01-git-github/) : dépôt GitHub ; [Lab 02](../lab-02-tests/) et [Lab 04](../lab-04-postgresql/) : tests.
- `gh auth status` valide.
- Pour la revue Claude : une clé d'API Anthropic **de test**, ajoutée comme secret du dépôt
  (`gh secret set ANTHROPIC_API_KEY`) — jamais dans un fichier.

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **Skill** `ci-pipeline` | La doctrine de pipeline : permissions minimales, gate, actions épinglées | Des règles d'équipe à appliquer à chaque workflow écrit |
| **Mode headless** (`claude -p`, voir l'[annexe](../../modules/annexe-agent-sans-terminal/)) | La revue du diff et du SQL dans la CI | Pas une brique : les mêmes, sans terminal — personne n'est là à 23 h |
| **MCP GitHub** (module 08) | Lire l'état des runs, diagnostiquer un échec | L'API GitHub, en lecture seule, sans quitter la session |
| **`/security-review`** + `security-reviewer` | Auditer les workflows produits | Un pipeline manipule des secrets : c'est du code sensible |

---

## 4. Déroulé pas-à-pas

### Étape 1 — La CI (15 min)

```bash
cd ~/lab-ecommerce && git switch -c ci/pipeline && claude
```
```text
> /plan Écris .github/workflows/ci.yml : sur push et PR vers main ; job 1 : restore, build
  Release, dotnet test de ECommerce.slnx (les tests du catalogue utilisent Testcontainers) et
  publication des résultats ; job 2 : script SQL idempotent des migrations du catalogue, en
  artefact. Aucun déploiement.
```

Le skill `ci-pipeline` doit se déclencher. Avant de valider, vérifiez trois points :

- `permissions:` explicites et minimales (`contents: read`) ;
- actions épinglées (`@v4`) ;
- aucune étape qui déploie.

```bash
git add .github/workflows/ci.yml && git commit -m "ci: add build, test and migration script"
git push -u origin ci/pipeline && gh pr create --fill
gh run watch
```

> **Ce qui se passe :** les tests Testcontainers démarrent `postgres:17-alpine` sur le runner.
> Le même moteur que l'AppHost, le même que le cluster du [Lab 08](../lab-08-kubernetes/).

### Étape 2 — Diagnostiquer un échec sans quitter le terminal (10 min)

Cassez volontairement un test :

```bash
sed -i.bak 's/2 \* 329.00m + 119.99m/2 * 329.00m/' tests/ECommerce.Ordering.Tests/OrderingEndpointsTests.cs && rm -f tests/ECommerce.Ordering.Tests/*.bak
git commit -qam "test: break the build on purpose" && git push
```
```text
> Le dernier run de CI a échoué. Lis ses logs et explique la cause en trois lignes.
```

Avec le serveur MCP GitHub (module 08), il lit les logs du run directement ; sinon il utilise
`gh run view --log-failed`. Remettez le test : `git revert HEAD --no-edit && git push`.

### Étape 3 — La CD, avec un gate (10 min)

```text
> /plan Écris .github/workflows/cd.yml : déclenché après une CI verte sur main
  (workflow_run), déploiement staging automatique, production uniquement via un
  environnement protégé. Les étapes de déploiement restent des echo commentés : Helm arrive au
  lab 09.
```

Puis configurez la protection **côté GitHub** — c'est elle, le contrôle :

```bash
gh api -X PUT "repos/{owner}/{repo}/environments/production" \
  -f "reviewers[][type]=User" -F "reviewers[][id]=$(gh api user --jq .id)"
```

> **Ce qui protège la production, ce n'est pas le YAML : c'est la règle d'environnement côté
> forge.** Le workflow décrit l'intention ; la protection l'impose. Niveau 5 des
> [garde-fous](../../docs/garde-fous.md).

### Étape 4 — L'agent dans la CI (15 min)

Ajoutez le secret, puis le workflow de revue :

```bash
gh secret set ANTHROPIC_API_KEY          # collez la clé de test : elle n'apparaît nulle part
cp "$FORMATION/labs/lab-06-ci-cd/solution/.github/workflows/claude-review.yml" .github/workflows/
```

Lisez-le avant de le committer. Points à vérifier :

| Point | Pourquoi |
|---|---|
| `-p` présent | Sinon le job attend un humain, puis expire |
| `--allowedTools "Read,Grep,Glob"` / `"Read"` | Le job **ne peut pas** écrire |
| `--max-turns` | Coût et durée bornés |
| `permissions: pull-requests: write` et rien d'autre | Le seul droit d'écriture : commenter |
| `if: … head.repo.full_name == github.repository` | Une PR venue d'un fork ne reçoit pas vos secrets |

Ouvrez une PR qui modifie un endpoint **et** ajoute une migration (par exemple une colonne `Brand`
nullable sur `Products`, via le skill `ef-migration`). La PR reçoit un commentaire avec la revue du
diff, puis celle du SQL.

### Étape 5 — Auditer le pipeline qui appelle l'agent (10 min)

```text
> /security-review
> Fais relire .github/workflows/ par security-reviewer : quels secrets sont exposés à quels
  jobs ? Un fork peut-il déclencher un job avec mes secrets ? Un secret peut-il finir dans les
  logs ? Une action non épinglée peut-elle changer sous mes pieds ?
```

---

## 5. Livrable

```
.github/workflows/
├── ci.yml              # build, tests Testcontainers, script SQL des migrations — aucun déploiement
├── cd.yml              # staging automatique, production derrière un environnement protégé
└── claude-review.yml   # revue headless du diff et du SQL, en commentaire de PR
```

## 6. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| Aucun déploiement en production automatique (R3) | Environnement `production` protégé côté GitHub | Contrôle de plateforme |
| La revue Claude ne peut rien modifier | `--allowedTools` en lecture + `permissions` minimales | Contrôle |
| Pas de secrets pour les forks | Condition `if` du job de revue | Contrôle |
| Aucun secret dans le YAML | `secrets.*` ; audit par `security-reviewer` | Contrôle + revue |
| Le SQL des migrations est relu avant production (R4) | Artefact CI + revue Claude + revue humaine | Revue |

## 7. Pour aller plus loin

- Essayez `/install-github-app` : l'application GitHub de Claude, déclenchée par `@claude` dans une PR.
  Comparez avec votre job : qui contrôle les outils et les permissions ?
- Ajoutez le workflow `security.yml` du [Lab 03](../lab-03-securite-secrets/) comme contrôle requis
  de la branche `main` (protection de branche).
- Faites commenter par l'agent uniquement ce qui a changé depuis sa revue précédente.

## 8. La limite révélée

La CI construit et teste du **code**. Mais ce qu'on déploie, ce sont des **artefacts** : des images
de conteneur, avec leur système de base, leurs dépendances, leur utilisateur. Rien ne les construit,
rien ne les scanne encore.

> **→ [Lab 07 — Conteneurisation](../lab-07-docker/)**

## Corrigé

```bash
cp -r "$FORMATION/labs/lab-06-ci-cd/solution/.github" ~/lab-ecommerce/
```

Les trois workflows du corrigé sont syntaxiquement valides et n'utilisent que des actions
épinglées existantes (`actions/checkout@v4`, `actions/setup-dotnet@v4`,
`actions/upload-artifact@v4`).
