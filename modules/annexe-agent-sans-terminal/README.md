# Annexe — L'agent sans terminal : headless, `/loop` et CI

> **Durée :** 40 min · **Hors de la chaîne des briques** · **Pré-requis :** [Module 08](../08-mcp/),
> [Labs 04](../../labs/lab-04-postgresql/) et [05](../../labs/lab-05-frontend/)
> · **Suivant :** [Lab 06 — CI/CD](../../labs/lab-06-ci-cd/)

> **Pourquoi une annexe, et pas un module 09 ?** Les modules 00 à 08 enseignent les **briques** de
> Claude Code — ce qu'on configure pour outiller l'agent : mémoire, commandes, hooks, skills,
> plugins, sous-agents, MCP. Cette annexe n'en ajoute aucune. Elle montre un autre **mode
> d'exécution** du même agent, avec les mêmes briques, au même titre que l'IDE ou l'application de
> bureau ([module 00](../00-prise-en-main/)). La CI, elle, n'est pas une fonctionnalité de Claude
> Code : c'est un **cas d'usage**, traité au [Lab 06](../../labs/lab-06-ci-cd/).

---

## 1. Le besoin — d'où l'on vient

Commandes, hooks, skills, plugins, sous-agents, MCP : tout ce que vous avez construit suppose
**quelqu'un devant un terminal**. Or les besoins les plus répétitifs arrivent quand personne ne
regarde :

| Moment | Cas d'usage Dev | Cas d'usage DevOps |
|---|---|---|
| Une PR est ouverte à 23 h | Une première revue (contrats, tests, sécurité) est prête le matin | Le SQL de chaque migration est généré et commenté sur la PR |
| Pendant que vous travaillez | Surveiller que la suite de tests reste verte pendant un refactoring | Suivre un rollout ou une CI sans rafraîchir l'onglet |
| Chaque lundi | — | Rapport des dépendances NuGet vulnérables, qualifié par criticité réelle |

## 2. Le concept — l'agent comme commande Unix

```bash
claude -p "ta consigne"
```

En mode **headless** (`-p`, *print*), Claude Code se comporte comme n'importe quel outil en ligne
de commande : une entrée, une action, une sortie sur `stdout`, puis il rend la main. Il
s'enchaîne donc avec un pipe, un `cron`, un `Makefile` ou un job de CI.

```bash
git diff main...HEAD -- '**/Migrations/**' | claude -p "Résume les opérations destructives de ce diff" > revue.md
```

**Le renversement :** jusqu'ici vous pilotiez l'agent. Désormais, **vos systèmes** le pilotent.

### Les trois degrés d'automatisation

| Degré | Mécanisme | L'agent… | Risque |
|:---:|---|---|---|
| 1 | `/loop` en session | observe et rapporte pendant que vous travaillez | Nul |
| 2 | `claude -p` dans un script ou un job CI | analyse et **produit un artefact** (rapport, commentaire) | Maîtrisé |
| 3 | Un agent qui **modifie** un système sans revue | corrige, merge, déploie | **Hors cadre de cette formation** |

Le degré 3 est exclu par la règle R2 des [garde-fous](../../docs/garde-fous.md). En production
bancaire, un agent autonome sur des systèmes réels relève d'une gouvernance qui dépasse le choix
d'un outil.

## 3. Anatomie

### 3.1 `/loop` — surveiller pendant qu'on travaille

```text
> /loop 3m Lance dotnet test ECommerce.slnx et signale tout test qui passe au rouge depuis
  l'itération précédente. Ne corrige rien.
```

Sans intervalle, l'agent choisit son rythme selon ce qu'il attend (une CI, un rollout). **Une
boucle se formule toujours en lecture seule** : « signale », jamais « corrige ».

### 3.2 Le mode headless — les options qui comptent

```bash
claude -p "Relis ce diff de migration" \
  --output-format json \
  --allowedTools "Read,Grep,Glob" \
  --permission-mode plan \
  --max-turns 10
```

