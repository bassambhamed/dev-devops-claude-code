# Pré-requis techniques

À installer **avant J1**. Comptez une heure si tout est à installer, quinze minutes si Docker et
le SDK .NET sont déjà là. Vérification automatique : `./docs/check-prereqs.sh`.

> **Poste verrouillé ?** Anticipez : Docker, le SDK .NET et `gh` passent souvent par le catalogue
> logiciel interne. Faites la demande **une semaine avant** la session.

---

## 1. Claude Code — indispensable

| Plateforme | Commande |
|---|---|
| macOS / Linux / WSL | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Windows (PowerShell) | `irm https://claude.ai/install.ps1 \| iex` |
| macOS (Homebrew) | `brew install --cask claude-code` |
| Windows (WinGet) | `winget install Anthropic.ClaudeCode` |

```bash
claude --version     # ≥ 2.1 attendu
claude doctor
```

**Compte requis :** abonnement **Pro, Max, Team, Enterprise** ou **Console**. Le navigateur
connecté (Claude in Chrome, labs 05 et 10) demande un compte claude.ai — pas une simple clé d'API.

**IDE (recommandé) :** extension Claude Code pour **VS Code** ou plugin **JetBrains** (Rider).
Une fois connecté (`/ide`), l'agent lit les diagnostics de l'éditeur via le serveur MCP intégré `ide`.

---

## 2. Outillage par jour

| Outil | Sert à | Labs | Vérification |
|---|---|:---:|---|
| Git + GitHub CLI (`gh`) | dépôts, PR, Actions | 01, 06 | `gh auth status` |
| **.NET SDK 10** | builder et tester l'app | tous | `dotnet --version` |
| `dotnet-ef` | migrations EF Core | 04 | `dotnet ef --version` |
| **Docker** (Desktop ou moteur) | PostgreSQL via Aspire, Testcontainers, images | 04 → 11 | `docker info` |
| Node.js ≥ 20 (`npx`) | serveurs MCP DBHub, Playwright | 04, 05 | `npx --version` |
| `jq` | hooks | 02 → 04 | `jq --version` |
| `gitleaks` | détection de secrets | 03 | `gitleaks version` |
| `trivy` | scan d'images et de configuration | 03, 07 | `trivy --version` |
| `kubectl` + `k3d` | cluster local | 08 → 11 | `kubectl version --client` · `k3d version` |
| `helm` | packaging | 09, 10 | `helm version` |
| Aspire CLI | serveur MCP Aspire (observabilité) | 10, 11 | `aspire --version` |
| `csharp-ls` | serveur de langage du plugin `csharp-lsp` | 06 → | `csharp-ls --version` |
| Google Chrome ou Edge + extension *Claude in Chrome* | vérifier l'interface | 05 | `/chrome` dans une session |

### Installation express — macOS

```bash
brew install git gh dotnet-sdk jq gitleaks trivy kubectl helm k3d node
brew install --cask docker
dotnet tool install --global dotnet-ef
dotnet tool install --global csharp-ls
curl -sSL https://aspire.dev/install.sh | bash
```

### Installation express — Windows (PowerShell)

```powershell
winget install Git.Git GitHub.cli Microsoft.DotNet.SDK.10 jqlang.jq Gitleaks.Gitleaks `
  AquaSecurity.Trivy Kubernetes.kubectl Helm.Helm k3d.k3d OpenJS.NodeJS.LTS Docker.DockerDesktop
dotnet tool install --global dotnet-ef
dotnet tool install --global csharp-ls
irm https://aspire.dev/install.ps1 | iex
```

> Les outils globaux .NET s'installent dans `~/.dotnet/tools` : ajoutez ce dossier au `PATH`
> s'ils sont introuvables (`export PATH="$PATH:$HOME/.dotnet/tools"`).

---

## 3. Vérifier d'un coup

```bash
./docs/check-prereqs.sh
```

Une ligne par outil — `OK` (présent), `MANQ` (indispensable manquant) ou `ABS` (optionnel absent) —
et rien n'est installé. Un outil `ABS` ne bloque pas la formation : les labs concernés se suivent en
observation. Le script sort en erreur (code 1) tant qu'un outil `MANQ` subsiste.

---

## 4. Comptes et accès à préparer

| Accès | Pourquoi | Labs |
|---|---|:---:|
| Compte GitHub **personnel ou de test** | dépôt, PR, Actions | 01, 06 |
| Jeton GitHub *fine-grained*, lecture seule, 7 jours (créé au module 08) | serveur MCP GitHub | 08, 06 |
| Extension *Claude in Chrome* connectée au **même** compte que Claude Code | lab frontend | 05 |

> **Règle absolue :** ces jetons vont dans des **variables d'environnement** ou dans le trousseau
> (via `userConfig` d'un plugin), jamais dans un fichier committé, jamais dans un prompt.

---

## 5. Application fil rouge

```bash
export PATH="/usr/local/share/dotnet:$PATH"    # si dotnet n'est pas trouvé
cd ecommerce-app
dotnet restore ECommerce.slnx
dotnet build ECommerce.slnx
dotnet dev-certs https --trust                 # une seule fois, sinon dashboard en UntrustedRoot
dotnet run --project src/ECommerce.AppHost     # URL du dashboard + jeton affichés en console
```

Si le build passe et que le dashboard Aspire s'ouvre, votre poste est prêt.
