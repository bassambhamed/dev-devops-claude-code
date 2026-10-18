# Module 07 — Sous-agents

> **Durée :** 45 min · **Pré-requis :** [Module 06](../06-plugins/) et [Lab 03](../../labs/lab-03-securite-secrets/)
> · **Suivant :** [Module 08 — MCP](../08-mcp/)

---

## 1. La limite — d'où l'on vient

Au [Lab 03](../../labs/lab-03-securite-secrets/), la revue de sécurité de tout le dépôt a fait
deux dégâts, que ni un skill ni un plugin ne réparent :

| Problème | Ce qui s'est passé | Pourquoi un skill ne suffit pas |
|---|---|---|
| **Le bruit** | La revue a lu trente fichiers et la sortie de `dotnet list package` : 60 % du contexte consommés avant la première correction | Un skill s'exécute **dans** votre session : tout ce qu'il lit y reste |
| **La complaisance** | Le relecteur est l'agent qui a écrit le code ; il connaît le raisonnement et tend à le valider | Un skill partage votre contexte, donc vos biais |
| **Le droit d'écrire** | « Relis » s'est transformé en « j'ai corrigé au passage » | Un skill a les mêmes outils que vous |

| Cas d'usage Dev | Cas d'usage DevOps |
|---|---|
| Une revue **indépendante** du diff avant PR, par un relecteur qui ne peut rien modifier | Diagnostiquer un pod en échec : 800 lignes de logs lues ailleurs, 15 lignes rendues |
| « Qu'est-ce qui n'est pas testé ? » sur toute la solution, sans saturer la session | Relire en parallèle Dockerfiles, workflows et manifestes |

Et au [module 06](../06-plugins/), vous avez vu que `pr-review-toolkit` embarque **six agents**.
Voici ce que c'est.

## 2. Le concept — déléguer à un exécutant au contexte séparé

Un **sous-agent** est un agent spécialisé, avec **ses** instructions, **ses** outils et **sa
propre fenêtre de contexte**. Il travaille à côté et ne rend que sa conclusion.

```
  Session principale                         Sous-agent « security-reviewer »
  ──────────────────                         ────────────────────────────────
  « relis le diff, sécurité »  ──────────▶   contexte VIERGE : il n'a pas vu
                                             comment le code a été écrit
                                             lit 30 fichiers, lance dotnet list package
       contexte intact     ◀──────────────   rend un tableau de 12 lignes + un verdict
  « corrige les deux bloquants »             (il n'avait ni Write ni Edit)
```

**Quatre bénéfices, dans l'ordre d'importance :**

1. **Isolation du contexte** — le bruit reste chez lui.
2. **Indépendance du regard** — il n'a pas vu votre raisonnement : il juge le code, pas l'intention.
3. **Restriction d'outils** — un relecteur limité à `Read, Grep, Glob` ne *peut* pas modifier un
   fichier. Ce n'est pas une consigne, c'est le harnais qui l'applique.
4. **Parallélisme** — plusieurs sous-agents travaillent en même temps sur des axes différents.

| | Skill ([module 05](../05-skills/)) | **Sous-agent** |
|---|---|---|
| Nature | Un mode d'emploi | Un exécutant |
| Contexte | Le vôtre | **Le sien**, vierge |
| Outils | Les vôtres | **Ceux qu'on lui accorde** |
| Rend | Tout le déroulé | **Une synthèse** |
| Bon pour | Une procédure à suivre | Une tâche lourde, bruyante, ou qui exige un regard indépendant |

> **Le pont entre les deux :** un skill avec `context: fork` s'exécute dans un sous-agent. Utile
> pour une procédure bruyante qu'on veut aussi pouvoir appeler par `/nom`.

### Vous en utilisez déjà

| Sous-agent intégré | Rôle |
|---|---|
| `Explore` | Recherche rapide dans le code, **lecture seule** |
| `Plan` | Collecte de contexte en mode Plan (module 01) |
| `general-purpose` | Tâches multi-étapes qui explorent et agissent |

