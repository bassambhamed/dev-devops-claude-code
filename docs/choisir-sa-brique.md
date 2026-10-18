# Choisir sa brique — du besoin à la bonne extension

Le document de référence du parcours. Chaque brique de Claude Code existe parce que la précédente
atteint une **limite** sur un cas d'usage réel. Ce document rassemble ces limites, les cas d'usage
Dev et DevOps qui les révèlent, et l'arbre de décision à garder sous la main après la formation.

---

## 1. La chaîne en une image

```
 prompt      commande     mémoire      commande       hook          skill          plugin        sous-agent     MCP
 libre   ──▶ native   ──▶ CLAUDE.md ──▶ perso     ──▶ (garantie) ──▶ (procédure) ──▶ (diffusion) ──▶ (délégation) ──▶ (connexion)
   │            │             │            │             │              │              │               │               │
 « fais »   « cadre »    « souviens »  « rejoue »    « impose »     « sais-faire »  « partage »    « isole »       « vois »
```

Lire la chaîne de gauche à droite, c'est lire l'histoire d'une équipe qui adopte l'outil :
d'abord on **demande**, puis on **cadre**, on **mémorise**, on **rejoue**, on **impose**, on
**capitalise**, on **diffuse**, on **délègue**, et enfin on **connecte**.

**La chaîne s'arrête au MCP.** Chaque maillon est une **brique de Claude Code** : quelque chose
qu'on configure pour outiller l'agent. Le mode headless (`claude -p`) et la CI n'en sont pas : le
premier est un autre **mode d'exécution** des mêmes briques, la seconde un **cas d'usage**. Ils
sont traités hors chaîne, dans l'[annexe](../modules/annexe-agent-sans-terminal/) et au
[Lab 06](../labs/lab-06-ci-cd/).

---

## 2. Chaque transition, justifiée par un cas d'usage

| De → vers | La limite rencontrée | Cas d'usage Dev | Cas d'usage DevOps | Module |
|---|---|---|---|:---:|
| Prompt → **commandes natives** | L'agent part dans une direction et je ne sais ni l'arrêter proprement, ni voir ce qu'il a en tête. | Un refactoring de `OrderingEndpoints` dérape : `/rewind` plutôt que « annule ». | Avant de toucher au `docker-compose.yml` : `/plan` pour lire avant d'autoriser. | [01](../modules/01-commandes-natives/) |
| Commandes natives → **`CLAUDE.md`** | Chaque session repart de zéro : il ignore nos conventions. | Il code une URL `http://localhost:5147` en dur au lieu du service discovery Aspire. | Il lance `dotnet build` au lieu de `dotnet build ECommerce.slnx` et casse le cache CI. | [02](../modules/02-contexte-et-memoire/) |
| `CLAUDE.md` → **commande perso** | Il connaît les règles, mais je retape le même prompt de vingt lignes avant chaque PR. | `/review-diff` : la checklist de revue d'équipe, en une commande. | `/ship` : diff, tests, commit conventionnel, PR — toujours dans le même ordre. | [03](../modules/03-commandes-personnalisees/) |
| Commande perso → **hook** | Ma commande *dit* « ne committe pas de secret » ; rien ne l'*empêche*. Et un collègue committe sans passer par `/ship`. | Un mot de passe de `appsettings.Development.json` part dans un commit. Le formatage n'est appliqué que quand on y pense. | Un `docker compose down -v` efface la base locale d'un collègue pendant une démo. | [04](../modules/04-hooks/) |
| Hook → **skill** | Un hook sait dire **non** ou formater. Il ne sait pas **faire** une procédure qui demande du jugement. | Ajouter une colonne : modèle, `OnModelCreating`, `migrations add`, relecture du SQL, test — huit étapes, une checklist. | Conteneuriser un service : multi-stage, non-root, `.dockerignore`, scan, compose. | [05](../modules/05-skills/) |
| Skill → **plugin** | Mes commandes, hooks et skills vivent dans **mon** `.claude/`. Douze collègues, huit dépôts. Et je réécris peut-être ce qui existe déjà. | Installer le serveur de langage C# (`csharp-lsp`) plutôt que bricoler un hook de build. | Donner les mêmes garde-fous à toute l'équipe en une commande, versionnés. | [06](../modules/06-plugins/) |
| Plugin → **sous-agent** | Une revue de 40 fichiers sature ma session ; le relecteur a vu tout mon raisonnement et approuve par complaisance. | Une revue sécurité **indépendante** du diff, sans écriture possible. | Diagnostiquer un pod en `CrashLoopBackOff` : 800 lignes de logs lues ailleurs, 15 lignes rendues. | [07](../modules/07-sous-agents/) |
| Sous-agent → **MCP** | L'agent ne voit que le disque et le shell : ni la base, ni le navigateur, ni GitHub, ni les traces. | Vérifier le schéma PostgreSQL réellement migré ; voir le rendu de la page dans Chrome. | Lire les traces et logs structurés de l'app via Aspire ; interroger Grafana pendant un incident. | [08](../modules/08-mcp/) |

