# Module 05 — Skills

> **Durée :** 45 min · **Pré-requis :** [Module 04](../04-hooks/)
> · **Suivant :** [Lab 02 — Tests](../../labs/lab-02-tests/), puis [Module 06 — Plugins](../06-plugins/)

---

## 1. La limite — d'où l'on vient

Les hooks du module 04 savent **dire non** (un secret, une commande destructive) et **corriger la
forme** (le formatage). Ils ne savent pas **faire** un travail qui demande du jugement.

| Demande | Ce qu'elle implique réellement | Pourquoi ni un hook ni une commande ne suffisent |
|---|---|---|
| **Dev** — « Ajoute un SKU unique aux produits » | Modèle, `OnModelCreating`, `migrations add`, relecture du **SQL**, seed, tests Testcontainers | Huit étapes avec des décisions ; une checklist de revue ; vous voulez qu'il s'en serve **sans y penser** |
| **Dev** — « Ce calcul de total n'est pas testé » | Choisir le bon niveau de test, faux service HTTP, cas limites | Une doctrine d'équipe de deux pages, que l'agent doit appliquer seul |
| **DevOps** — « Conteneurise Gateway » | Multi-stage, non-root, `.dockerignore`, vérification UID, scan | Une procédure avec ses pièges connus (image chiselée sans `id`, contexte de build) |

Une commande de 80 lignes pourrait contenir tout ça. Mais vous devez penser à l'appeler, elle
occupe tout le contexte à chaque appel, et elle ne peut pas embarquer de fichiers d'appui.

## 2. Le concept — un savoir-faire que l'agent mobilise seul

Un **skill** est un **dossier** contenant un `SKILL.md` — une procédure écrite en langage
naturel — et, si besoin, des fichiers d'appui. L'agent le charge **de lui-même** quand votre
demande correspond à sa `description`. Vous pouvez aussi l'appeler par `/nom`.

```
.claude/skills/ef-migration/
├── SKILL.md              ← frontmatter (le déclencheur) + la procédure
└── checklist-revue.md    ← fichier d'appui, lu SEULEMENT quand la procédure en a besoin
```

**La bascule mentale :** la `description` n'est pas de la documentation, c'est le **critère de
déclenchement**. Une description vague = un skill qui ne sert jamais.

### Commande, skill, hook : la frontière

Depuis Claude Code 2.1, **commandes et skills ont fusionné** : `.claude/commands/ship.md` et
`.claude/skills/ship/SKILL.md` créent tous deux `/ship`. Ce qui les distingue n'est plus le
mécanisme, mais **ce dont le besoin a besoin** :

| | Commande (module 03) | **Skill** | Hook (module 04) |
|---|---|---|---|
| Qui déclenche | Vous (`/nom`) | **L'agent**, selon la description — et vous si vous voulez | Le harnais, sur événement |
| Forme | Un fichier | **Un dossier** : procédure + fichiers d'appui + scripts | Un script |
| Coût en contexte | Tout le prompt, à l'appel | **Seule la description en permanence** ; le reste à l'usage | Aucun |
| Nature | Un raccourci | **Un savoir-faire avec du jugement** | Une garantie sans jugement |
| Analogie | Un alias shell | **Un runbook** | Une règle de pare-feu |

### La divulgation progressive

```
toujours en contexte   →  name + description           (~80 tokens)
à l'usage              →  le corps de SKILL.md          (quelques centaines)
si la procédure le dit →  checklist-revue.md, doctrine.md…
exécuté, jamais lu     →  scripts/*.sh
```

C'est pour cela qu'une équipe peut avoir vingt skills sans saturer le contexte — et pas vingt
pages dans `CLAUDE.md`.

## 3. Anatomie

### 3.1 Le `SKILL.md`

Extrait de [`ef-migration`](../../plugins/oddo-dev-toolkit/skills/ef-migration/SKILL.md) :

