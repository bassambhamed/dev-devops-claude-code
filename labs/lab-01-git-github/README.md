# Lab 01 — Git & GitHub assistés

> **Durée :** 60 min · **Modules requis :** [00](../../modules/00-prise-en-main/) →
> [03](../../modules/03-commandes-personnalisees/) · **Outils :** `git`, `gh`, `dotnet`
> · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Partir d'une application non versionnée et livrer **un vrai correctif** jusqu'à une Pull Request
documentée — en faisant porter le travail répétitif par la mémoire projet et les commandes
d'équipe. Puis constater, sur un cas concret, ce qu'une commande **ne peut pas** garantir.

Le correctif : aujourd'hui, `POST /api/orders` accepte une quantité nulle ou négative. Une
commande de « -3 claviers » est enregistrée, avec un total négatif.

## 2. Pré-requis

```bash
git --version && gh --version
gh auth login        # une seule fois : GitHub.com → HTTPS → navigateur
gh auth status
```

Un compte GitHub **personnel ou de test**, jamais l'organisation de production. Votre copie de
travail (module 00) : `~/lab-ecommerce`.

## 3. Briques mobilisées — et pourquoi elles suffisent ici

| Brique | Rôle dans ce lab | Pourquoi elle convient |
|---|---|---|
| **`CLAUDE.md`** | Conventions de branches, de commits, d'interdits | Ce sont des connaissances stables du projet |
| **Commandes natives** | `/plan`, `/code-review`, `/rewind` | Cadrer et relire une modification |
| **Commandes perso** | `/init-repo`, `/review-diff`, `/ship` | Des prompts d'équipe, déclenchés **par vous** au bon moment |
| `gh` (CLI) | Créer le dépôt, ouvrir la PR | Pas besoin de MCP : la CLI fait très bien ce travail |

---

## 4. Déroulé pas-à-pas

### Étape 1 — La mémoire du projet (10 min)

```bash
cd ~/lab-ecommerce && claude
```
```text
> /init
```

Éditez le `CLAUDE.md` produit : sections **Commandes**, **Conventions**, **Interdits**. Modèle :
[`solution/CLAUDE.md`](solution/CLAUDE.md). Puis, à la volée :

```text
> # branches : feat/, fix/, chore/, test/, ci/ — jamais de travail direct sur main
> # commits : Conventional Commits, en anglais, à l'impératif ; scopes catalog, ordering, gateway, web, db, ci
```

### Étape 2 — Initialiser, puis capitaliser (10 min)

Faites-le une fois **à la main** pour savoir ce que la commande automatisera :

```bash
git init && git branch -M main
git status                 # contrôle visuel : ni bin/, ni obj/, ni .env
git add . && git commit -m "chore: initial commit"
gh repo create lab-ecommerce --private --source=. --remote=origin --push
```

Puis capitalisez la procédure :

```text
> Crée .claude/commands/init-repo.md : une commande qui initialise le dépôt, vérifie le
  .gitignore (.env, *.pem, *.key, appsettings.*.local.json, bin/, obj/), montre git status
  et attend ma validation, puis DEMANDE confirmation avant gh repo create --private.
  Elle refuse de toucher un dépôt qui a déjà un remote.
```

Elle grossira : au [module 05](../../modules/05-skills/), elle deviendra un skill.

### Étape 3 — Le correctif, sous contrôle (15 min)

```text
> Crée une branche pour corriger ce bug : POST /api/orders accepte une quantité nulle ou
  négative.
```

Il doit proposer `fix/...` — c'est `CLAUDE.md` qui le lui dit.

```text
> /plan Refuse en 400 toute ligne de commande dont la quantité est inférieure ou égale à 0,
  avec un message explicite. Ne touche à rien d'autre.
```

Validez le plan, laissez-le implémenter, puis vérifiez **vous-même** :

```bash
dotnet build ECommerce.slnx
dotnet run --project src/ECommerce.Ordering.Api &       # port 5086, sans Catalog : suffit pour ce test
curl -s --retry 15 --retry-delay 1 --retry-all-errors -o /dev/null -w "%{http_code}\n" \
  -X POST http://localhost:5086/api/orders \
  -H "Content-Type: application/json" -d '{"customer":"Test","items":[{"productId":1,"quantity":-3}]}'
kill %1
```

`400` attendu.

### Étape 4 — Relire avec la commande d'équipe (5 min)

Créez `/review-diff` (module 03) si ce n'est pas fait, puis :

```text
> /review-diff
> /code-review
```

