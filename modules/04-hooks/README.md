# Module 04 — Hooks

> **Durée :** 50 min · **Pré-requis :** [Module 03](../03-commandes-personnalisees/) et
> [Lab 01](../../labs/lab-01-git-github/) · **Suivant :** [Module 05 — Skills](../05-skills/)

---

## 1. La limite — d'où l'on vient

Au [Lab 01](../../labs/lab-01-git-github/), `/ship` a structuré la livraison. Mais l'étape 6 du lab
l'a montré : un mot de passe glissé dans `appsettings.Development.json` peut partir dans un
commit. `/ship` *demande* une vérification ; rien ne l'*impose*.

| Ce qui reste fragile | Pourquoi une commande ne suffit pas |
|---|---|
| **Un secret committé** (Dev) | Le modèle peut mal juger une ligne ; un collègue committe sans `/ship` |
| **Un fichier mal formaté** (Dev) | Le formatage n'arrive que si quelqu'un pense à le demander |
| **`docker compose down -v`** (DevOps) | La base locale d'un collègue disparaît ; aucune commande ne l'en empêche |
| **La traçabilité** (DORA) | Personne ne « pense » à journaliser chaque commande |

Vous avez une **consigne**. Il vous faut un **contrôle**. En environnement bancaire, cette nuance
décide de ce qui est auditable.

## 2. Le concept — le harnais exécute, le modèle n'est pas consulté

Un **hook** est un script lancé automatiquement par le harnais sur un **événement**. Le modèle
n'intervient pas : il ne peut ni le contourner, ni l'oublier, ni le « juger inutile cette fois ».

```
  L'agent veut lancer :  git commit -m "feat: add db config"
                                   │
                                   ▼
              ┌─────────── hook PreToolUse (Bash) ───────────┐
              │  votre script reçoit l'appel en JSON sur     │
              │  stdin, inspecte le diff indexé, décide      │
              └────────────┬──────────────────────┬──────────┘
                    exit 0 │                      │ exit 2
                           ▼                      ▼
                  la commande part        BLOQUÉE — le message stderr
                                          est renvoyé à l'agent, qui
                                          propose de sortir le secret
```

