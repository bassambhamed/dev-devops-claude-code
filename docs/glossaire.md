# Glossaire

Les termes que vous croiserez pendant la formation, expliqués pour un profil Dev ou DevOps.

---

## Intelligence artificielle générative

**LLM (Large Language Model)** — Un modèle entraîné à **prédire la suite la plus plausible** d'un
texte. Il ne « comprend » pas votre code : il produit la suite la plus vraisemblable compte tenu
de ce que vous lui avez donné. La qualité vient donc du contexte.

**Token** — L'unité de découpage du texte (≈ 4 caractères). Coûts, limites et fenêtre de contexte
se comptent en tokens.

**Fenêtre de contexte** — Ce que le modèle peut prendre en compte en une fois. Un contexte
saturé est la première cause de réponses incohérentes (`/context`, `/compact`, `/clear`).

**Hallucination** — Une affirmation fausse énoncée avec assurance : une méthode EF Core qui
n'existe pas, un paramètre de Helm imaginaire. D'où la règle : **on vérifie**.

**Agent de coding** — Un LLM équipé d'**outils** (lire, éditer, exécuter) et d'une **boucle** :
il agit, observe le résultat (une erreur de compilation, un test rouge), corrige.

**Injection de prompt** — Du texte placé dans une donnée (un ticket, une page web, une ligne de
base) qui tente de se faire passer pour une consigne. Parade : règle R6, outils en lecture seule.

---

## Claude Code — les briques, dans l'ordre du parcours

**Harnais** — Le programme Claude Code lui-même, par opposition au modèle. Les commandes `/`, les
permissions et les hooks sont exécutés par le harnais : ils sont **déterministes**.

**Commande native** (`/rewind`, `/plan`, `/context`…) — Une instruction au harnais, livrée avec
l'outil.

**`CLAUDE.md`** — La mémoire du projet : stack, commandes, conventions, interdits. Relue
automatiquement à chaque session. Le préfixe `#` y ajoute une règle à la volée.

**Commande personnalisée** — Un fichier Markdown dans `.claude/commands/` dont le contenu devient
un prompt rejouable par `/nom`. Accepte `$ARGUMENTS` et l'injection de sortie shell (`` !`git diff` ``).
Depuis Claude Code 2.1, les commandes sont une forme simple de skill.

**Hook** — Un script déclenché **automatiquement** par le harnais sur un événement
(`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`…). Code de sortie `2` = action bloquée, et
le message `stderr` est renvoyé à l'agent.

**Permissions** — Les règles `allow` / `ask` / `deny` qui décident ce que l'agent peut faire seul,
ce qui demande confirmation, et ce qui est interdit.

**Skill** — Un dossier `.claude/skills/<nom>/` avec un `SKILL.md` : une procédure et ses fichiers
d'appui. L'agent la charge **quand sa `description` correspond à la demande** ; on peut aussi
l'appeler par `/nom`. Seule la description occupe le contexte en permanence (*divulgation
progressive*).

**Plugin** — Un paquet distribuable : commandes, skills, sous-agents, hooks, serveurs MCP et LSP,
sous un manifeste `.claude-plugin/plugin.json`. Ses composants sont préfixés : `/oddo-dev-toolkit:ship`.

**Marketplace** — Un catalogue de plugins : un dépôt Git avec un `.claude-plugin/marketplace.json`.
L'officiel, `claude-plugins-official`, est ajouté automatiquement ; on peut en héberger un interne.

**Plugin LSP** — Un plugin qui branche un serveur de langage (ex. `csharp-lsp`) : l'agent reçoit
les diagnostics du compilateur juste après chaque édition, et peut naviguer par symbole.

**Plugin « bundle »** — Un plugin sans composant, fait uniquement de `dependencies` : l'installer
installe tout un poste de travail standard.

**`userConfig`** — Les réglages qu'un plugin demande à l'installation. Une valeur `sensitive`
(un jeton) part dans le trousseau du système, jamais dans un fichier.

**Sous-agent** — Un agent spécialisé, avec ses instructions, **ses outils** et **son propre
contexte**, à qui l'agent principal délègue une tâche. Il rend une synthèse, pas ses 800 lignes
de lecture. Défini dans `.claude/agents/<nom>.md`.