Deux regards : la **checklist de l'équipe**, puis la revue générique. La première doit signaler
qu'aucun test ne couvre ce comportement : notez-le, c'est le point de départ du
[Lab 02](../lab-02-tests/).

### Étape 5 — Livrer avec `/ship` (10 min)

Créez `.claude/commands/ship.md` à partir du [modèle](solution/.claude/commands/ship.md), puis :

```text
> /ship correctif de validation des quantités de commande
```

Observez qu'il **s'arrête** pour valider le message de commit, puis avant le push. Vérifiez la PR :

```bash
gh pr view --web
```

### Étape 6 — Le moment de vérité : ce qu'une commande ne garantit pas (10 min)

**L'étape la plus importante du lab.** Revenez sur `main`, créez une branche, et simulez l'erreur
classique : une chaîne de connexion de test collée dans la configuration.

```bash
git switch main && git pull && git switch -c chore/db-config
cat > src/ECommerce.Catalog.Api/appsettings.Development.json <<'EOF'
{
  "Logging": { "LogLevel": { "Default": "Information", "Microsoft.AspNetCore": "Warning" } },
  "ConnectionStrings": { "catalogdb": "Host=db;Username=app;Password=Sup3rS3cret!" }
}
EOF
```

**Cas A — avec la commande.**

```text
> /ship ajout de la configuration de base locale
```

Selon le contexte, l'agent signale le mot de passe (étape 2 de `/ship`)… ou pas. Notez ce qui se passe.

**Cas B — sans la commande, comme un collègue pressé.**

```text
> Commite tout ce qui est modifié, message "chore: local db config".
```

Le commit **passe**. Rien ne l'a empêché : `/ship` n'a pas été appelée, et `CLAUDE.md` n'est
qu'une consigne. Annulez — vous-même, la branche n'a pas été poussée :

```bash
git reset --soft HEAD~1 && git restore --staged . && git checkout -- src/ECommerce.Catalog.Api/appsettings.Development.json
git switch main && git branch -D chore/db-config
```

> En situation réelle, un secret committé est un secret **compromis**, même non poussé : il se
> révoque. Ici, la valeur est fictive.

---

## 5. Livrable

```
~/lab-ecommerce/
├── CLAUDE.md                                  # commandes, conventions, interdits vérifiables
├── .claude/commands/
│   ├── init-repo.md                           # initialisation guidée, confirmations
│   ├── review-diff.md                         # checklist de revue, lecture seule
│   └── ship.md                                # livraison en étapes validées
├── src/ECommerce.Ordering.Api/Endpoints/OrderingEndpoints.cs   # le correctif
└── (sur GitHub) une PR fix/… documentée
```

## 6. Garde-fous

| Règle | Mécanisme dans ce lab | Niveau de garantie |
|---|---|---|
| Aucun secret committé | Consigne dans `CLAUDE.md` + étape de `/ship` | **Consigne** — mis en défaut à l'étape 6 |
| Aucun push sans validation | Étape explicite de `/ship` | Consigne |
| Aucun merge par l'agent | Interdit dans `/ship` et `CLAUDE.md` | Consigne |
| Dépôt privé | `/init-repo` | Consigne |

Tous les garde-fous de ce lab sont des **consignes**. C'est voulu : le module suivant les
transforme en **contrôles**.

## 7. Pour aller plus loin

- Ajoutez `.github/pull_request_template.md` et faites-le remplir par `/ship`.
- Ajoutez un argument à `/review-diff` pour choisir la branche de base.
- Testez `/code-review` sur la PR d'un binôme.

## 8. La limite révélée

L'étape 6 l'a montré : une commande est une **consigne que vous déclenchez**. Elle n'agit pas
quand personne ne l'appelle, et elle dépend du jugement du modèle quand on l'appelle.

> **→ [Module 04 — Hooks](../../modules/04-hooks/) :** le même contrôle anti-secret, exécuté par le
> harnais à **chaque** `git commit`, quel que soit le prompt et quel que soit le développeur.

## Corrigé

```bash
cp "$FORMATION/labs/lab-01-git-github/solution/CLAUDE.md" ~/lab-ecommerce/
cp -r "$FORMATION/labs/lab-01-git-github/solution/.claude" ~/lab-ecommerce/
cp "$FORMATION/labs/lab-01-git-github/solution/src/ECommerce.Ordering.Api/Endpoints/OrderingEndpoints.cs" \
   ~/lab-ecommerce/src/ECommerce.Ordering.Api/Endpoints/
```
