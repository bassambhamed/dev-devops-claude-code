# Lab 05 — Améliorer le frontend

> **Durée :** 75 min · **Modules requis :** [04](../../modules/04-hooks/) → [08](../../modules/08-mcp/)
> · **Outils :** `dotnet`, Chrome ou Edge + extension *Claude in Chrome* · **Corrigé :** [`solution/`](solution/) (vérifié)

---

## 1. Objectif

Moderniser l'interface Blazor (`ECommerce.Web`) **sans toucher aux règles métier** :

1. la page catalogue : **filtre par catégorie** et **recherche** (le backend du [Lab 04](../lab-04-postgresql/)),
   états de **chargement / vide / erreur**, **responsive**, **accessibilité** ;
2. une page **santé des services** pour l'exploitation ;
3. une vérification **dans le navigateur**, pas seulement dans le code.

## 2. Pré-requis

- [Lab 04](../lab-04-postgresql/) terminé (endpoints `/api/categories` et filtres). Sans lui,
  sautez l'étape 4 : le reste du lab fonctionne.
- Extension *Claude in Chrome* installée et connectée au **même** compte que Claude Code
  (`/chrome` doit afficher *Status: Enabled*).

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **Plugin officiel** `frontend-design` | Proposer une direction visuelle | Un savoir-faire générique, maintenu par Anthropic : on ne le réécrit pas |
| **Skill** `ui-modernize` | La doctrine de l'équipe : Bootstrap, états, a11y, logique métier intacte | Les conventions **de la maison** — ce qu'aucun plugin public ne connaît |
| **Hook** `build-web-on-edit` | Compiler le front après chaque édition `.razor` | `csharp-lsp` ne couvre que les `.cs` ; une erreur Razor ne se voit qu'au build |
| **MCP intégré** `claude-in-chrome` | Ouvrir la page, 375 px, console, clavier, GIF | Le rendu réel n'est pas dans le code source |
| **Sous-agent** `a11y-reviewer` | Audit d'accessibilité indépendant, en lecture seule | Celui qui a écrit la page n'est pas le mieux placé pour l'auditer |

---

## 4. Déroulé pas-à-pas

### Étape 1 — L'état des lieux, dans le navigateur (10 min)

Terminal 1 : `cd ~/lab-ecommerce && dotnet run --project src/ECommerce.AppHost`

Terminal 2 :

```bash
cd ~/lab-ecommerce && git switch -c feat/ui-catalog && claude --chrome
```
```text
> Ouvre la page /products de l'application web (URL de la ressource « web » : http://localhost:5190).
  À 1280 px puis à 375 px de large : qu'est-ce qui déborde ? Lis la console. Navigue au clavier
  jusqu'au bouton « Place order » : le focus est-il visible ? Les boutons « Add » sont-ils
  distinguables pour un lecteur d'écran ? Rends un tableau des manques.
```

Constats attendus : tableau qui déborde sur mobile, « Loading… » en texte brut, une erreur
réseau indiscernable d'un catalogue vide, dix boutons qui s'appellent tous « Add », un label
« Customer name » non relié à son champ, un stock sans statut.

### Étape 2 — Le hook qui compile le front (5 min)

```bash
mkdir -p .claude/hooks
cp "$FORMATION/labs/lab-05-frontend/solution/.claude/hooks/build-web-on-edit.sh" .claude/hooks/
chmod +x .claude/hooks/build-web-on-edit.sh
```

Ajoutez-le en `PostToolUse` (matcher `Write|Edit|MultiEdit`, voir
[`solution/.claude/settings.json`](solution/.claude/settings.json)). Lisez-le : il ne s'exécute
que pour `src/ECommerce.Web/`, et renvoie à l'agent les seules lignes d'erreur.

> **Pourquoi ce hook existe.** En écrivant ce corrigé, une page `Health.razor` qui injectait un
> service sous le nom `Health` a produit l'erreur `CS0542` — un membre ne peut pas porter le nom
> de son composant. Le serveur de langage ne la voit pas (il ne lit pas les `.razor`), et le
> hook `Stop` ne la signalerait qu'en fin de tâche. Ce hook la remonte à l'édition même.

### Étape 3 — Une direction visuelle, puis la doctrine (10 min)

```text
> /plugin install frontend-design@claude-plugins-official
```

```text
> En t'appuyant sur frontend-design, propose une maquette HTML statique de la page catalogue
  (filtres, cartes ou tableau, badges de stock, états chargement / vide / erreur), dans
  l'esprit Bootstrap déjà utilisé. Ne touche pas encore au code Blazor.
```

Comparez avec la [maquette de référence](solution/mockup/catalog-mockup.html). Décidez de la
direction **avant** de coder. Le skill d'équipe `ui-modernize` (plugin `oddo-dev-toolkit`)
encadre ensuite l'implémentation : Bootstrap seulement, aucune nouvelle dépendance, logique
métier intacte.

### Étape 4 — Filtres et états (20 min)

