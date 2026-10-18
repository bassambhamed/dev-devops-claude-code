# Lab 03 — Sécurité & secrets (DevSecOps)

> **Durée :** 60 min · **Modules requis :** [04](../../modules/04-hooks/), [06](../../modules/06-plugins/)
> · **Outils :** `gitleaks`, `trivy`, `dotnet` · **Corrigé :** [`solution/`](solution/)

---

## 1. Objectif

Construire la **chaîne de sécurité complète** du poste et de la CI — permissions, secrets,
dépendances vulnérables, journal d'audit, contrôle bloquant en CI — puis la **distribuer** à toute
l'équipe par le plugin. À la fin, la sécurité n'est plus une vigilance individuelle : c'est une
configuration qui s'applique par défaut.

C'est le lab qui rend acceptables, en environnement bancaire, ceux qui suivent : base de données,
conteneurs, cluster.

## 2. Pré-requis

```bash
gitleaks version       # brew install gitleaks
trivy --version
```

[Lab 02](../lab-02-tests/) terminé ; le marketplace de la formation ajouté au [module 06](../../modules/06-plugins/).

## 3. Briques mobilisées — et pourquoi chacune

| Brique | Rôle | Pourquoi celle-ci |
|---|---|---|
| **`/permissions`** | `allow` / `ask` / `deny`, y compris la **lecture** des secrets | Un motif suffit : pas besoin d'un hook |
| **Hooks** `scan-secrets-on-write`, `secret-scan` (gitleaks), `audit-log` | Bloquer un secret à l'écriture **et** au commit ; tracer | Il faut regarder le contenu et le contexte : un motif ne suffit pas |
| **`/security-review`** | Revue de sécurité du diff | Un regard générique, en complément de vos règles |
| **Plugin officiel** `security-guidance` | Avertissements à l'édition, revue du diff en fin de tâche | Ne pas réécrire ce qu'un éditeur maintient |
| **Plugin d'équipe** (`mon-toolkit`, puis le bundle `oddo-dev-standard`) | Distribuer la chaîne | Le seul moyen d'avoir **les mêmes** garde-fous partout |
| **CI** (`security.yml`) | Le contrôle bloquant de dernier recours | Le niveau 5 des [garde-fous](../../docs/garde-fous.md) : hors de portée de l'agent |

---

## 4. Déroulé pas-à-pas

### Étape 1 — Les permissions, lecture comprise (10 min)

```bash
cd ~/lab-ecommerce && git switch -c chore/security-chain && claude
```
```text
> /permissions
```

Mettez en place la configuration de référence des [garde-fous, §3](../../docs/garde-fous.md#3-configuration-de-référence) :
lecture, build et tests en `allow` ; écriture Git et dépendances en `ask` ; l'irréversible et la
**lecture des secrets** en `deny`. Testez les trois niveaux :

```text
> Lance dotnet test                                   → passe sans question
> Ajoute le paquet Polly au projet Catalog            → demande confirmation
> Lis le fichier .env et résume-le                    → refusé
```

> Le `deny` sur `Read(./.env)` empêche l'agent de **lire** un fichier de secrets, donc de le
> recopier dans une réponse, un commit ou un ticket. Interdire l'écriture ne suffit pas.

### Étape 2 — Le bon endroit pour un secret de développement (5 min)

```text
> Comment configurer en local la chaîne de connexion de Catalog sans jamais l'écrire dans un
  fichier du dépôt ?
```

Réponse attendue : `dotnet user-secrets` (stocké hors du dépôt, dans le profil utilisateur) ou une
variable d'environnement. Faites-le vous-même :

```bash
cd src/ECommerce.Catalog.Api
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:catalogdb" "Host=localhost;Username=dev;Password=valeur-locale"
dotnet user-secrets list
cd ../..
```

### Étape 3 — Bloquer un secret avant qu'il touche le disque (10 min)

Le hook du module 04 bloquait le **commit**. Celui-ci bloque l'**écriture** :

```bash
cp "$FORMATION/plugins/oddo-dev-toolkit/hooks/scan-secrets-on-write.sh" .claude/hooks/
chmod +x .claude/hooks/scan-secrets-on-write.sh
```

Câblez-le en `PreToolUse`, matcher `Write|Edit|MultiEdit` (modèle :
[`settings.before-plugin.json`](solution/.claude/settings.before-plugin.json)). Puis :

```text
> Ajoute dans appsettings.Development.json de Catalog la chaîne
  Host=db;Username=app;Password=Sup3rS3cret! pour la base locale.
```

**L'écriture est refusée** et l'agent reçoit la marche à suivre (user-secrets). Comparez avec
l'étape 6 du Lab 01 : même erreur, cette fois **impossible**.

### Étape 4 — gitleaks au commit (5 min)

Avec `gitleaks` installé, le hook `secret-scan` l'utilise automatiquement. Testez avec un fichier
créé **par vous** (le hook d'écriture bloquerait l'agent) :

```bash
echo 'AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' > .env.test
git add -f .env.test
```
```text
> Commite ce fichier
```

Refus attendu. Nettoyez : `git reset .env.test && rm .env.test`.

### Étape 5 — Les dépendances vulnérables : de vrais résultats (10 min)

L'application contient **réellement** des dépendances vulnérables (vues au module 00 : les
avertissements `NU1903`).