| Option | Rôle | Pourquoi c'est important en CI |
|---|---|---|
| `-p` | Mode non interactif | Sans lui, le job attend un humain, puis expire |
| `--output-format json` | Sortie structurée (`.result`, coût, durée) | Exploitable par `jq` dans la suite du pipeline |
| `--allowedTools` | **Liste blanche d'outils** | Un job de revue n'a aucune raison d'écrire |
| `--permission-mode` | Comportement face aux permissions | Personne ne peut répondre « oui » |
| `--max-turns` | Plafond d'itérations | Borne le coût et la durée d'un job |

> **La règle d'or de la CI :** en non interactif, **aucune demande de permission ne peut être
> satisfaite**. Donnez une liste blanche restrictive — ne désactivez jamais les garde-fous pour
> « faire passer » un job.

### 3.3 Ce qui se charge en headless

| Élément | En `claude -p` |
|---|---|
| `CLAUDE.md`, `.claude/settings.json` (permissions, hooks) | Chargés — **vos hooks protègent aussi la CI** |
| Plugins déjà installés, `enabledPlugins` du dépôt | Chargés (`CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1` pour attendre leur installation) |
| `/plugin` et toute commande interactive | Indisponibles |
| Serveurs MCP d'un `.mcp.json` | Chargés **sans** demande d'approbation — à garder en tête |

### 3.4 Dans GitHub Actions

Deux voies, de la plus simple à la plus maîtrisée :

| Voie | Mise en place | Pour |
|---|---|---|
| **Application GitHub de Claude** | `/install-github-app` dans une session : installe l'application et un workflow ; on mentionne `@claude` dans une PR ou une issue | Une équipe qui veut une revue à la demande |
| **`claude -p` dans un job** | Un job écrit à la main, avec ses permissions et sa liste blanche | Un contrôle précis et auditable — l'option de ce module |

Le job de revue des migrations du [Lab 06](../../labs/lab-06-ci-cd/) :

```yaml
name: Revue assistée des migrations
on:
  pull_request:
    paths: ['src/**/Migrations/**']

permissions:
  contents: read
  pull-requests: write

jobs:
  migration-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '10.0.x' }

      - name: Générer le SQL des migrations (sans base : aucune connexion nécessaire)
        run: |
          dotnet tool install --global dotnet-ef
          dotnet ef migrations script --idempotent \
            --project src/ECommerce.Catalog.Api -o migration.sql

      - name: Installer Claude Code
        run: curl -fsSL https://claude.ai/install.sh | bash

      - name: Relire le SQL
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p "Relis migration.sql comme un DBA avant une mise en production : opérations
            destructives, conversions avec perte, NOT NULL sur table non vide, index manquants.
            Rends un tableau Markdown puis un verdict SÛRE / À REVOIR / BLOQUANTE.
            N'invente aucune instruction absente du fichier." \
            --allowedTools "Read" --max-turns 5 > review.md

      - name: Publier en commentaire
        run: gh pr comment ${{ github.event.pull_request.number }} --body-file review.md
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Ce que fait ce job — et ce qu'il ne fait pas.** Il produit un **commentaire**. Il n'applique
aucune migration, ne merge rien, ne bloque même pas la PR : la décision reste humaine. L'agent
est un relecteur de plus, pas un approbateur.

### 3.5 Le rapport planifié

```bash
#!/usr/bin/env bash
# Rapport hebdomadaire des dépendances vulnérables — lecture seule.
set -euo pipefail
dotnet list ECommerce.slnx package --vulnerable --include-transitive > /tmp/vuln.txt
claude -p "À partir de ce rapport, qualifie chaque vulnérabilité pour l'ecommerce-app :
  le paquet est-il atteint à l'exécution ? dans quel service ? exposé hors Development ?
  Classe par criticité RÉELLE et propose la montée de version minimale." \
  --allowedTools "Read,Grep,Glob" < /tmp/vuln.txt > rapport-vulnerabilites.md