## 3. Anatomie

[`security-reviewer.md`](../../plugins/oddo-dev-toolkit/agents/security-reviewer.md) (extrait) :

```markdown
---
name: security-reviewer
description: Relit un diff ou une partie du code de l'ecommerce-app sous l'angle sécurité et
  conformité bancaire — secrets, injection, autorisation, données personnelles dans les logs,
  dépendances vulnérables. À utiliser avant une PR, ou quand on demande un avis de sécurité
  indépendant. Lecture seule.
tools: Read, Grep, Glob, Bash
color: red
---

Tu es ingénieur sécurité applicative dans une banque soumise à DORA et au RGPD. Tu n'as pas
vu la conversation qui a produit ce code : c'est voulu. Ton rôle est de douter.

## Méthode
1. Délimite le périmètre : git diff main...HEAD --stat.
2. Cherche, dans cet ordre : secrets, données personnelles dans les logs, injection, exposition,
   dépendances (dotnet list package --vulnerable), configuration.
3. Pour chaque constat : la ligne, l'exploitabilité dans CE contexte, le correctif.

## Garde-fous
- Lecture seule. Tu ne recopies jamais la valeur d'un secret.

## Format de sortie
| Gravité | Fichier:ligne | Constat | Exploitable ici ? | Correctif |  — puis un verdict.
```

### Les champs qui comptent

| Champ | Rôle | Conseil |
|---|---|---|
| `description` | **Quand** déléguer — le critère de sélection | Décrire la situation, pas l'agent |
| `tools` | Liste blanche d'outils | Minimale. Un relecteur n'a pas besoin de `Write` |
| `disallowedTools` | Liste noire (sur les outils hérités) | `Write, Edit` pour un analyste qui hérite de tout |
| `model` | `haiku`, `sonnet`, `opus`, `inherit` | `haiku` pour lancer des tests et filtrer leur sortie |
| `skills` | Skills **préchargés** dans son contexte | `gen-tests` pour un agent qui écrit des tests |
| `mcpServers` | Serveurs MCP **réservés** à ce sous-agent | Annonce du [module 08](../08-mcp/) |
| `isolation: worktree` | Travaille dans un *worktree* Git temporaire | Un agent qui modifie sans toucher à votre arbre |
| `color` | Couleur dans l'interface | Repérer qui parle |

Le corps suit toujours le même canevas : **un rôle** (« tu es… »), **une méthode** numérotée,
**des garde-fous**, **un format de sortie**. Ce dernier est décisif : un sous-agent qui rend un
paragraphe libre oblige à tout relire, et n'a rien fait gagner.

### Les invoquer

| Façon | Exemple |
|---|---|
| Implicite, par la description | « Qu'est-ce qui n'est pas testé dans cette solution ? » |
| Explicite | « Utilise le sous-agent security-reviewer sur le diff » |
| Mention | `@agent-security-reviewer relis la branche` |
| En parallèle | « Fais relire le diff **en parallèle** par security-reviewer et test-engineer » |
| Toute la session | `claude --agent security-reviewer` |

`Ctrl+B` passe un sous-agent en arrière-plan ; `/tasks` les liste. `/agents` liste, crée (avec
assistant) et inspecte les sous-agents, d'où qu'ils viennent.

### Portée

| Emplacement | Disponible |
|---|---|
| `.claude/agents/<nom>.md` | Ce projet, toute l'équipe |
| `~/.claude/agents/<nom>.md` | Vous, partout |
| Dans un plugin | Préfixé : `oddo-dev-toolkit:security-reviewer` |

---

## 4. Mini-lab — relecteurs indépendants (20 min)

Le plugin `oddo-dev-toolkit`, installé avec le poste standard à la fin du [Lab 03](../../labs/lab-03-securite-secrets/),
apporte déjà six sous-agents.

