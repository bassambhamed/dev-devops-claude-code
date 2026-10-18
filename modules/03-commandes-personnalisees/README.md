# Module 03 — Commandes personnalisées

> **Durée :** 30 min · **Pré-requis :** [Module 02](../02-contexte-et-memoire/)
> · **Suivant :** [Lab 01 — Git & GitHub](../../labs/lab-01-git-github/), puis
> [Module 04 — Hooks](../04-hooks/)

---

## 1. La limite — d'où l'on vient

`CLAUDE.md` donne à l'agent ce qu'il doit **savoir**. Il ne dit pas ce qu'il doit **faire** quand
vous le lui demandez. Résultat : les mêmes prompts longs, retapés chaque jour, chacun sa variante.

| Prompt retapé | Qui | Fréquence |
|---|---|---|
| « Relis le diff : contrats d'API, tests, secrets, migrations, URL en dur. Rends un tableau. » | Dev | Avant chaque PR |
| « Prépare la livraison : tests, message de commit conventionnel, PR documentée. Attends mon accord. » | Dev & DevOps | Plusieurs fois par jour |
| « Explique-moi ce service à moi qui arrive : rôle, dépendances, points d'entrée, pièges. » | Nouvel arrivant | À chaque intégration |

## 2. Le concept — un prompt devient un fichier

Une commande personnalisée, c'est **un fichier Markdown dont le contenu est envoyé comme prompt**.
Le nom du fichier devient le nom de la commande.

```
.claude/commands/review-diff.md      →      /review-diff
```

C'est la brique la plus simple du parcours, et c'est volontaire : on capitalise un **prompt**
avant d'apprendre à imposer une **règle** (hooks) puis à capitaliser une **procédure** (skills).

| | `CLAUDE.md` (module 02) | **Commande personnalisée** |
|---|---|---|
| Contenu | Ce que l'agent doit savoir | Ce que l'agent doit faire, quand vous le demandez |
| Chargement | À chaque session, toujours | Seulement quand vous tapez `/nom` |
| Coût en contexte | Permanent | Nul tant qu'elle n'est pas appelée |

> **Bon à savoir.** Depuis Claude Code 2.1, les commandes et les skills ont fusionné : un fichier
> `.claude/commands/ship.md` et un dossier `.claude/skills/ship/SKILL.md` créent tous deux `/ship`.
> La commande reste la forme la plus simple — un fichier, un prompt, déclenché par vous. Le
> [module 05](../05-skills/) montre quand il faut passer à la forme complète.

## 3. Anatomie

### 3.1 Le fichier minimal

`.claude/commands/review-diff.md` :

```markdown
---
description: Relit le diff courant selon la checklist de revue de l'équipe, sans rien modifier
---

Relis les changements de la branche courante par rapport à main. Pour chaque fichier modifié :

1. Correction — le code fait-il ce que les commits annoncent ? Cas d'erreur traités ?
2. Contrats — une route, un DTO ou un champ JSON a-t-il changé ? Qui le consomme ?
3. Tests — chaque comportement modifié a-t-il un test ?
4. Conventions — URL en dur ? secret ? donnée client dans un log ?
5. Base — une migration est-elle présente ? destructive ?

Rends un tableau Fichier | Constat | Gravité | Proposition, puis un verdict en une ligne.
Lecture seule : ne modifie aucun fichier.
```

### 3.2 Les trois mécanismes qui en font plus qu'un copier-coller

| Mécanisme | Syntaxe | Effet |
|---|---|---|
| **Arguments** | `$ARGUMENTS`, ou `$0`, `$1`… par position | Ce que l'utilisateur tape après la commande |
| **Injection de sortie shell** | `` !`git diff --stat main...HEAD` `` | La commande est exécutée **avant** l'envoi ; sa sortie remplace le texte |
| **Pré-autorisation** | `allowed-tools: Bash(git diff:*)` dans le frontmatter | Les outils nécessaires ne demandent pas de permission pendant ce tour |

`.claude/commands/explain-service.md` :

