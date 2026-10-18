# Module 06 — Plugins : consommer, produire, distribuer, gouverner

> **Durée :** 60 min · **Pré-requis :** [Module 05](../05-skills/) et [Lab 02](../../labs/lab-02-tests/)
> · **Suivant :** [Lab 03 — Sécurité & secrets](../../labs/lab-03-securite-secrets/), puis
> [Module 07 — Sous-agents](../07-sous-agents/)

---

## 1. La limite — d'où l'on vient

À la fin du [Lab 02](../../labs/lab-02-tests/), votre `.claude/` contient trois commandes, quatre
hooks et deux skills. C'est du bon travail — qui ne sert qu'à **vous**, dans **un** dépôt.

| Problème | Cas d'usage Dev | Cas d'usage DevOps |
|---|---|---|
| **Partager** | Douze développeurs, huit dépôts : chacun recopie `.claude/` à la main, et les versions divergent | Les garde-fous (anti-secret, blocage destructif) doivent être **identiques** partout, et à jour |
| **Ne pas réinventer** | Vous attendez le hook `Stop` pour découvrir une erreur de type ; un serveur de langage la donnerait après chaque édition | Vous alliez écrire un connecteur Grafana ; l'éditeur en publie un |
| **Maîtriser** | Un collègue installe un plugin trouvé sur Internet qui exécute des scripts sur son poste | La DSI doit pouvoir dire quelles sources sont autorisées |

## 2. Le concept — le paquet et le catalogue

Un **plugin** regroupe, sous un manifeste, tout ce que les modules précédents produisent — et
plus encore. Un **marketplace** est un catalogue de plugins : un dépôt Git avec un
`.claude-plugin/marketplace.json`.

```
   Marketplace (dépôt Git)                Plugin                  Ce qu'il peut embarquer
   ───────────────────────────      ────────────────────     ──────────────────────────────────
   claude-plugins-official     ──▶  csharp-lsp           ──▶  commands/ skills/ agents/
   (300+, ajouté d'office)          context7                  hooks/hooks.json
                                    pr-review-toolkit         .mcp.json   (serveurs MCP)
   oddo-dev-marketplace        ──▶  oddo-dev-toolkit          .lsp.json   (serveurs de langage)
   (le vôtre, interne)              oddo-dev-standard         bin/  monitors/  output-styles/
```

**Le principe de ce module : consommer avant de produire.** Avant d'écrire un outil, cherchez
s'il existe. N'écrivez que ce qui porte **vos** conventions — votre doctrine de migration, vos
garde-fous bancaires —, jamais un connecteur ou un outil générique.

| | `.claude/` du projet | **Plugin** |
|---|---|---|
| Portée | Un dépôt | Tous les dépôts où il est activé |
| Diffusion | Copier-coller | `claude plugin install`, une commande |
| Mise à jour | Chacun refait la copie | Un commit + une version ; mise à jour automatique possible |
| Noms | `/ship` | `/oddo-dev-toolkit:ship` — **aucun conflit** possible |
| Contenu possible | commandes, skills, agents, hooks, MCP | + **serveurs LSP**, exécutables `bin/`, moniteurs, styles de sortie, dépendances |

---

## 3. Anatomie

### 3.1 Les marketplaces

| Marketplace | Nom (après `@`) | Comment l'obtenir |
|---|---|---|
| Officiel Anthropic — plugins Anthropic **et** éditeurs | `claude-plugins-official` | Ajouté automatiquement à la première session interactive |
| Communautaire (soumis à Anthropic) | `claude-community` | `/plugin marketplace add anthropics/claude-plugins-community` |
| Démo (exemples) | `claude-code-plugins` | `/plugin marketplace add anthropics/claude-code` |
| Tiers ou interne | le `name` de son `marketplace.json` | `/plugin marketplace add <owner/repo \| URL git \| chemin local>` |

### 3.2 Consommer : `/plugin`

```text
> /plugin                                   # onglets Discover · Installed · Marketplaces · Errors
> /plugin install csharp-lsp@claude-plugins-official
```