```text
> Applique la direction retenue à Products.razor :
  - un filtre par catégorie (GET /catalog/api/categories) et une recherche par nom, branchés sur
    les paramètres categoryId et search de l'API ;
  - un skeleton au chargement, un message si aucun résultat, une alerte avec bouton Retry si
    l'appel échoue ;
  - le tableau en table-responsive ; le stock en badge COULEUR + TEXTE ;
  - chaque bouton Add avec un aria-label unique, le label Customer name relié à son champ.
  Ne modifie PAS la logique du panier ni du passage de commande.
```

Le skill `ui-modernize` doit se déclencher ; le hook compile après chaque édition. Vérifiez le
diff vous-même : `git diff src/ECommerce.Web` — le bloc `PlaceOrder` doit être inchangé.

### Étape 5 — La page santé (10 min)

```text
> Crée une page /health-dashboard qui affiche l'état de Gateway, Catalog et Ordering en
  appelant leurs /health à travers la gateway, avec un rafraîchissement toutes les 10 s, des
  badges couleur + texte, et un lien dans le menu.
```

Si l'agent nomme le composant `Health.razor` et injecte le client sous le nom `Health`, vous
verrez le hook de l'étape 2 en action.

> `/health` n'est exposé qu'en **Development** (`MapDefaultEndpoints`). En production, un
> tableau de bord de santé s'appuie sur la supervision (Lab 10), pas sur ces endpoints.

### Étape 6 — Vérifier dans le navigateur (10 min)

Relancez l'AppHost, puis :

```text
> Dans Chrome : ouvre /products à 375 px. Filtre sur « Displays », cherche « mouse ». Vérifie
  qu'aucune erreur n'apparaît dans la console. Navigue au clavier jusqu'à « Place order ».
  Enregistre un GIF du parcours : ajouter deux produits, saisir un nom, passer commande.
  Puis ouvre /health-dashboard.
```

Pour vérifier l'état d'erreur, arrêtez la ressource `catalog` depuis le dashboard Aspire, puis
rechargez `/products` : l'alerte *Retry* doit apparaître — pas « aucun produit ».

> **Cadre bancaire.** Le GIF capture tout ce qui est visible : ici, uniquement `localhost` et des
> données fictives. Relisez toute capture avant de la partager.

### Étape 7 — L'audit indépendant (10 min)

```text
> Fais auditer Products.razor et HealthDashboard.razor par a11y-reviewer.
```

Le sous-agent rend un tableau critère WCAG / ligne / correction, et une liste de points à vérifier
dans le navigateur. Faites corriger, puis :

```text
> /review-diff
> /ship modernisation de la page catalogue et page de santé
```

---

## 5. Livrable

```
src/ECommerce.Web/
├── Services/CatalogApiClient.cs          # catégories + filtres
├── Services/HealthApiClient.cs           # sondes /health via la gateway
├── Components/Pages/Products.razor       # filtres, états, a11y, responsive — panier inchangé
├── Components/Pages/HealthDashboard.razor
├── Components/Layout/NavMenu.razor       # lien Health
└── Program.cs                            # enregistrement de HealthApiClient
.claude/hooks/build-web-on-edit.sh        # + câblage PostToolUse
```

## 6. Garde-fous

| Règle | Mécanisme | Garantie |
|---|---|---|
| Le comportement métier ne change pas | Doctrine `ui-modernize` + vérification du diff | Consigne + revue |
| Le front compile après chaque édition | Hook `build-web-on-edit` | Contrôle |
| Aucune information par la couleur seule | Checklist a11y + `a11y-reviewer` | Consigne + regard indépendant |
| Le navigateur n'agit que sur `localhost` | Permissions par site de l'extension | Contrôle (côté extension) |
| Aucune donnée réelle dans les captures | Application à données fictives | Consigne |

## 7. Pour aller plus loin

- Installez le plugin `playwright` et faites écrire un test de bout en bout du parcours de
  commande, rejouable en CI (contrairement à Claude in Chrome, qui pilote **votre** navigateur).
- Ajoutez un `CLAUDE.md` dans `src/ECommerce.Web/` avec les règles front (module 02).
- Faites mesurer les contrastes réels dans le navigateur et corrigez ceux sous 4,5:1.

## 8. La limite révélée

Le code, la base et l'interface avancent. Mais tout repose sur **vous** : vous lancez les tests,
vous relisez le SQL des migrations, vous ouvrez les PR. Une PR ouverte à 23 h attend le matin.

> **→ [Annexe — l'agent sans terminal](../../modules/annexe-agent-sans-terminal/)** (pas une
> nouvelle brique : les mêmes, lancées en headless), puis [Lab 06 — CI/CD](../lab-06-ci-cd/).

## Corrigé

```bash
S="$FORMATION/labs/lab-05-frontend/solution"
cp -r "$S/src/ECommerce.Web/"* ~/lab-ecommerce/src/ECommerce.Web/
cp "$S/.claude/hooks/build-web-on-edit.sh" ~/lab-ecommerce/.claude/hooks/
```

Vérifications faites : build sans erreur ; application lancée avec PostgreSQL ; page `/products`
rendue avec filtres, badges « N in stock » et `aria-label` uniques ; `/health-dashboard`
affichant trois services *Healthy* ; hook testé sur un cas sain, sur l'erreur `CS0542`, et sur un
fichier hors du front.
