# Module 02 — Contexte & mémoire

> **Durée :** 40 min · **Pré-requis :** [Module 01](../01-commandes-natives/)
> · **Suivant :** [Module 03 — Commandes personnalisées](../03-commandes-personnalisees/)

---

## 1. La limite — d'où l'on vient

Les commandes natives cadrent **une** session. Mais à chaque `/clear`, à chaque nouvelle session,
l'agent repart sans rien savoir de votre projet :

| Il fait… | …alors que l'équipe… | Coût |
|---|---|---|
| `new HttpClient { BaseAddress = new Uri("http://localhost:5147") }` | résout les services par nom (`https+http://catalog`) | Code qui marche en local, casse en conteneur |
| `dotnet build` à la racine | build `ECommerce.slnx` (la solution contient aussi les tests) | Des projets oubliés, un CI différent du poste |
| une branche `feature-pagination` | nomme `feat/`, `fix/`, `chore/` | Des PR refusées par la forge |
| `_logger.LogInformation("Commande de {Customer}", order.Customer)` | interdit les données client dans les logs (RGPD) | Une fuite de données personnelles vers la télémétrie |

Il n'a pas *oublié* : il ne l'a **jamais su**.

## 2. Le concept — trois horizons de mémoire

```
┌─ Fenêtre de contexte ──────────────────── la session en cours, volatile ──┐
│  conversation, fichiers lus, sorties de commandes                         │
│  → se remplit (/context), se résume (/compact), se vide (/clear)          │
└───────────────────────────────────────────────────────────────────────────┘
┌─ Mémoire projet ─────────────── ./CLAUDE.md — versionné, partagé, durable ─┐
│  stack, commandes, conventions, interdits                                 │
│  → relu à CHAQUE session, par TOUTE l'équipe                              │
└───────────────────────────────────────────────────────────────────────────┘
┌─ Mémoire personnelle ─────────── ~/.claude/CLAUDE.md — vous seul, partout ─┐
│  préférences : langue des réponses, niveau de détail, outils favoris       │
└───────────────────────────────────────────────────────────────────────────┘
```

**La distinction qui compte :** la fenêtre de contexte est une *mémoire de travail* qui
s'efface ; `CLAUDE.md` est une *procédure* qui reste. Tout ce que vous répétez à l'agent plus
d'une fois doit migrer de la première vers la seconde.

| | Commandes natives (module 01) | **`CLAUDE.md`** |
|---|---|---|
| Portée | Une session | Toutes les sessions, toute l'équipe |
| Nature | Une action sur le harnais | Une connaissance donnée au modèle |
| Garantie | Déterministe | **Non garantie** : le modèle la lit, il peut s'en écarter |

Ce dernier point préparera le module 04 : `CLAUDE.md` *informe*, il n'*impose* pas.

## 3. Anatomie

### 3.1 Le fichier `CLAUDE.md`

Généré par `/init`, puis **édité à la main** — c'est là qu'est la valeur. Pour l'ecommerce-app :

````markdown
# ecommerce-app

## Stack
.NET 10 / ASP.NET Core, orchestré par .NET Aspire (AppHost).
Catalog.Api et Ordering.Api (minimal APIs + EF Core), Gateway (YARP), Web (Blazor Server).
Ordering appelle Catalog en HTTP pour valider chaque produit.

## Commandes
```bash
export PATH="/usr/local/share/dotnet:$PATH"
dotnet build ECommerce.slnx               # toujours la solution, jamais un projet seul
dotnet test ECommerce.slnx
dotnet run --project src/ECommerce.AppHost # dashboard Aspire (URL + jeton en console)
```

## Conventions
- Les services s'appellent par nom (https+http://catalog) : JAMAIS d'URL en dur.
- Branches : feat/, fix/, chore/, test/, ci/ — jamais de travail direct sur main.
- Commits : Conventional Commits, en anglais, à l'impératif.
- Un endpoint = un test d'intégration WebApplicationFactory dans tests/.

## Interdits
- Aucune donnée client (nom, e-mail) dans un log, une trace ou une exception.
- Aucun secret dans le code ou appsettings.json : dotnet user-secrets ou variable d'environnement.
- Ne jamais modifier un test pour faire passer un build : corriger le code.
- Ne jamais modifier une migration EF Core déjà committée : en ajouter une nouvelle.
````

**Ce qui distingue un `CLAUDE.md` utile d'un inutile :**

| ✅ Utile | ❌ Inutile |
|---|---|
| « `dotnet build ECommerce.slnx` (pas `dotnet build`) » | « Utilise les bonnes pratiques » |
| « Jamais d'URL de service en dur : service discovery » | « Écris du code propre » |
| « Aucun nom de client dans les logs » | « Fais attention à la sécurité » |
| Une contrainte **vérifiable** | Une intention **non mesurable** |

Règle : si vous ne pouvez pas dire objectivement si la règle a été respectée, elle n'a rien à
faire dans le fichier. Visez **40 à 120 lignes** : chaque ligne est payée à chaque session.

### 3.2 Plusieurs `CLAUDE.md`