```bash
cd ~/lab-ecommerce
git switch -c feat/agents-demo
claude
```

**1. Les voir**

```text
> /agents
```

**2. Déléguer sans nommer**

```text
> /context
> Qu'est-ce qui n'est pas testé dans cette solution ? Classe par risque.
> /context
```

Il délègue à `test-engineer`. Comparez les deux `/context` : votre session a reçu une synthèse,
pas les vingt fichiers lus.

**3. Paralléliser**

Faites un petit changement (par exemple, un log dans `OrderingEndpoints.cs` qui inclut
`order.Customer` — volontairement fautif), puis :

```text
> Fais relire ce diff en parallèle par security-reviewer et test-engineer, puis fais-moi
  une synthèse unique : les bloquants d'abord.
```

`security-reviewer` doit relever la donnée personnelle dans le log (R1).

**4. Vérifier la restriction d'outils**

```text
> Demande à security-reviewer de corriger lui-même le log fautif.
```

Il ne peut pas : `tools` ne contient ni `Write` ni `Edit`. **La restriction est technique.**

**5. Créer le vôtre**

```text
> /agents
```

Créez avec l'assistant un agent projet `api-contract-reviewer` : il détecte les changements de
route, de DTO ou de champ JSON dans le diff et liste les consommateurs impactés (Gateway,
Ordering, Web). Outils : `Read, Grep, Glob`. Modèle : `sonnet`. Puis :

```text
> Est-ce que mon diff casse un contrat entre services ?
```

Gardez cet agent : il prendra tout son sens au [Lab 11](../../labs/lab-11-incident-postmortem/).

**6. Nettoyer**

```bash
git restore . && git switch main && git branch -D feat/agents-demo   # vous-même : le hook bloquerait l'agent
```

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| `description` qui décrit l'agent au lieu du moment | Jamais délégué | Décrire **la situation** |
| `tools` omis sur un relecteur | Il hérite de `Write` et « corrige au passage » | Liste minimale |
| Pas de format de sortie | Un pavé à relire entièrement | Tableau imposé + verdict |
| Déléguer une tâche triviale | Surcoût et latence | Le sous-agent sert quand la tâche est **lourde, bruyante ou à juger** |
| Croire qu'il connaît la conversation | Il démarre vierge | Tout ce dont il a besoin doit être dans la demande |
| Un agent « généraliste » | Résultats quelconques | Un agent = un rôle |

---

## 6. Checklist de sortie

- [ ] Je sais expliquer les quatre bénéfices d'un sous-agent, dans l'ordre.
- [ ] J'ai vu une délégation implicite et vérifié l'effet sur `/context`.
- [ ] J'ai lancé deux relecteurs en parallèle et obtenu une synthèse unique.
- [ ] J'ai constaté qu'un outil non listé est techniquement indisponible.
- [ ] J'ai créé mon propre sous-agent avec `/agents`.
- [ ] Je sais choisir entre skill, skill `context: fork` et sous-agent.

---

## 7. La limite suivante

Vos relecteurs sont indépendants et sûrs. Mais ils ne voient **que des fichiers** :

| Le sous-agent… | …devrait pouvoir | …mais il ne voit que |
|---|---|---|
| `db-reviewer` | vérifier le schéma **réellement** migré et la volumétrie des tables | les fichiers `Migrations/*.cs` |
| `a11y-reviewer` | voir la page **rendue**, la console, le comportement au clavier | le source `.razor` |
| `incident-analyst` | lire les **traces** et les **logs structurés** de l'application | ce que vous lui collez |
| tous | lire une PR, un ticket, la doc **à jour** d'EF Core 10 | leur mémoire d'entraînement |

> **→ [Module 08 — MCP](../08-mcp/) :** brancher l'agent — et chaque sous-agent — sur la base,
> le navigateur, la forge et la télémétrie, en lecture seule d'abord.
