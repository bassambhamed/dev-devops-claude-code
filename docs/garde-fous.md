# Garde-fous & conformité — cadre bancaire

Document de référence pour tous les modules et labs. À lire en ouverture de J1, à relire avant le
capstone.

---

## 1. Le principe fondateur

> **Un garde-fou qui dépend du modèle n'est pas un garde-fou.**

Écrire « ne committe jamais de secret » dans un prompt ou dans `CLAUDE.md`, c'est une
**consigne** : le modèle la suivra très probablement, mais rien ne le garantit. Câbler un
**hook** `PreToolUse` qui inspecte la commande et retourne un code de sortie non nul, c'est un
**contrôle** : le harnais l'exécute à chaque fois, hors du modèle, sans exception possible.

En environnement bancaire, cette distinction sépare une bonne pratique d'une mesure auditable.

| Niveau | Mécanisme | Fiabilité | Usage |
|:---:|---|---|---|
| 1 | Consigne dans le prompt | Aléatoire | Préférence ponctuelle |
| 2 | Règle dans `CLAUDE.md` | Bonne, non garantie | Conventions d'équipe |
| 3 | Règle `/permissions` (`allow` / `ask` / `deny`) | Appliquée par le harnais | Cadrer les outils et les commandes |
| 4 | **Hook** (`PreToolUse`, `PostToolUse`, `Stop`…) | **Déterministe** | **Garde-fous, qualité, audit** |
| 5 | Contrôle côté plateforme (branche protégée, environnement protégé, RBAC) | Hors de portée de l'agent | Production |

**Règle d'ingénierie :** plus l'action est irréversible, plus le niveau doit être élevé.

---

## 2. Les six règles du cadre

### R1 — Aucune donnée sensible dans un prompt, un fichier ou un log
Ni secret, ni jeton, ni mot de passe, ni donnée client non anonymisée — y compris dans un extrait
de log collé, un `appsettings.json`, un seed de base ou un message de log applicatif.