```bash
dotnet list ECommerce.slnx package --vulnerable --include-transitive
```

Deux paquets transitifs ressortent en *High* : `Microsoft.OpenApi 2.0.0` (Catalog, Ordering) et
`MessagePack 2.5.192` (AppHost).

```text
> /security-review
> Pour chaque dépendance vulnérable : quel service l'embarque, est-elle atteinte à l'exécution
  (l'OpenAPI n'est mappé qu'en Development, l'AppHost ne tourne qu'en local), et quelle est la
  montée de version MINIMALE qui corrige ? Applique-la, puis vérifie avec dotnet list package.
```

Correctif attendu (vérifié) : référence directe à `Microsoft.OpenApi` **2.7.5** dans Catalog et
Ordering, à `MessagePack` **2.5.301** dans l'AppHost. Après correction : plus aucun paquet
vulnérable, plus aucun avertissement de build.

> **Le travail que l'agent fait bien ici** n'est pas de trouver les vulnérabilités — le scanner
> le fait. C'est de **qualifier** : exploitable ici, ou théorique ? Et de proposer le correctif
> minimal, pas une montée de version majeure.

### Étape 6 — Le journal d'audit (5 min)

```bash
cp "$FORMATION/plugins/oddo-dev-toolkit/hooks/audit-log.sh" .claude/hooks/ && chmod +x .claude/hooks/audit-log.sh
```

Câblez-le en `PostToolUse` (matcher `Bash|Write|Edit|MultiEdit|mcp__.*`), faites travailler
l'agent quelques minutes, puis :

```bash
tail -5 ~/.claude/audit/$(date -u +%F).jsonl | jq .
```
```text
> À partir de ~/.claude/audit/, combien d'actions l'agent a-t-il faites aujourd'hui, dans quels
  dépôts, et lesquelles ont écrit des fichiers ?
```

C'est la pièce qu'un auditeur DORA demandera : qui, quand, quoi, où, dans quelle session.

### Étape 7 — Le contrôle bloquant en CI (5 min)

```bash
mkdir -p .github/workflows
cp "$FORMATION/labs/lab-03-securite-secrets/solution/.github/workflows/security.yml" .github/workflows/
cp "$FORMATION/labs/lab-03-securite-secrets/solution/.gitleaks.toml" .
```
```text
> Relis @.github/workflows/security.yml : quels contrôles bloquent la PR, avec quelles
  permissions, et qu'est-ce qui empêcherait un fork d'exfiltrer un secret ?
```

### Étape 8 — Distribuer : du `.claude/` au poste standard (10 min)

Votre chaîne vit dans **ce** dépôt. Deux façons de la distribuer :

- **(a) Faire évoluer votre plugin** du module 06 : copiez les nouveaux hooks dans
  `~/mon-marketplace/mon-toolkit/hooks/`, câblez-les dans `hooks.json`, passez la version à
  `0.2.0`, puis `claude plugin update mon-toolkit@mon-marketplace`. Une correction = un commit
  **et** une version.