**MCP (Model Context Protocol)** — Un protocole ouvert qui branche l'agent sur des systèmes
externes. Un **serveur MCP** expose des *tools* (actions), des *resources* (données, `@serveur:…`)
et des *prompts* (`/mcp__serveur__prompt`).

**MCP intégrés** — Ceux que Claude Code fournit sans configuration : `ide` (diagnostics de
VS Code / JetBrains), `claude-in-chrome` (navigateur, avec `--chrome`), connecteurs du compte claude.ai.

**Tool search** — Le mécanisme qui ne charge la définition d'un outil MCP que lorsqu'il est
utile : brancher un serveur ne sature plus le contexte d'office.

**Mode headless** (`claude -p`) — L'agent sans interface : il reçoit un prompt, agit, imprime
et rend la main. C'est ce qui permet de l'appeler depuis un script ou une CI.

**Checkpoint / `/rewind`** — Un point de reprise automatique, que `/rewind` restaure.

**Mode Plan** (`/plan`) — L'agent propose un plan et **attend votre validation** avant d'agir.

---

## .NET & ecommerce-app

**.NET Aspire** — L'orchestrateur de l'application : `AppHost` démarre les services, PostgreSQL
(en conteneur) et le tableau de bord de télémétrie.

**Service discovery** — Les services s'appellent par **nom** (`https+http://catalog`), jamais par
adresse codée en dur. Hors Aspire, on fournit `services__catalog__http__0`.

**EF Core / migration** — L'ORM .NET. Une migration est un fichier versionné qui décrit un
changement de schéma ; `dotnet ef migrations add` la génère, `dotnet ef migrations script`
montre le SQL.

**Testcontainers** — Une bibliothèque qui démarre une vraie base (PostgreSQL) dans Docker le temps
d'une suite de tests. Plus fiable qu'un provider in-memory, qui ignore contraintes et index.

**`WebApplicationFactory`** — Démarre l'API en mémoire pour des tests d'intégration HTTP.

**OpenTelemetry** — Le standard de télémétrie : **traces** (le chemin d'une requête entre
services), **métriques** (compteurs, histogrammes), **logs structurés**.

**Blazor Server** — L'interface web en C# : composants `.razor` rendus côté serveur.

**a11y** — Accessibilité : utilisable au clavier, au lecteur d'écran, sans dépendre de la couleur.

---

## DevOps — rappels utiles

**Image chiselée** — Une image .NET minimale, sans shell ni gestionnaire de paquets.

**k3d** — Kubernetes léger (k3s) dans Docker : un cluster local en quelques secondes.

**Probe liveness / readiness** — « Le conteneur est-il vivant ? » / « Peut-il recevoir du
trafic ? ». La readiness de Catalog inclut la base : base injoignable = pod retiré du trafic.

**Chart Helm** — Templates Kubernetes + `values.yaml` paramétrable par environnement.

**Post-mortem blameless** — Compte rendu d'incident centré sur les causes systémiques, jamais
sur les personnes.

**DORA** — Règlement européen sur la résilience opérationnelle numérique du secteur financier :
traçabilité et maîtrise des outils — d'où les hooks d'audit.

**MTTD / MTTR** — Temps moyen de détection / de rétablissement d'un incident.

---

## Les confusions les plus fréquentes

| On confond souvent… | …alors que |
|---|---|
| **Commande** et **skill** | La commande, *vous* la déclenchez ; le skill, *l'agent* le mobilise quand la situation correspond, et il peut porter des fichiers d'appui. |
| **Skill** et **hook** | Le skill guide un travail qui demande du jugement ; le hook impose une règle sans exception. |
| **Skill** et **sous-agent** | Le skill s'exécute dans votre contexte ; le sous-agent travaille dans le sien et ne rend qu'une synthèse. |
| **Hook** et **prompt** | Le hook est exécuté par le programme, toujours ; le prompt est interprété par le modèle, généralement. |
| **MCP** et **plugin** | Le MCP *connecte* à un système ; le plugin *distribue* une configuration (qui peut contenir des MCP). |
| **`CLAUDE.md`** et **`settings.json`** | Le premier informe le modèle ; le second contraint le harnais. |
| **`/clear`** et **`/compact`** | `/clear` repart à vide ; `/compact` résume et garde l'essentiel. |