| | Commande (module 03) | `CLAUDE.md` (module 02) | **Hook** |
|---|---|---|---|
| Qui décide de l'appliquer | Vous, en tapant `/nom` | Le modèle | **Le harnais, sur événement** |
| S'applique si on l'oublie | Non | Pas forcément | **Oui** |
| Peut bloquer une action | Non | Non | **Oui** |
| Peut exécuter du code | Non | Non | **Oui** (n'importe quel script) |

### Permissions ou hook ?

`/permissions` filtre un outil ou une commande par motif (`deny` sur `Bash(git push --force:*)`).
Un hook **raisonne** : il lit la commande, inspecte le dépôt, appelle `gitleaks`, écrit un
journal, puis décide. Règle simple : **un motif suffit → permission ; il faut regarder le
contexte → hook.**

## 3. Anatomie

### 3.1 Les événements, et leur usage Dev & DevOps

| Événement | Quand | Peut bloquer ? | Usage Dev | Usage DevOps |
|---|---|:---:|---|---|
| `PreToolUse` | **Avant** un outil | Oui | Refuser un commit avec secret ; interdire d'éditer une migration committée | Refuser `kubectl delete ns`, `docker compose down -v` |
| `PostToolUse` | **Après** un outil | Non (renvoie un message à l'agent) | Formater le `.cs` qui vient d'être écrit | Journal d'audit, scan d'image après `docker build` |
| `Stop` | L'agent veut conclure | Oui (il reprend la main) | Refuser de conclure si les tests sont rouges | Refuser de conclure si le chart ne passe pas `helm lint` |
| `SessionStart` | Ouverture de session | Non | Rappeler la branche, signaler `main` | Rappeler le contexte kubectl courant |
| `UserPromptSubmit` | À chaque prompt | Oui | Refuser un prompt contenant une clé collée | — |
| `Notification` | L'agent attend une action | Non | Notification de bureau | — |

### 3.2 Le contrat d'un hook

- **Entrée :** l'événement en **JSON sur stdin** — `session_id`, `cwd`, `hook_event_name`,
  `tool_name`, `tool_input` (la commande, le chemin du fichier, le contenu écrit…).
- **Sortie :** le **code de retour** décide.

| Code | Effet |
|:---:|---|
| `0` | On laisse passer. (Pour `SessionStart`, ce que le script écrit sur stdout est ajouté au contexte.) |
| `2` | **Bloqué.** Ce qui est écrit sur `stderr` est renvoyé à l'agent : expliquez-lui quoi faire à la place. |
| autre | Erreur non bloquante, affichée à l'utilisateur. |

Pour aller plus loin, un hook peut écrire un JSON sur stdout pour demander une **confirmation**
au lieu de bloquer (`"permissionDecision": "ask"`), ou pour ajouter du contexte à l'agent.

### 3.3 Le câblage — `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/guard-destructive.sh" },
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/secret-scan.sh" }
      ]}
    ],
    "PostToolUse": [
      { "matcher": "Write|Edit|MultiEdit", "hooks": [
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format-cs.sh", "timeout": 60 }
      ]}
    ]
  }
}
```

- `matcher` : une expression sur le **nom de l'outil** (`Bash`, `Write|Edit`, `mcp__.*`). Sensible à la casse.
- `$CLAUDE_PROJECT_DIR` : la racine du projet, quel que soit le dossier courant de l'agent.
- `timeout` en secondes : un hook lent ralentit **chaque** action concernée.

Les hooks se déclarent aussi au niveau utilisateur (`~/.claude/settings.json`), dans un plugin
(`hooks/hooks.json`, [module 06](../06-plugins/)) ou dans le frontmatter d'un skill ou d'un
sous-agent. `/hooks` montre ce qui est **réellement** actif, d'où que ça vienne.

### 3.4 Un hook de garde complet

`.claude/hooks/guard-destructive.sh` (version complète dans
[`plugins/oddo-dev-toolkit/hooks/`](../../plugins/oddo-dev-toolkit/hooks/guard-destructive.sh)) :

```bash
#!/usr/bin/env bash
# Hook PreToolUse (Bash) — bloque les commandes irréversibles.
set -uo pipefail

cmd="$(jq -r '.tool_input.command // empty' 2>/dev/null)" || exit 0
[ -z "$cmd" ] && exit 0

DATA='DROP (TABLE|DATABASE|SCHEMA)|dotnet ef database drop|docker (volume rm|system prune)|docker compose down .*(-v|--volumes)'
INFRA='kubectl delete (ns|namespace|pvc)|k3d cluster delete|helm uninstall'
GIT='git push .*(-f|--force)|git reset --hard|git clean -[a-z]*f'

if printf '%s' "$cmd" | grep -qiE "$DATA|$INFRA|$GIT"; then
  {
    echo "BLOQUÉ par le hook guard-destructive : $cmd"
    echo "Commande irréversible. Présente l'impact et l'alternative réversible ;"
    echo "l'humain la lancera lui-même s'il la valide."
  } >&2
  exit 2
fi
exit 0
```

**Pourquoi `jq` plutôt qu'un `grep` sur le JSON brut :** un parsing approximatif rate une
commande échappée ou sur plusieurs lignes. Un garde-fou qui rate une fois sur vingt n'en est pas un.

---

## 4. Mini-lab — trois hooks, trois rôles (25 min)

On travaille dans le dépôt initialisé au Lab 01.

```bash
cd ~/lab-ecommerce
mkdir -p .claude/hooks
```

**1. Bloquer — `guard-destructive.sh`.** Recopiez le script du §3.4.

**2. Bloquer selon le contexte — `secret-scan.sh`.** Faites-le écrire, puis comparez avec la
[version de référence](../../plugins/oddo-dev-toolkit/hooks/secret-scan.sh) :

```text
> Écris .claude/hooks/secret-scan.sh : un hook PreToolUse sur Bash qui, si la commande contient
  "git commit", analyse le diff indexé (gitleaks protect --staged si gitleaks est installé,
  sinon des motifs password/secret/token/connectionstring), et bloque avec exit 2 en
  expliquant sur stderr comment sortir le secret du code. Lis le JSON avec jq.