```markdown
---
description: Explique un service de l'ecommerce-app à un nouvel arrivant
argument-hint: <catalog|ordering|gateway|web>
allowed-tools: Bash(git log:*)
---

Explique le service $ARGUMENTS à un développeur qui arrive dans l'équipe.

Historique récent du service :
!`git log --oneline -10 -- src/`

Couvre : son rôle, ses endpoints, qui l'appelle et qui il appelle (service discovery),
sa persistance, sa configuration, et les trois pièges à connaître. Cite fichiers et lignes.
```

Invocation : `/explain-service ordering`.

### 3.3 Où les placer

| Emplacement | Portée | Versionné ? |
|---|---|---|
| `.claude/commands/<nom>.md` | Le projet, **toute l'équipe** | Oui — c'est le but |
| `~/.claude/commands/<nom>.md` | Vous, sur tous vos projets | Non |
| Dans un plugin ([module 06](../06-plugins/)) | Toute personne qui installe le plugin, sous `/plugin:nom` | Oui |

Des sous-dossiers créent des espaces de noms : `.claude/commands/db/explain.md` → `/db:explain`.

---

## 4. Mini-lab — vos premières commandes (15 min)

```bash
cd ~/lab-ecommerce
mkdir -p .claude/commands
claude
```

**1. Faire écrire `/review-diff`** — dans l'esprit de la formation, l'agent écrit ses propres outils :

```text
> Crée .claude/commands/review-diff.md : une commande en lecture seule qui relit le diff
  courant contre main selon cinq axes (correction, contrats d'API, tests, conventions,
  migrations) et rend un tableau Fichier | Constat | Gravité | Proposition.
  Utilise l'injection !`git diff --stat main...HEAD` et pré-autorise Bash(git diff:*).
```

**2. Vérifier qu'elle est vue**

```text
> /help
```

**3. Créer `/explain-service`** avec un argument (exemple §3.2), puis :

```text
> /explain-service gateway
```

**4. Préparer `/ship`** — la commande de livraison que le [Lab 01](../../labs/lab-01-git-github/)
utilisera. Partez du modèle de [`plugins/oddo-dev-toolkit/commands/ship.md`](../../plugins/oddo-dev-toolkit/commands/ship.md)
et adaptez-le.

**5. Versionner** (si Git est initialisé — sinon ce sera fait au Lab 01)

```bash
git add .claude/commands/ && git commit -m "chore: add team commands"
```

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| Pas de `description` | Commande illisible dans `/help` | Toujours une ligne de description |
| Un prompt vague (« vérifie que tout va bien ») | Résultat différent à chaque fois | Étapes numérotées et format de sortie imposé |
| Oublier « lecture seule » sur une commande de revue | Une revue qui *corrige* | L'écrire explicitement |
| L'injection `!` d'une commande qui peut échouer | Toute l'invocation est annulée | Prévoir un repli : `` !`git diff --stat main...HEAD \|\| git diff --stat` `` |
| La mettre dans `~/.claude/` | L'équipe ne l'a pas | `.claude/commands/`, versionné |
| Une commande qui fait douze choses | Impossible à maintenir | En faire un skill (module 05) |

---

## 6. Checklist de sortie

- [ ] J'ai créé `/review-diff` et `/explain-service` dans `.claude/commands/`.
- [ ] Je sais utiliser `$ARGUMENTS`, l'injection `` !`…` `` et `allowed-tools`.
- [ ] Je sais dire ce qui distingue une commande de `CLAUDE.md`.
- [ ] Mes commandes de revue sont explicitement en lecture seule.

---

## 7. La limite suivante

Le [Lab 01](../../labs/lab-01-git-github/) va mettre `/ship` à l'épreuve sur un vrai workflow Git.
Vous y constaterez sa limite : `/ship` **dit** « ne committe pas de secret ». Mais le modèle peut
mal juger une ligne ; un collègue peut committer sans passer par `/ship` ; et le formatage n'est
appliqué que quand quelqu'un y pense. Une commande est une **consigne que vous déclenchez**, pas
un **contrôle qui s'applique tout seul**.

> **→ [Lab 01](../../labs/lab-01-git-github/)**, puis **[Module 04 — Hooks](../04-hooks/)** : les
> règles qui s'exécutent à chaque fois, quel que soit le prompt et quel que soit le développeur.