- **(b) Adopter le poste standard de référence** — recommandé pour la suite : il contient
  exactement ces hooks, les skills des labs suivants et six sous-agents de revue.

```bash
claude plugin uninstall mon-toolkit@mon-marketplace --scope project
claude plugin install oddo-dev-standard@oddo-dev-marketplace --scope project
claude plugin list        # oddo-dev-standard + 4 dépendances : oddo-dev-toolkit, csharp-lsp, context7, security-guidance
```

Puis **retirez du projet** les hooks désormais portés par le plugin — sinon ils s'exécutent deux
fois. Seul le hook `Stop` (choix propre à ce dépôt) reste local. Version finale :
[`solution/.claude/settings.json`](solution/.claude/settings.json).

```bash
claude
```
```text
> /hooks
```

Chaque hook apparaît **une** fois, avec sa source (plugin ou projet). Ouvrez une session dans un
dépôt **quelconque** où le plugin est installé : vos garde-fous vous y suivent.

---

## 5. Livrable

```
.claude/settings.json            # permissions + plugins d'équipe + hook Stop local
.github/workflows/security.yml   # gitleaks, dépendances vulnérables, trivy fs — bloquant
.gitleaks.toml                   # règles .NET / Npgsql
src/*/…csproj                    # dépendances corrigées
(poste) dotnet user-secrets      # la chaîne de connexion locale, hors dépôt
```

## 6. Garde-fous — contrôle final

- [ ] Un secret ne peut être ni **écrit** dans un fichier, ni **committé** — testé réellement.
- [ ] `deny` couvre la **lecture** de `.env`, `*.pem`, `*.key`.
- [ ] Les secrets de développement sont dans `dotnet user-secrets`, pas dans `appsettings`.
- [ ] Aucune dépendance vulnérable *High* ou *Critical*.
- [ ] Le journal d'audit est écrit hors du dépôt.
- [ ] La CI échoue sur un secret, une dépendance vulnérable ou une configuration critique.
- [ ] La chaîne est distribuée par le plugin ; aucun hook n'est exécuté deux fois.

## 7. Pour aller plus loin

- Testez les plugins officiels `semgrep` ou `sonarqube` et comparez leurs constats à `/security-review`.
- Ajoutez au hook `scan-secrets-on-write` un motif pour les chaînes de connexion Oracle ou SQL Server.
- Planifiez un rapport hebdomadaire des dépendances en headless ([annexe, §3.5](../../modules/annexe-agent-sans-terminal/)).
- Ajoutez `strictKnownMarketplaces` à un fichier de *managed settings* de test et constatez le refus d'un marketplace inconnu.

## 8. La limite révélée

Relancez `/security-review` sur **tout le dépôt**, puis `/context`. La revue a lu des dizaines de
fichiers et la sortie de `dotnet list package` : la session est saturée avant la première
correction. Et le relecteur est l'agent qui a écrit la moitié de ce code — il en connaît les
intentions, et tend à les valider.

> **→ [Module 07 — Sous-agents](../../modules/07-sous-agents/) :** un relecteur de sécurité
> indépendant, au contexte séparé, qui ne peut techniquement rien modifier.

## Corrigé

```bash
cp -r "$FORMATION/labs/lab-03-securite-secrets/solution/.github" ~/lab-ecommerce/
cp "$FORMATION/labs/lab-03-securite-secrets/solution/.gitleaks.toml" ~/lab-ecommerce/
cp "$FORMATION/labs/lab-03-securite-secrets/solution/.claude/hooks/"*.sh ~/lab-ecommerce/.claude/hooks/
# Dépendances corrigées (état d'avant le lab 04) :
for p in Catalog.Api Ordering.Api AppHost; do
  cp "$FORMATION/labs/lab-03-securite-secrets/solution/src/ECommerce.$p/ECommerce.$p.csproj" ~/lab-ecommerce/src/ECommerce.$p/
done
```

`settings.before-plugin.json` montre la configuration avant packaging ; `settings.json` la
configuration finale, une fois le plugin installé.
