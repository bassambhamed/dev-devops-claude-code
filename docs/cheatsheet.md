# Cheat-sheet Claude Code — mémo Dev & DevOps

À garder ouvert pendant toute la formation. Version de référence : **Claude Code 2.1.x**.
La liste exacte des commandes de *votre* version s'obtient en tapant `/` dans une session.

---

## Lancer l'agent

| Commande | Effet |
|---|---|
| `claude` | Session interactive dans le dossier courant |
| `claude "consigne"` | Démarre en exécutant immédiatement ce prompt |
| `claude -p "consigne"` | **Headless** : exécute, imprime, rend la main — scripts et CI |
| `claude -c` · `claude -r` | Continue la dernière conversation · choisit une session à reprendre |
| `claude --chrome` | Session avec le navigateur Chrome connecté (MCP intégré `claude-in-chrome`) |
| `claude --agent <nom>` | Toute la session tourne avec le prompt et les outils d'un sous-agent |
| `claude --plugin-dir ./mon-plugin` | Charge un plugin depuis le disque pour **une** session (développement) |
| `claude doctor` · `claude update` | Diagnostic · mise à jour |

## Préfixes de saisie

| Préfixe | Effet | Exemple |
|:---:|---|---|
| `@` | Référencer un fichier, un dossier, une ressource MCP ou un sous-agent | `@src/ECommerce.Catalog.Api/Endpoints/CatalogEndpoints.cs` · `@agent-db-reviewer` |
| `!` | Exécuter une commande shell ; sa sortie entre en contexte | `!dotnet test ECommerce.slnx` |
| `#` | Ajouter une note durable à la mémoire (`CLAUDE.md`) | `# jamais d'URL de service en dur : service discovery Aspire` |
| `/` | Ouvrir le menu des commandes (natives, perso, skills, plugins, prompts MCP) | `/permissions` |

---

## Commandes natives, par intention

### Se repérer
| Commande | Effet |
|---|---|
| `/help` · `/status` · `/doctor` | Aide · version, modèle, compte · diagnostic |
| `/context` | **Ce qui occupe la fenêtre de contexte**, source par source |
| `/usage` · `/insights` | Coût et limites · statistiques d'usage |

### Cadrer le travail
| Commande | Effet | Réflexe |
|---|---|---|
| `/init` | Analyse le dépôt et génère un `CLAUDE.md` | **Premier geste** sur un dépôt |
| `/memory` | Édite les fichiers mémoire | Inscrire une règle d'équipe |
| `/goal` | Fixe l'objectif de la session | Avant un chantier long |
| `/plan` | Mode Plan : l'agent propose, vous validez | **Avant toute modification non triviale** |
| `/model` · `/effort` | Modèle · niveau de raisonnement | `/effort high` avant une revue de migration |
| `/add-dir <chemin>` | Ouvre un dossier supplémentaire | Dépôt de charts séparé du code |

### Piloter la session
| Commande | Effet |
|---|---|
| `/rewind` | Revient à un checkpoint (code et/ou conversation) |
| `/btw` | Glisse une précision **sans interrompre** la tâche |
| `/compact` · `/clear` | Résume pour libérer du contexte · repart à vide (la mémoire projet reste) |
| `/resume` · `/export` · `/rename` | Reprendre · exporter · renommer une session |
| `/tasks` | Ce qui tourne en arrière-plan (shells, sous-agents) |

### Qualité et sécurité
| Commande | Effet |
|---|---|
| `/code-review [niveau] [--fix]` | Revue du diff : bugs, simplifications |
| `/security-review` | Analyse de sécurité des changements en cours |
| `/permissions` | Règles `allow` / `ask` / `deny` |
| `/hooks` | Les hooks **réellement** actifs |

### Extensions
| Commande | Effet |
|---|---|
| `/skills` | Skills disponibles (projet, perso, plugins) |
| `/agents` | Sous-agents : lister, créer, inspecter |
| `/mcp` | Serveurs MCP : statut, outils, authentification, activer / désactiver |
| `/plugin` | Découvrir, installer, gérer plugins et marketplaces |
| `/reload-plugins` | Appliquer un plugin installé ou mis à jour sans redémarrer |
| `/chrome` | État de la connexion au navigateur, permissions par site |
| `/ide` | Connecter la session terminal à VS Code / JetBrains |