```markdown
---
name: ef-migration
description: Fait évoluer le schéma PostgreSQL de l'ecommerce-app avec EF Core — modifier les
  entités et le DbContext, générer la migration avec dotnet ef, relire le SQL produit,
  l'appliquer en local et vérifier dans la base. À utiliser pour ajouter une table, une colonne,
  un index, une contrainte ou des données de seed. N'applique jamais une migration hors du poste
  local et ne réécrit jamais une migration déjà committée.
---

# Skill : ef-migration

## Procédure
1. Modéliser — entités et OnModelCreating : longueurs, index, CHECK, Restrict par défaut.
2. Compiler.
3. Générer — dotnet ef migrations add <NomExplicite>.
4. Relire le SQL, pas le C# — dotnet ef migrations script … ; dérouler checklist-revue.md.
5. Appliquer en local, vérifier dans la base, lancer les tests.

## Garde-fous
- Une migration committée est immuable : on en ajoute une nouvelle.
- Toute opération destructive est signalée en tête de réponse.
```

### 3.2 Les quatre règles d'un bon skill

1. **Une `description` qui dit *quand*, avec les mots des utilisateurs.** « …ajouter une colonne,
   un index, une contrainte… » se déclenche ; « Gère la base » ne se déclenche jamais.
2. **Des étapes ordonnées et vérifiables**, comme un runbook.
3. **Une section Garde-fous** : ce que le skill ne doit jamais faire.
4. **Un format de sortie** : sinon le rendu varie à chaque exécution.

### 3.3 Contrôler qui déclenche

| Frontmatter | Qui peut le déclencher | Exemple |
|---|---|---|
| *(par défaut)* | L'agent **et** vous | `gen-tests`, `ef-migration` |
| `disable-model-invocation: true` | **Vous seulement** | `init-repo`, `deploy` : un effet de bord qu'on ne laisse pas l'agent décider |
| `user-invocable: false` | **L'agent seulement** (absent du menu `/`) | `conventions-api` : un savoir de fond, pas une action |

### 3.4 Les autres champs utiles

| Champ | Effet | Exemple |
|---|---|---|
| `allowed-tools` | Outils autorisés sans demande **pendant ce tour** | `Bash(dotnet ef migrations script:*)` |
| `argument-hint` | Aide à la saisie dans le menu `/` | `[NomDeLaMigration]` |
| `paths` | Ne se charge automatiquement que pour ces fichiers | `src/ECommerce.Web/**/*.razor` |
| `context: fork` | S'exécute dans un **sous-agent**, contexte séparé | Annonce du [module 07](../07-sous-agents/) |
| `hooks` | Hooks actifs une fois le skill invoqué | Un formatage spécifique |

Et dans le corps : `$ARGUMENTS` et l'injection `` !`commande` ``, comme pour les commandes.

### 3.5 Portée

| Emplacement | Disponible |
|---|---|
| `.claude/skills/<nom>/SKILL.md` | Ce projet, toute l'équipe (versionné) |
| `~/.claude/skills/<nom>/SKILL.md` | Vous, partout — **prioritaire** sur un skill projet de même nom |
| Dans un plugin ([module 06](../06-plugins/)) | Sous `/<plugin>:<nom>` — jamais de conflit de nom |

`/skills` liste ce qui est réellement chargé, avec l'origine de chaque skill.

---

## 4. Mini-lab — deux skills, deux modes de déclenchement (25 min)

```bash
cd ~/lab-ecommerce
claude
```

### Partie A — un skill que l'agent mobilise seul : `gen-tests` (15 min)

**1. Le faire écrire**, avec un fichier d'appui :

```text
> Crée le skill .claude/skills/gen-tests/ :
  - SKILL.md : écrire des tests d'intégration pour l'ecommerce-app. Description qui dit QUAND
    l'utiliser (ajouter des tests, tester un endpoint, couvrir un cas d'erreur, reproduire un bug).
    Procédure : comprendre avant d'écrire, choisir le niveau, un test = un comportement, exécuter.
    Garde-fous : ne jamais modifier un test pour le faire passer, données fictives.
  - doctrine.md : quel outil pour quel besoin (WebApplicationFactory, faux HttpMessageHandler,
    Testcontainers), et les pièges connus (Program interne, provider in-memory).
  SKILL.md renvoie vers doctrine.md au lieu de tout recopier.
```