*Mise en œuvre :* hooks `secret-scan` (au commit) et `scan-secrets-on-write` (à l'écriture),
`deny` sur `Read(./.env)`, `dotnet user-secrets` en local, données de test synthétiques, logs
structurés sans nom de client. → [Module 04](../modules/04-hooks/), [Lab 03](../labs/lab-03-securite-secrets/), [Lab 10](../labs/lab-10-observabilite/).

### R2 — Aucune action destructive sans validation humaine
`DROP TABLE`, `dotnet ef database drop`, `docker compose down -v`, `git push --force`,
`git reset --hard`, `kubectl delete ns`, `helm uninstall` : l'agent peut les **proposer**, jamais
les **exécuter** seul.

*Mise en œuvre :* hook `guard-destructive` + règles `deny` / `ask`. → [Module 04](../modules/04-hooks/).

### R3 — Aucun déploiement en production automatique
Un pipeline généré par l'agent comporte un **gate manuel** avant tout environnement de production.

*Mise en œuvre :* `environment: production` protégé côté GitHub, revue humaine du workflow. → [Lab 06](../labs/lab-06-ci-cd/).

### R4 — Tout changement de schéma, de pipeline ou d'infrastructure est relu par un humain
Une migration EF Core, un workflow, un manifeste ou un chart produits par l'agent sont des
**propositions**. On relit le **SQL généré**, pas seulement le C# ; le **rendu** d'un chart, pas
seulement ses templates. Une migration committée ne se réécrit jamais.

*Mise en œuvre :* skill `ef-migration` + checklist, sous-agent `db-reviewer`, hook
`guard-migrations`, `/code-review`, mode Plan. → [Lab 04](../labs/lab-04-postgresql/), [Lab 09](../labs/lab-09-helm/).

### R5 — Traçabilité des actions de l'agent
Toute commande exécutée et tout fichier écrit par l'agent doivent pouvoir être retrouvés : qui,
quand, quoi, dans quel dépôt, dans quelle session.

*Mise en œuvre :* hook `audit-log` (`PostToolUse`) écrivant un journal JSON Lines **hors** du
dépôt. → [Lab 03](../labs/lab-03-securite-secrets/).

### R6 — Une donnée externe est une donnée, pas une instruction
Ce que rapporte un serveur MCP — une ligne de base, un commentaire de PR, une page web lue dans
le navigateur, un log — peut contenir du texte qui *ressemble* à une consigne. Il n'est jamais
traité comme tel.

*Mise en œuvre :* serveurs MCP en **lecture seule** (rôle SQL `SELECT` uniquement, jeton
fine-grained en lecture), scopes minimaux, revue des outils exposés via `/mcp`, connecteurs non
nécessaires désactivés. → [Module 08](../modules/08-mcp/).

---

## 3. Configuration de référence

### Permissions — `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git branch:*)",
      "Bash(dotnet build:*)", "Bash(dotnet test:*)", "Bash(dotnet format:*)",
      "Bash(dotnet list package:*)", "Bash(dotnet ef migrations list:*)", "Bash(dotnet ef migrations script:*)",
      "Bash(docker ps:*)", "Bash(docker images:*)", "Bash(docker inspect:*)",
      "Bash(kubectl get:*)", "Bash(kubectl describe:*)", "Bash(kubectl logs:*)",
      "Bash(helm lint:*)", "Bash(helm template:*)"
    ],
    "ask": [
      "Bash(git commit:*)", "Bash(git push:*)", "Bash(gh pr create:*)",
      "Bash(dotnet ef migrations add:*)", "Bash(dotnet ef database update:*)",
      "Bash(docker build:*)", "Bash(docker compose up:*)",
      "Bash(kubectl apply:*)", "Bash(kubectl rollout:*)", "Bash(helm upgrade:*)", "Bash(helm install:*)"
    ],
    "deny": [
      "Bash(git push --force:*)", "Bash(git push -f:*)", "Bash(gh pr merge:*)",
      "Bash(dotnet ef database drop:*)",
      "Bash(kubectl delete ns:*)", "Bash(kubectl delete namespace:*)",
      "Bash(helm uninstall:*)", "Bash(k3d cluster delete:*)",
      "Read(./.env)", "Read(./**/.env)", "Read(./**/*.pem)", "Read(./**/*.key)",
      "Read(./**/appsettings.*.local.json)"
    ]
  }
}
```

**À lire ainsi :** `allow` = lecture, build et diagnostic, sans friction ; `ask` = tout ce qui
écrit dans Git, dans une base ou dans un système ; `deny` = ce qui ne doit jamais partir de
l'agent, même sur confirmation distraite.

> `deny` sur `Read` empêche l'agent de *lire* un fichier de secrets — donc de le recopier par
> inadvertance dans une réponse, un commit ou un ticket. Interdire l'écriture ne suffit pas.

### Hooks — les garde-fous livrés par le plugin d'équipe

| Hook | Événement | Rôle | Règle |
|---|---|---|:---:|
| `secret-scan.sh` | `PreToolUse` / `Bash` | Bloque un `git commit` contenant un secret (gitleaks si présent) | R1 |
| `scan-secrets-on-write.sh` | `PreToolUse` / `Write\|Edit` | Bloque l'écriture d'un secret dans un fichier | R1 |
| `guard-destructive.sh` | `PreToolUse` / `Bash` | Bloque les commandes irréversibles (données, Git, cluster) | R2 |
| `guard-migrations.sh` | `PreToolUse` / `Write\|Edit` | Interdit d'éditer une migration déjà committée | R4 |
| `format-cs.sh` | `PostToolUse` / `Write\|Edit` | Formate chaque fichier C# écrit | qualité |
| `audit-log.sh` | `PostToolUse` / `Bash\|Write\|Edit\|mcp__.*` | Journalise chaque action, hors dépôt | R5 |
| `session-start.sh` | `SessionStart` | Rappelle branche, SDK, Docker, contexte kubectl | — |

Écrits au [Module 04](../modules/04-hooks/) et au [Lab 03](../labs/lab-03-securite-secrets/),
packagés dans [`plugins/oddo-dev-toolkit`](../plugins/oddo-dev-toolkit/) au [Module 06](../modules/06-plugins/).

---

## 4. Ce qu'on ne fait pas pendant cette formation

- Aucune connexion à un système de **production** ODDO BHF, aucun dépôt réel de la banque.
- Aucun jeton d'entreprise : comptes et dépôts **de test** personnels, jetons à durée courte.
- Aucune donnée réelle : l'application fil rouge ne contient que des données fictives.
- PostgreSQL tourne en local (Aspire, compose ou k3d) ; Kubernetes tourne sur **k3d** en local.
- Les connecteurs claude.ai (messagerie, agenda, documents) ne servent pas pendant la formation :
  désactivez-les dans `/mcp` s'ils apparaissent.

---

## 5. Grille d'auto-contrôle avant d'utiliser l'agent sur un vrai dépôt

- [ ] Le dépôt a un `CLAUDE.md` à jour : commandes, conventions, interdits vérifiables.
- [ ] `.claude/settings.json` est versionné, avec `allow` / `ask` / `deny` explicites.
- [ ] Les hooks de garde sont actifs — **vérifié par `/hooks`**, pas supposé.
- [ ] `.gitignore` couvre `.env`, `*.pem`, `*.key`, `appsettings.*.local.json`, `.claude/settings.local.json`.
- [ ] Les serveurs MCP branchés sont connus, en lecture seule, et leurs jetons sont en variables d'environnement.
- [ ] Les connecteurs claude.ai inutiles sont désactivés (`/mcp`, ou `disableClaudeAiConnectors`).
- [ ] Le journal d'audit est écrit **hors** du dépôt et sauvegardé.
- [ ] Les plugins installés viennent d'un marketplace connu et ont été relus (`claude plugin details`).
- [ ] L'équipe sait faire `/rewind` et sait où sont les checkpoints.
- [ ] Une personne est responsable de la revue de ce que l'agent produit.