### Aller plus loin
| Commande | Effet | Cas d'usage |
|---|---|---|
| `/loop [intervalle] <prompt>` | Rejoue un prompt à intervalle régulier | Surveiller un rollout, attendre une CI — **en lecture seule** |
| `/install-github-app` | Installe l'application GitHub de Claude et son workflow | Revue de PR par `@claude` dans GitHub |
| `/output-style` · `/statusline` | Style de sortie · barre de statut | Afficher branche et contexte kubectl |

---

## Plugins — en ligne de commande

```bash
claude plugin marketplace add anthropics/claude-plugins-official   # officiel (auto en interactif)
claude plugin marketplace add ./dev-devops-claude-code             # le marketplace de la formation
claude plugin install csharp-lsp@claude-plugins-official           # portée user par défaut
claude plugin install oddo-dev-toolkit@oddo-dev-marketplace --scope project
claude plugin details oddo-dev-toolkit       # inventaire + coût en tokens, AVANT de garder un plugin
claude plugin list                           # version, portée, statut
claude plugin disable|enable|uninstall <plugin>@<marketplace>
claude plugin validate ./plugins/mon-plugin --strict
claude plugin update <plugin>@<marketplace>
```

## MCP — en ligne de commande

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ -H "Authorization: Bearer $TOKEN"
claude mcp add --scope project catalogdb -- npx -y @bytebase/dbhub@1.5.0 --transport stdio --config dbhub.toml
claude mcp list · claude mcp get <nom> · claude mcp remove <nom>
claude mcp reset-project-choices             # rejouer l'approbation des serveurs d'un .mcp.json
```

| Syntaxe en session | Effet |
|---|---|
| `@<serveur>:<protocole>://<chemin>` | Référencer une **ressource** MCP (ex. `@github:issue://123`) |
| `/mcp__<serveur>__<prompt> [args]` | Lancer un **prompt** exposé par un serveur MCP |

**Les MCP présents sans rien configurer :** `ide` (diagnostics de l'éditeur, quand VS Code ou
JetBrains est connecté), `claude-in-chrome` (avec `--chrome`), et les connecteurs de votre compte
claude.ai (marqués *claude.ai* dans `/mcp`).

---

## Où vivent les fichiers

```
<projet>/
├── CLAUDE.md                          # mémoire projet, versionnée, relue à chaque session
├── .mcp.json                          # serveurs MCP du projet — versionné, sans secret
└── .claude/
    ├── settings.json                  # permissions, hooks, plugins d'équipe — versionné
    ├── settings.local.json            # vos réglages locaux — jamais versionné
    ├── commands/<nom>.md              # /nom — commande personnalisée
    ├── skills/<nom>/SKILL.md          # skill (+ fichiers d'appui dans le même dossier)
    ├── agents/<nom>.md                # sous-agent
    └── hooks/<script>.sh              # scripts de garde-fous

<plugin>/
├── .claude-plugin/plugin.json         # manifeste (nom, version, dépendances, userConfig)
├── commands/ · skills/ · agents/      # composants, préfixés /<plugin>:<nom>
├── hooks/hooks.json                   # câblage des hooks (${CLAUDE_PLUGIN_ROOT})
├── .mcp.json · .lsp.json              # serveurs MCP et LSP livrés avec le plugin
└── bin/ · monitors/monitors.json      # exécutables sur le PATH · surveillances en arrière-plan
```

---

## Les 8 réflexes Dev & DevOps

1. **`/init` d'abord**, puis éditer `CLAUDE.md` à la main : c'est là qu'est la valeur.
2. **`/plan` avant toute modification non triviale.** On lit le plan, puis on autorise.
3. **Un garde-fou = un hook, jamais un prompt.**
4. **On relit le résultat, pas l'intention** : le SQL d'une migration, le rendu d'un chart, la page dans le navigateur.
5. **`/context` quand ça dérive**, `/rewind` plutôt que « annule ».
6. **Un bon prompt utilisé deux fois devient une commande ; une procédure devient un skill.**
7. **Avant d'écrire un outil, cherchez le plugin officiel** (`/plugin`) — puis lisez `claude plugin details`.
8. **Jamais de secret dans un prompt, un fichier ou un log.** `dotnet user-secrets`, variables d'environnement, coffre.