```

---

## 4. Mini-lab — de la boucle au pipeline (20 min)

### Partie A — `/loop` (5 min)

```bash
cd ~/lab-ecommerce && claude
```
```text
> /loop 2m Lance dotnet test ECommerce.slnx et signale tout test rouge. Ne corrige rien.
```

Pendant qu'elle tourne, faites une petite modification dans un autre terminal ; observez le
signalement. Arrêtez la boucle.

### Partie B — headless (8 min)

```bash
claude -p "Décris en 5 lignes comment Ordering valide un produit." --allowedTools "Read,Grep,Glob"
git log -5 --oneline | claude -p "Ces messages respectent-ils Conventional Commits ?" --output-format json | jq -r '.result'
```

Testez la restriction :

```bash
claude -p "Crée un fichier test.txt contenant bonjour" --allowedTools "Read,Grep"
ls test.txt
```

Le fichier n'existe pas. **Vous venez de vérifier votre garde-fou de CI.**

Testez aussi que vos hooks s'appliquent en headless :

```bash
claude -p "Lance docker compose down -v" --allowedTools "Bash"
```

Refus du hook `guard-destructive`, même sans humain.

### Partie C — auditer le job (7 min)

Créez `.github/workflows/migration-review.yml` (§3.4), puis :

```text
> /security-review
> Relis @.github/workflows/migration-review.yml : ce job peut-il modifier le dépôt, merger,
  appliquer une migration, ou exposer un secret dans les logs ? Un fork peut-il le déclencher
  avec mes secrets ?
```

On **fait auditer le pipeline qui appelle l'agent**, comme le reste de la chaîne.

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| Oublier `-p` en CI | Le job attend un humain, puis expire | Toujours `-p` |
| Pas de `--allowedTools` | Le job échoue sur une demande de permission | Liste blanche explicite |
| Élargir les permissions pour faire passer le job | Garde-fous contournés | Corriger la tâche, pas les droits |
| Clé d'API en clair dans le YAML | Secret dans les logs et l'historique | `secrets.` de la forge |
| Une boucle qui **corrige** | Action non revue | Boucles en lecture seule (R2) |
| Faire décider le job (merge, migration, déploiement) | Décision non humaine, non tracée | L'agent commente, l'humain décide |
| Parser la sortie texte à la main | Pipeline fragile | `--output-format json` + `jq` |

---

## 6. Checklist de sortie

- [ ] J'ai fait tourner une boucle `/loop` en lecture seule.
- [ ] Je sais appeler `claude -p` dans un pipe et exploiter `--output-format json`.
- [ ] J'ai vérifié l'effet de `--allowedTools` et constaté que mes hooks s'appliquent en headless.
- [ ] J'ai un job de CI qui **commente** sans rien modifier, et je l'ai fait auditer.
- [ ] Je sais dire pourquoi le degré 3 d'automatisation est hors cadre ici.

---

## Et maintenant

Les briques sont posées (modules 00 à 08), dans l'ordre où chacune lève la limite de la
précédente — résumé dans [`docs/choisir-sa-brique.md`](../../docs/choisir-sa-brique.md). Cette annexe
a montré qu'elles s'appliquent aussi **sans vous** : vos hooks protègent la CI, vos skills et vos
sous-agents y travaillent. La suite, ce sont les labs
de livraison et d'exploitation : [CI/CD](../../labs/lab-06-ci-cd/), [conteneurs](../../labs/lab-07-docker/),
[Kubernetes](../../labs/lab-08-kubernetes/), [Helm](../../labs/lab-09-helm/),
[observabilité](../../labs/lab-10-observabilite/), [incident](../../labs/lab-11-incident-postmortem/),
puis le [capstone](../../labs/capstone/).