Le panneau de détail montre, **avant** installation :
- **Will install** : commandes, agents, skills, hooks, serveurs MCP et LSP ;
- **Context cost** : *Every turn* (ajouté à chaque message) et *When invoked* (à l'usage) ;
- le choix de la **portée** :

| Portée | Pour qui | Écrit dans |
|---|---|---|
| `user` | Vous, tous vos projets | `~/.claude/settings.json` |
| `project` | **Toute l'équipe** de ce dépôt | `.claude/settings.json` (versionné) |
| `local` | Vous, ce dépôt seulement | `.claude/settings.local.json` |

En ligne de commande, l'équivalent — et la commande à connaître par cœur :

```bash
claude plugin details pr-review-toolkit     # inventaire + coût en tokens
claude plugin list                          # version, portée, statut
claude plugin disable|enable|uninstall <plugin>@<marketplace>
```

### 3.3 La sélection Dev & DevOps du marketplace officiel

Noms vérifiés dans le catalogue `claude-plugins-official`. Le catalogue évolue : `/plugin` reste
la source de vérité.

| Besoin | Plugin | Ce qu'il apporte | Composants |
|---|---|---|---|
| **Diagnostics du compilateur** | `csharp-lsp` · `jdtls-lsp` (Java) · `typescript-lsp` | Erreurs et avertissements **après chaque édition**, navigation par symbole | serveur LSP (binaire à installer) |
| **Documentation à jour** | `context7` | La doc de la version exacte d'EF Core, d'Aspire, de Blazor | serveur MCP distant |
| **Workflow Git** | `commit-commands` | `/commit`, `/commit-push-pr`, `/clean_gone` | commandes |
| **Revue** | `code-review` · `pr-review-toolkit` | Revue multi-agents ; six relecteurs spécialisés (tests, erreurs silencieuses, typage…) | commandes + **agents** |
| **Développer une fonctionnalité** | `feature-dev` | Explorer → architecturer → relire | commande + 3 **agents** |
| **Sécurité** | `security-guidance` · `semgrep` · `sonarqube` · `claude-security` | Avertissements à l'édition, revue du diff en fin de tâche, règles d'analyse | **hooks**, skills |
| **Front** | `frontend-design` · `playwright` · `figma` | Direction visuelle ; navigateur piloté (tests E2E) ; maquettes | skill ; serveur MCP |
| **Forges & outils** | `github` · `gitlab` · `atlassian` · `sentry` · `grafana-mcp` | PR, tickets, erreurs, métriques | serveurs MCP |
| **Outiller Claude** | `hookify` · `plugin-dev` · `skill-creator` · `claude-md-management` · `mcp-server-dev` | Écrire un hook en langage naturel, un plugin, un skill, un serveur MCP | skills, agents, hooks |
| **Apprendre** | `explanatory-output-style` · `learning-output-style` | L'agent explique ses choix, ou vous fait écrire le code aux points clés | hooks |

### 3.4 Lire un plugin avant de l'installer — trois anatomies réelles

**`csharp-lsp` — un plugin qui tient dans son entrée de catalogue.** Son dossier ne contient qu'un
`README` : toute la configuration est dans `marketplace.json` (`"strict": false`) :

```json
{
  "name": "csharp-lsp",
  "source": "./plugins/csharp-lsp",
  "strict": false,
  "lspServers": {
    "csharp-ls": { "command": "csharp-ls", "extensionToLanguage": { ".cs": "csharp" } }
  }
}
```

Leçon : un plugin LSP **ne contient pas** le serveur de langage. Il faut installer le binaire
(`dotnet tool install --global csharp-ls`), sinon l'onglet *Errors* affiche
`Executable not found in $PATH`. Et il ne couvre que `.cs` — pas les `.razor`.

**`context7` — un plugin qui n'est qu'un serveur MCP.** Son `.mcp.json` complet :

```json
{ "mcpServers": { "context7": { "type": "http", "url": "https://mcp.context7.com/mcp?client=claude-code-plugin" } } }
```

Coût permanent mesuré : **~0 token**, grâce au *tool search* qui ne charge les outils MCP qu'à
l'usage ([module 08](../08-mcp/)).

**`grafana-mcp` — un plugin qui demande un secret proprement.** Son manifeste déclare un
`userConfig` ; le jeton est marqué `sensitive` :

```json
"userConfig": {
  "grafana_url": { "type": "string", "title": "Grafana instance URL", "required": true, "description": "…" },
  "grafana_service_account_token": { "type": "string", "title": "Grafana service account token",
                                     "required": true, "sensitive": true, "description": "…" }
}
```

Claude Code le demande à l'activation et le range dans le **trousseau du système** — jamais dans
un fichier. Son README prévient aussi : *40+ outils MCP — ne l'activer que quand on en a besoin.*

> **La grille de lecture avant d'installer, en environnement bancaire :**
> 1. **Éditeur** : Anthropic, l'éditeur de l'outil, ou inconnu ?
> 2. **`claude plugin details`** : qu'est-ce qui s'exécute ? Des **hooks** et des **serveurs MCP**
>    tournent avec vos droits, sur votre poste, sans coût de contexte — donc sans bruit.
> 3. **Réseau** : un serveur MCP distant reçoit ce que l'agent lui envoie (R1, R6).
> 4. **Coût** : *Every turn* — trois plugins bien choisis valent mieux que quinze « pour voir ».
> 5. **Version** : épinglée ? mise à jour automatique ? (activée par défaut pour l'officiel,
>    désactivée pour les marketplaces tiers et locaux).

### 3.5 Produire : la structure d'un plugin

```
oddo-dev-toolkit/
├── .claude-plugin/
│   └── plugin.json          ← manifeste (seul « name » est obligatoire)
├── commands/                → /oddo-dev-toolkit:ship, /oddo-dev-toolkit:review-diff
├── skills/<nom>/SKILL.md    → /oddo-dev-toolkit:ef-migration … (+ fichiers d'appui)
├── agents/<nom>.md          → sous-agents (module 07)
├── hooks/
│   ├── hooks.json           ← câblage, avec ${CLAUDE_PLUGIN_ROOT}
│   └── *.sh
├── .mcp.json · .lsp.json    ← (optionnel) serveurs MCP et LSP
└── bin/ · monitors/ · output-styles/ · settings.json   ← (optionnel)
```

[`plugin.json`](../../plugins/oddo-dev-toolkit/.claude-plugin/plugin.json) de la formation :

```json
{
  "name": "oddo-dev-toolkit",
  "displayName": "ODDO BHF — Dev & DevOps toolkit",
  "version": "1.0.0",
  "description": "Commandes, skills, sous-agents de revue et garde-fous déterministes…",
  "author": { "name": "Formation Claude Code Dev & DevOps" },
  "license": "MIT",
  "userConfig": {
    "audit_dir": { "type": "directory", "title": "Dossier du journal d'audit",
                   "description": "Toujours HORS d'un dépôt Git.", "default": "~/.claude/audit" }
  }
}
```

Le hook d'audit lit cette option dans `$CLAUDE_PLUGIN_OPTION_AUDIT_DIR` : chaque poste choisit
où écrire son journal, sans modifier le plugin.

**Les règles qui changent par rapport à `.claude/` :**

| Dans `.claude/` | Dans un plugin | Pourquoi |
|---|---|---|
| `"$CLAUDE_PROJECT_DIR"/.claude/hooks/x.sh` | `"${CLAUDE_PLUGIN_ROOT}"/hooks/x.sh` | Le plugin ne sait pas dans quel projet il tourne |
| `CLAUDE.md` à la racine | **Ignoré** | Les consignes d'un plugin passent par un skill |
| `/ship` | `/oddo-dev-toolkit:ship` | Espace de noms : aucun conflit entre plugins |
| `mcpServers` dans un agent | **Ignoré** | Les serveurs MCP d'un plugin se déclarent dans son `.mcp.json` |

**La boucle de développement :**

```bash
claude plugin validate ./plugins/oddo-dev-toolkit --strict   # forme du manifeste, chemins, MCP
claude --plugin-dir ./plugins/oddo-dev-toolkit               # charge le plugin pour UNE session
claude plugin details oddo-dev-toolkit                       # coût réel
```

Sortie réelle de `claude plugin details` pour le toolkit de la formation :

```
Component inventory
  Skills (10)  ci-pipeline, containerize, ef-migration, gen-tests, git-commit, open-pr,
               postmortem, review-diff, ship, ui-modernize
  Agents (6)   security-reviewer, test-engineer, incident-analyst, k8s-debug-pod, a11y-reviewer, db-reviewer
  Hooks (3)    SessionStart, PreToolUse, PostToolUse  (harness-only — no model context cost)

Projected token cost
  Always-on:   ~1,279 tok   added to every session
```

Deux lectures : les **commandes** sont comptées comme des skills (fusion du module 05), et les
**hooks ne coûtent rien en contexte** — ce qui ne veut pas dire qu'ils ne coûtent rien en
risque.

### 3.6 Distribuer

**Le catalogue** — [`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json) à la
racine du dépôt :

```json
{
  "name": "oddo-dev-marketplace",
  "owner": { "name": "Formation Claude Code Dev & DevOps — ODDO BHF" },
  "allowCrossMarketplaceDependenciesOn": ["claude-plugins-official"],
  "plugins": [
    { "name": "oddo-dev-toolkit",  "source": "./plugins/oddo-dev-toolkit" },
    { "name": "oddo-dev-standard", "source": "./plugins/oddo-dev-standard" }
  ]
}
```

**L'installation par l'équipe** — trois façons, de la plus manuelle à la plus automatique :

| Méthode | Commande / fichier | Pour |
|---|---|---|
| Manuelle | `claude plugin marketplace add ODDO-BHF/claude-dev-toolkit` puis `claude plugin install oddo-dev-toolkit@oddo-dev-marketplace` | Essayer |
| **Par dépôt** | `extraKnownMarketplaces` + `enabledPlugins` dans le `.claude/settings.json` versionné du dépôt | **Une équipe** : proposé à chacun après l'acceptation de la confiance du dossier |
| Par la DSI | les mêmes clés dans les *managed settings* | Toute l'organisation, non désactivable |

```json
{
  "extraKnownMarketplaces": {
    "oddo-dev-marketplace": { "source": { "source": "github", "repo": "ODDO-BHF/claude-dev-toolkit" } }
  },
  "enabledPlugins": { "oddo-dev-toolkit@oddo-dev-marketplace": true }
}
```

**Le plugin « bundle » — un poste standard en une commande.** Un plugin peut ne contenir **que**
des dépendances. [`oddo-dev-standard`](../../plugins/oddo-dev-standard/.claude-plugin/plugin.json) :

```json
{
  "name": "oddo-dev-standard",
  "version": "1.0.0",
  "dependencies": [
    "oddo-dev-toolkit",
    { "name": "csharp-lsp",        "marketplace": "claude-plugins-official" },
    { "name": "context7",          "marketplace": "claude-plugins-official" },
    { "name": "security-guidance", "marketplace": "claude-plugins-official" }
  ]
}
```

Sortie réelle de l'installation :

```
✔ Successfully installed plugin: oddo-dev-standard@oddo-dev-marketplace (scope: user)
  (+ 4 dependencies: oddo-dev-toolkit, csharp-lsp, context7, security-guidance)
```

Une dépendance vers un **autre** marketplace n'est installée que si le marketplace racine
l'autorise (`allowCrossMarketplaceDependenciesOn`) : un catalogue ne peut pas faire installer
silencieusement des plugins d'une source que vous n'avez pas relue. On peut aussi contraindre la
version : `{ "name": "secrets-vault", "version": "~2.1.0" }`.

**Les mises à jour.** `version` dans `plugin.json` fige ce que reçoivent les postes : une
correction = un commit **et** un incrément de version. `claude plugin tag --push` pose un tag
cohérent avec le manifeste. Côté poste : `claude plugin update <plugin>@<marketplace>`, puis
`/reload-plugins`.

### 3.7 Gouverner — ce que la DSI peut imposer

Un plugin exécute du code sur le poste. En banque, la liste des sources autorisées n'est pas un
choix individuel. Les *managed settings* (console d'administration, MDM ou fichier système)
s'imposent à toutes les portées :

| Clé | Effet |
|---|---|
| `strictKnownMarketplaces` | **Liste blanche** des sources de marketplaces (`[]` = tout bloquer) |
| `blockedMarketplaces` | Liste noire, vérifiée en premier |
| `enabledPlugins` (managé) | `true` : imposé et non désactivable ; `false` : interdit et masqué |
| `disableSideloadFlags` | Refuse `--plugin-dir` et le chargement de plugins hors marketplace |
| `strictPluginOnlyCustomization` | N'accepte skills, agents, hooks, MCP **que** s'ils viennent d'un plugin ou des réglages managés |
| `allowManagedHooksOnly` | Seuls les hooks des réglages managés s'exécutent |
| `pluginTrustMessage` | Ajoute votre message à l'avertissement de confiance avant installation |

---

## 4. Mini-lab — consommer, produire, distribuer (35 min)

### Partie A — consommer un plugin officiel (10 min)

```bash
dotnet tool install --global csharp-ls     # le binaire que le plugin attend
cd ~/lab-ecommerce && claude
```
```text
> /plugin install csharp-lsp@claude-plugins-official
```

Lisez le panneau (*Will install*, *Context cost*), choisissez la portée **project**. Puis :

```text
> Dans OrderingEndpoints.cs, juste après la récupération du produit, ajoute
  `int prixArrondi = product.Price;` — je veux voir ce que remonte le serveur de langage.
  Ne lance aucun build.
```

Sous l'édition apparaît `Found N new diagnostic issues in 1 file` (Ctrl+O pour le détail) :
l'agent voit l'erreur `CS0266` (conversion implicite de `decimal` en `int`) **sans avoir lancé de
build**. Faites `/rewind`.

Puis **lisez sans installer** deux plugins que vous croiserez. Dans une session, `/plugin install`
ouvre d'abord le panneau de détail : rien n'est installé tant que vous n'avez pas choisi une portée.

```text
> /plugin install pr-review-toolkit@claude-plugins-official     # lire, puis Échap
> /plugin install security-guidance@claude-plugins-official     # lire, puis décider
```

`pr-review-toolkit` embarque **six agents** ; `security-guidance`, quatre **hooks** (dont un `Stop`
qui relit le diff). Décidez en connaissance de cause. Une fois un plugin installé,
`claude plugin details <nom>` donne son coût mesuré.

### Partie B — packager votre `.claude/` (15 min)

```bash
mkdir -p ~/mon-toolkit/.claude-plugin
cp -r ~/lab-ecommerce/.claude/{commands,skills,hooks} ~/mon-toolkit/
```

```text
> Dans ~/mon-toolkit : écris .claude-plugin/plugin.json (name mon-toolkit, version 0.1.0,
  description, author) et hooks/hooks.json à partir des hooks de ~/lab-ecommerce/.claude/settings.json,
  en remplaçant "$CLAUDE_PROJECT_DIR"/.claude/hooks par "${CLAUDE_PLUGIN_ROOT}"/hooks.
  N'oublie pas l'enveloppe { "hooks": { ... } }.
```

```bash
claude plugin validate ~/mon-toolkit --strict
claude --plugin-dir ~/mon-toolkit
```
```text
> /help        # vos commandes apparaissent sous /mon-toolkit:…
> /hooks       # ATTENTION : chaque hook apparaît DEUX fois (projet + plugin)
```

**Le piège classique :** si les hooks restent aussi dans `.claude/settings.json`, ils
s'exécutent deux fois. Retirez-les du projet : c'est désormais le plugin qui les porte.

### Partie C — distribuer (10 min)

Un marketplace, c'est un dossier (ou un dépôt Git) avec un `.claude-plugin/marketplace.json` :

```bash
mkdir -p ~/mon-marketplace/.claude-plugin && mv ~/mon-toolkit ~/mon-marketplace/
cat > ~/mon-marketplace/.claude-plugin/marketplace.json <<'JSON'
{
  "name": "mon-marketplace",
  "owner": { "name": "Mon équipe" },
  "plugins": [ { "name": "mon-toolkit", "source": "./mon-toolkit" } ]
}
JSON
claude plugin validate ~/mon-marketplace
claude plugin marketplace add ~/mon-marketplace
cd ~/lab-ecommerce
claude plugin install mon-toolkit@mon-marketplace --scope project
cat .claude/settings.json                      # enabledPlugins est apparu
```

Ajoutez à ce fichier le bloc `extraKnownMarketplaces` (§3.6 — en vrai une source `github` ; ici
`{ "source": "directory", "path": "<chemin absolu de ~/mon-marketplace>" }`) et committez. Un
collègue qui clone le dépôt et accepte la confiance du dossier se verra proposer le marketplace
et le plugin.

Enfin, **lisez** — sans l'installer encore — le poste standard de la formation :

```bash
claude plugin marketplace add "$FORMATION"
cat "$FORMATION/plugins/oddo-dev-standard/.claude-plugin/plugin.json"
```

Un plugin, cinq installations. Vous l'installerez à la fin du [Lab 03](../../labs/lab-03-securite-secrets/),
quand votre propre chaîne de sécurité vous aura montré ce qu'il contient.

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| Installer « pour voir » quinze plugins | Contexte et sessions alourdis, hooks inconnus actifs | `details` avant, `disable` après |
| Installer un plugin LSP sans le binaire | `Executable not found in $PATH` dans *Errors* | Installer le binaire, relancer |
| `$CLAUDE_PROJECT_DIR` dans les hooks du plugin | Chemins introuvables chez les autres | `"${CLAUDE_PLUGIN_ROOT}"` entre guillemets |
| `hooks.json` sans l'enveloppe `"hooks"` | Le fichier ne se charge pas | `{ "hooks": { "PreToolUse": [...] } }` |
| Garder les hooks dans le projet **et** le plugin | Double exécution | Une seule source |
| Secret dans le `.mcp.json` du plugin | Secret distribué à toute l'équipe | `userConfig` `sensitive`, ou `${VAR}` |
| Oublier d'incrémenter `version` | Personne ne reçoit le correctif | Une correction = une version |
| Réécrire un connecteur officiel | Maintenance à vie d'un doublon | Dépendre du plugin de l'éditeur |

---

## 6. Checklist de sortie

- [ ] J'ai installé un plugin officiel après avoir lu son détail et choisi sa portée.
- [ ] J'ai vu le serveur de langage C# remonter une erreur sans build.
- [ ] J'ai packagé mon `.claude/` en plugin valide (`--strict`) et testé avec `--plugin-dir`.
- [ ] Je sais diffuser un plugin à une équipe via le `.claude/settings.json` du dépôt.
- [ ] Je sais ce qu'est un plugin « bundle » et à quoi sert `allowCrossMarketplaceDependenciesOn`.
- [ ] Je sais ce que j'exige avant d'autoriser un plugin tiers, et ce que la DSI peut imposer.

---

## 7. La limite suivante

Le [Lab 03](../../labs/lab-03-securite-secrets/) va compléter le toolkit avec la chaîne de
sécurité. Vous y lancerez une revue de sécurité de tout le diff, puis de tout le dépôt — et deux
problèmes surgiront :

1. **Le bruit** : la revue a lu trente fichiers ; votre session est saturée avant d'avoir corrigé quoi que ce soit.
2. **La complaisance** : le relecteur est le même agent qui a écrit le code ; il a vu tout le
   raisonnement et tend à le valider.

Au passage, regardez ce que contient `pr-review-toolkit` : **six agents**. Des relecteurs
spécialisés, avec leurs propres instructions et leurs propres outils.

> **→ [Lab 03](../../labs/lab-03-securite-secrets/)**, puis **[Module 07 — Sous-agents](../07-sous-agents/)** :
> déléguer à un relecteur indépendant, au contexte séparé, qui ne peut techniquement rien modifier.