```

**3. Agir après coup — `format-cs.sh`.** Un `PostToolUse` qui formate le fichier C# écrit :

```bash
cp "$FORMATION/plugins/oddo-dev-toolkit/hooks/format-cs.sh" .claude/hooks/
```

Lisez-le : il ne bloque jamais (`exit 0`), il ne traite que les `.cs`, et il passe à
`dotnet format` un chemin **relatif** (un chemin absolu est ignoré sans erreur — piège vérifié).

**4. Câbler et vérifier**

```bash
chmod +x .claude/hooks/*.sh
```

Créez `.claude/settings.json` (§3.3), relancez `claude`, puis :

```text
> /hooks
```

Les trois doivent apparaître. **`/hooks` est la seule preuve** : un hook mal câblé ne produit
aucune erreur, il ne se déclenche jamais.

**5. Tester le blocage destructif**

```text
> Repars d'une base propre : supprime les volumes Docker du projet avec docker compose down -v
```

Vous voyez le refus, et l'agent reçoit votre explication.

**6. Tester l'anti-secret**

```bash
cat > src/ECommerce.Catalog.Api/appsettings.Local.json <<'EOF'
{ "ConnectionStrings": { "catalogdb": "Host=db;Username=app;Password=Sup3rS3cret!" } }
EOF
git add -f src/ECommerce.Catalog.Api/appsettings.Local.json
```
```text
> Commite ce fichier de configuration
```

Refus attendu. Nettoyez : `git reset src/ECommerce.Catalog.Api/appsettings.Local.json && rm src/ECommerce.Catalog.Api/appsettings.Local.json`

**7. Tester le formatage**

```text
> Dans CatalogEndpoints.cs, ajoute un commentaire au-dessus du MapGet("/") — et volontairement,
  indente la ligne suivante avec 13 espaces.
```

Relisez le fichier : l'indentation a été corrigée par le hook, pas par le modèle.

> **Le hook se teste aussi sans Claude :**
> `echo '{"tool_input":{"command":"git push --force"}}' | .claude/hooks/guard-destructive.sh; echo $?`
> → `2`. Un hook est un script : il se teste comme un script.

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| Script non exécutable | Hook ignoré en silence | `chmod +x` |
| `matcher` erroné (`bash` au lieu de `Bash`) | Ne se déclenche jamais | Vérifier dans `/hooks` |
| `exit 1` pour bloquer | Erreur affichée, action **non bloquée** | `exit 2` + motif sur `stderr` |
| Parser le JSON avec `grep` | Faux négatifs sur commandes échappées | `jq` |
| Message d'erreur sans mode d'emploi | L'agent réessaie la même chose | Dire sur `stderr` quoi faire à la place |
| Hook lent sur chaque `Edit` | Toute la session traîne | Filtrer tôt (`*.cs` seulement), `timeout` |
| Chemin absolu passé à `dotnet format --include` | Fichier ignoré sans erreur | Chemin relatif à la racine |

---

## 6. Checklist de sortie

- [ ] Mes trois hooks sont écrits, exécutables, câblés et **visibles dans `/hooks`**.
- [ ] J'ai vu un blocage réel et lu le message reçu par l'agent.
- [ ] J'ai vu un `PostToolUse` corriger un fichier sans intervention du modèle.
- [ ] Je sais tester un hook en lui passant un JSON sur stdin.
- [ ] Je sais dire quand une permission suffit et quand il faut un hook.

---

## 7. La limite suivante

Les hooks savent **dire non** et **corriger la forme**. Ils ne savent pas **faire**. Demandez :

> *« Ajoute un SKU unique aux produits. »*

Il faut modifier le modèle, `OnModelCreating`, générer une migration, **relire le SQL** produit,
l'appliquer, adapter le seed et les tests : huit étapes, une checklist de revue, des pièges
connus. C'est une procédure qui demande du **jugement** — exactement ce qu'un script ne sait pas
faire, et ce qu'un prompt de vingt lignes fait mal.

> **→ [Module 05 — Skills](../05-skills/) :** capitaliser une procédure, avec ses fichiers
> d'appui, que l'agent mobilise de lui-même quand la situation s'y prête.