| Emplacement | Chargé | Exemple |
|---|---|---|
| `~/.claude/CLAUDE.md` | Toujours, pour vous | « Réponds en français, code en anglais. » |
| `./CLAUDE.md` | Toujours, pour le projet | Le fichier ci-dessus |
| `src/ECommerce.Web/CLAUDE.md` | Quand l'agent travaille dans ce dossier | Les conventions Blazor et d'accessibilité |

Un `CLAUDE.md` peut aussi en importer un autre : `@docs/conventions-api.md`. Utile pour garder le
fichier principal court.

### 3.3 Les trois préfixes

| Préfixe | Ce qu'il fait | Exemple |
|:---:|---|---|
| `@` | Injecte un fichier ou un dossier dans le contexte | `Explique @src/ECommerce.Ordering.Api/Services/CatalogServiceClient.cs` |
| `!` | Exécute une commande ; sa **sortie** entre en contexte | `!dotnet test ECommerce.slnx` |
| `#` | Ajoute une note **durable** dans `CLAUDE.md` | `# un endpoint ajouté = un test d'intégration ajouté` |

`#` est le geste de capitalisation le plus rentable de la formation : une correction faite une
fois est inscrite pour toute l'équipe.

### 3.4 Gérer la fenêtre

| Situation | Commande |
|---|---|
| Le contexte se remplit, la tâche continue | `/compact` (vous pouvez préciser quoi garder : `/compact garde la liste des fichiers modifiés`) |
| Nouveau sujet | `/clear` — `CLAUDE.md` reste chargé |
| Comprendre ce qui occupe la place | `/context` |

---

## 4. Mini-lab — donner une mémoire au projet (20 min)

```bash
cd ~/lab-ecommerce
claude
```

**1. Constater l'amnésie**

```text
> Je veux ajouter un appel de Ordering vers un nouveau service de stock. Comment je configure
  l'adresse du service ? Et comment je nomme ma branche ?
```

Réponse générique : une URL de configuration, une branche quelconque.

**2. Générer la base**

```text
> /init
```

**3. L'enrichir là où c'est utile.** Ouvrez `CLAUDE.md` et ajoutez les sections `## Conventions`
et `## Interdits` de l'exemple. Retirez ce que `/init` a écrit de vague.

**4. Vérifier que ça mord**

```text
> /clear
> Je veux ajouter un appel de Ordering vers un nouveau service de stock. Comment je configure
  l'adresse du service ? Et comment je nomme ma branche ?
```

Il doit répondre service discovery (`https+http://stock` déclaré dans l'AppHost) et `feat/...`.
**Même question qu'à l'étape 1, réponse d'équipe.**

**5. Capitaliser à la volée**

```text
> # toute nouvelle route d'API est déclarée aussi dans le Gateway (appsettings.json, ReverseProxy)
```

Relisez `CLAUDE.md` : la règle y est.

**6. Un `CLAUDE.md` de sous-dossier**

```text
> Crée src/ECommerce.Web/CLAUDE.md avec trois règles front : aucune information portée par
  la couleur seule, chaque bouton a un nom accessible, pas de nouvelle dépendance front sans
  accord.
```

**7. Mesurer le coût**

```text
> /context
```

Regardez la part prise par la mémoire. C'est le prix de chaque ligne, à chaque session.

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| `CLAUDE.md` de 600 lignes | Contexte mangé avant d'avoir commencé | 40–120 lignes factuelles, le reste en import ou en skill |
| Des vœux pieux (« code propre ») | Aucun effet observable | Des règles vérifiables |
| Ne pas le versionner | Chacun ses règles, l'équipe diverge | `git add CLAUDE.md` |
| Y mettre un secret ou une URL interne | Fuite dans un dépôt partagé | Variables d'environnement |
| Ne jamais le relire après `/init` | Il décrit un dépôt qui a changé | Le maintenir comme du code |
| Compter sur `CLAUDE.md` pour une règle critique | Le modèle peut s'en écarter | Module 04 : un hook |

---

## 6. Checklist de sortie

- [ ] Je distingue fenêtre de contexte, mémoire projet et mémoire personnelle.
- [ ] Mon `CLAUDE.md` contient des commandes, des conventions et des interdits **vérifiables**.
- [ ] J'ai utilisé `@`, `!` et `#` au moins une fois chacun.
- [ ] J'ai créé un `CLAUDE.md` de sous-dossier et je sais quand il est chargé.
- [ ] Je sais dire pourquoi `CLAUDE.md` *informe* sans *garantir*.

---

## 7. La limite suivante

L'agent connaît maintenant vos règles. Mais avant chaque PR, vous retapez le même prompt de vingt
lignes : « relis le diff, vérifie les contrats d'API, les tests, les secrets, les migrations,
rends-moi un tableau… ». Chaque développeur a sa variante, et aucune n'est versionnée.

> **→ [Module 03 — Commandes personnalisées](../03-commandes-personnalisees/) :** transformer un
> prompt d'équipe en fichier versionné, rejouable par `/nom`.