Comparez avec la [référence](../../plugins/oddo-dev-toolkit/skills/gen-tests/).

**2. Vérifier le chargement**

```text
> /skills
```

**3. Le déclencher sans le nommer** — le test qui compte :

```text
> Le calcul du total d'une commande n'est couvert par aucun test. Corrige ça.
```

Il doit mobiliser `gen-tests` et, au passage, lire `doctrine.md` pour choisir un faux service
Catalog. (Le [Lab 02](../../labs/lab-02-tests/) va plus loin sur ce point.)

**4. Mesurer le rôle de la description.** Remplacez-la par « Aide pour les tests. », relancez une
session, reposez la question : il ne se déclenche plus, ou au hasard. **Remettez l'originale.**

### Partie B — une commande qui devient un skill que *vous seul* déclenchez (10 min)

Au Lab 01, la commande `/init-repo` a grossi : vérifications préalables, création du dépôt distant,
liste des fichiers à ne jamais indexer. Transformez-la :

```text
> Transforme .claude/commands/init-repo.md en skill .claude/skills/init-repo/ :
  - SKILL.md avec disable-model-invocation: true (créer un dépôt distant est un effet de bord :
    c'est moi qui décide quand) ;
  - un fichier d'appui fichiers-interdits.md listant ce qu'on n'indexe jamais ;
  puis supprime l'ancienne commande.
```

Vérifiez : `/init-repo` est toujours dans le menu, mais demander « initialise le dépôt » sans le
nommer **ne le déclenche plus**. C'est exactement le comportement voulu.

**5. Versionner**

```bash
git add .claude/skills/ && git commit -m "chore: add gen-tests and init-repo skills"
```

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| Description vague | Le skill ne se déclenche jamais | Décrire **les situations**, avec les mots des utilisateurs |
| Frontmatter YAML invalide | Skill absent de `/skills` | Vérifier `name` et `description` |
| Tout mettre dans `SKILL.md` | 600 lignes chargées à chaque usage | Fichiers d'appui, référencés depuis la procédure |
| Aucune section Garde-fous | Le skill agit là où il devrait s'arrêter | Lister les interdits |
| Laisser l'agent déclencher un skill à effet de bord | Un dépôt créé, un déploiement lancé « parce que ça semblait pertinent » | `disable-model-invocation: true` |
| Mettre une règle critique dans un skill | Le skill n'est pas garanti | Une règle qui doit tenir = un hook |

---

## 6. Checklist de sortie

- [ ] J'ai écrit un skill complet : description, procédure, garde-fous, fichier d'appui.
- [ ] Il se déclenche **sans que je le nomme**, et j'ai vérifié le rôle de la description.
- [ ] J'ai transformé une commande en skill réservé à l'humain (`disable-model-invocation`).
- [ ] Je sais dire, pour un besoin donné, s'il relève d'une commande, d'un skill ou d'un hook.
- [ ] Mes skills sont versionnés.

---

## 7. La limite suivante

Le [Lab 02](../../labs/lab-02-tests/) va mettre `gen-tests` et deux nouveaux hooks au travail.
À la fin, votre `.claude/` contiendra trois commandes, quatre hooks, deux skills. Deux problèmes
apparaîtront :

1. **Douze collègues, huit dépôts** : chacun devrait recopier ces fichiers à la main, et les
   tenir à jour.
2. **Réinventer la roue** : votre hook `Stop` vous apprend une erreur de type en fin de tâche,
   après un `dotnet test` complet. N'existe-t-il pas déjà mieux — le retour du compilateur juste
   après chaque édition, maintenu par d'autres ?

> **→ [Lab 02](../../labs/lab-02-tests/)**, puis **[Module 06 — Plugins](../06-plugins/)** :
> consommer ce qui existe, packager ce qui vous est propre, et le distribuer en une commande.