> **La règle de la formation :** on ne passe à la brique suivante qu'après avoir *senti* la limite
> de la précédente sur un cas réel. Chaque module s'ouvre sur cette limite et se termine sur la
> suivante.

---

## 3. L'arbre de décision

À dérouler dans l'ordre : la première réponse « oui » donne la brique.

```
Le besoin doit-il s'appliquer À COUP SÛR, même si le modèle l'oublie ou si personne n'y pense ?
  └─ oui ─▶ HOOK  (ou /permissions si une simple règle allow / ask / deny suffit)

Le besoin est-il une connaissance stable du projet (convention, commande, interdit) ?
  └─ oui ─▶ CLAUDE.md  (40 à 120 lignes, des règles vérifiables)

L'agent doit-il accéder à un système HORS du dépôt (base, navigateur, forge, observabilité) ?
  └─ oui ─▶ MCP  (lecture seule d'abord ; plugin officiel s'il existe)

La tâche est-elle lourde, bruyante, ou doit-elle être jugée par un regard indépendant ?
  └─ oui ─▶ SOUS-AGENT  (outils restreints, format de sortie imposé)

Est-ce une procédure en plusieurs étapes, avec du jugement ou des fichiers d'appui ?
  └─ oui ─▶ SKILL  (déclenchée par l'agent quand la description correspond)

Est-ce un prompt que je relance moi-même, à la demande ?
  └─ oui ─▶ COMMANDE PERSONNALISÉE

Faut-il le donner à l'équipe ou à plusieurs dépôts ?
  └─ oui ─▶ PLUGIN  (et marketplace interne)
```

> **Et s'il faut que ça tourne sans moi ?** Ce n'est pas une brique de plus : ce sont **les mêmes
> briques**, exécutées autrement — `claude -p` dans un script ou un job de CI, `/loop` pendant une
> session, toujours en lecture seule. Voir l'[annexe — l'agent sans terminal](../modules/annexe-agent-sans-terminal/).

---

## 4. Les confusions qui coûtent cher

| On hésite entre… | Le critère qui tranche | Exemple |
|---|---|---|
| **Commande** et **skill** | *Qui* déclenche ? Vous → commande. L'agent, selon la situation → skill. Besoin de fichiers d'appui → skill. | `/ship` est une commande (vous décidez quand livrer). `ef-migration` est un skill (l'agent le mobilise dès qu'on parle de colonne). |
| **Skill** et **hook** | Faut-il du **jugement** ou une **garantie** ? | « Écrire une migration propre » : skill. « Ne jamais éditer une migration committée » : hook. |
| **`CLAUDE.md`** et **hook** | Une consigne peut être oubliée. Un contrôle non. | « Commits en anglais » : `CLAUDE.md`. « Aucun secret committé » : hook. |
| **Skill** et **sous-agent** | Le skill est un *mode d'emploi* exécuté dans votre session ; le sous-agent est un *exécutant* avec son propre contexte. | `gen-tests` (skill) écrit les tests ; `test-engineer` (sous-agent) dit ce qui manque, sans rien écrire. |
| **MCP** et **CLI dans le shell** | Le MCP donne des outils typés et scopés ; la CLI suffit si elle est déjà là et que le résultat est textuel. | `gh` suffit pour ouvrir une PR. Le MCP Aspire est indispensable pour lire les traces. |
| **MCP** et **plugin** | Le MCP *connecte* ; le plugin *distribue* (et peut contenir des MCP). | Le plugin officiel `github` installe le serveur MCP GitHub. |
| **Plugin maison** et **plugin officiel** | Ne réécrivez jamais un connecteur ou un outil générique. Écrivez ce qui porte **vos** conventions. | `csharp-lsp` (officiel) pour les diagnostics ; `oddo-dev-toolkit` (maison) pour la doctrine de migration. |

---

## 5. Le niveau de garantie de chaque brique

| Brique | Qui décide de l'appliquer | Garanti ? | Usage typique en banque |
|---|---|:---:|---|
| Prompt | Le modèle | Non | Une demande ponctuelle |
| `CLAUDE.md` | Le modèle (relu à chaque session) | Non | Conventions, commandes, interdits « doux » |
| Commande perso | Vous | Le contenu, oui ; son usage, non | Raccourcis d'équipe |
| Skill | Le modèle, selon la description | Non | Procédures et doctrines |
| Sous-agent | Le modèle délègue ; les **outils** sont restreints par le harnais | La restriction d'outils, oui | Revue, investigation en lecture seule |
| `/permissions` | Le harnais | **Oui** | `allow` / `ask` / `deny` par outil et par commande |
| Hook | Le harnais | **Oui** | Anti-secret, blocage destructif, audit DORA |
| Contrôle de plateforme | La forge, le cluster | **Oui**, hors agent | Branche protégée, environnement protégé, RBAC |

> **Plus une action est irréversible, plus la garantie doit être haute.** Une convention de
> nommage vit dans `CLAUDE.md`. Un secret se bloque par hook. Une mise en production se protège
> côté plateforme, là où l'agent n'a pas la main.
