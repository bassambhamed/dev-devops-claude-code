# Module 00 — Prise en main

> **Durée :** 45 min · **Pré-requis :** [docs/prerequis.md](../../docs/prerequis.md) validé
> · **Suivant :** [Module 01 — Commandes natives](../01-commandes-natives/)

---

## 1. La limite — pourquoi commencer ici

Vous avez installé un outil dont vous ne savez ni **ce qu'il voit**, ni **ce qu'il peut faire**,
ni **ce qu'il fera sans vous demander**. Tant que ces trois points ne sont pas clairs, on ne le
lance pas sur un dépôt qui compte.

| Cas d'usage | Ce qu'on veut savoir avant |
|---|---|
| **Dev** — « explique-moi comment Ordering valide un produit » | Va-t-il lire le code ou inventer une réponse plausible ? |
| **DevOps** — « lance le build » | Va-t-il exécuter une commande sur ma machine ? Avec quels droits ? |

## 2. Le concept — un agent, pas un chat

Un LLM seul produit du texte. Claude Code est un LLM **équipé** :

```
        ┌──────────────────────────────────────────────┐
        │                  Le modèle                   │
        │        décide de la prochaine action         │
        └───────────────┬──────────────────┬───────────┘
                        │ appelle          │ observe
                        ▼                  │
        ┌──────────────────────────────────┴───────────┐
        │                  Les outils                  │
        │   Read · Edit · Write · Bash · Grep · Glob   │
        └───────────────┬──────────────────────────────┘
                        │ agit sur
                        ▼
        ┌──────────────────────────────────────────────┐
        │        Votre dépôt · votre machine           │
        └──────────────────────────────────────────────┘
```

La boucle est : **il agit → il observe → il corrige**. Il lance `dotnet build`, lit l'erreur
`CS0542`, corrige le composant, relance. C'est ce qui le distingue d'un chat qui propose du texte
à recopier.

| Conséquence | Ce que ça implique pour vous |
|---|---|
| Il exécute de vraies commandes | Les **permissions** ne sont pas un détail de confort |
| Il ne voit que ce qu'on lui donne | Le **contexte** conditionne toute la qualité |
| Il se trompe avec assurance | La **vérification** (build, tests, relecture) reste la vôtre |

### Trois surfaces, un même agent

| Surface | Quand la préférer |
|---|---|
| **Terminal** (`claude`) | La surface de référence de la formation ; indispensable pour le headless et la CI |
| **Extension VS Code / plugin JetBrains** | Diffs dans l'éditeur, sélection envoyée en contexte, diagnostics de l'IDE |
| **Application de bureau** | Plusieurs sessions en parallèle, revue visuelle |

Les trois lisent les **mêmes** fichiers de configuration (`CLAUDE.md`, `.claude/`). Ce que vous
construisez pendant la formation vaut partout.

## 3. Anatomie d'une session

```bash
cd ecommerce-app     # 1. le dossier détermine ce que l'agent voit
claude               # 2. session interactive
```

Au démarrage, dans l'ordre :

1. Le **répertoire de travail** devient la frontière par défaut de l'agent.
2. Les fichiers **mémoire** sont chargés : `~/.claude/CLAUDE.md` (vous), puis `./CLAUDE.md` (le projet).
3. Les **permissions**, **hooks**, **skills**, **plugins** et **serveurs MCP** applicables sont chargés.
4. L'agent attend votre prompt.

Trois façons de lui parler :

| Vous tapez | Ça part vers | Exemple |
|---|---|---|
| Du texte libre | Le **modèle**, qui interprète | « Comment Ordering valide-t-il un produit ? » |
| `/quelque-chose` | Le **harnais**, qui exécute | `/context` |
| `!commande` | Le **shell** ; la sortie entre en contexte | `!dotnet build ECommerce.slnx` |

---

## 4. Mini-lab — première session (15 min)

Depuis la racine du dépôt de formation :

```bash
export FORMATION="$PWD"                      # racine du dépôt de formation, utilisée par tous les labs
cp -r ecommerce-app ~/lab-ecommerce && cd ~/lab-ecommerce
export PATH="/usr/local/share/dotnet:$PATH"
claude
```

> Ajoutez `export FORMATION=<chemin du dépôt de formation>` à votre `~/.zshrc` ou `~/.bashrc` :
> les énoncés y font référence pour copier un modèle ou un corrigé.

**Étape 1 — voir sans toucher.**

```text
> Décris l'architecture de cette application : les services, comment ils se trouvent
  (service discovery), qui appelle qui, et ce qui est exposé à l'extérieur.
  Ne modifie aucun fichier.
```

Observez : il **lit** des fichiers avant de répondre (`AppHost.cs`, `appsettings.json` du
Gateway, `CatalogServiceClient.cs`…). Sa stratégie d'exploration vous dit ce qu'il a compris.

**Étape 2 — une question de développeur.**

```text
> Que se passe-t-il exactement quand je crée une commande avec un produit qui n'existe pas ?
  Cite les fichiers et les lignes.
```

Exigez les références : une réponse sans fichier ni ligne est une réponse à vérifier.

**Étape 3 — le faire exécuter.**

```text
> !dotnet build ECommerce.slnx
```

Le `!` exécute la commande **vous-même** ; la sortie entre dans le contexte. Comparez avec :

```text
> Lance le build de la solution et dis-moi s'il y a des avertissements à traiter.
```

Là, c'est **lui** qui décide de lancer la commande, et il vous demande l'autorisation. **C'est le
moment clé de la formation :** cette boîte de dialogue est votre dernier rempart. Apprenez à la
lire plutôt qu'à la valider. (Il trouvera d'ailleurs de vrais avertissements `NU1903` :
des dépendances vulnérables. On les traitera au [Lab 03](../../labs/lab-03-securite-secrets/).)

**Étape 4 — constater ce qu'il ignore.**

```text
> Quelle est notre convention de nommage des branches, et quel format de message de commit
  utilise l'équipe ?
```

Il ne sait pas. Il n'a aucune raison de savoir. **Retenez cette réponse** : c'est le problème que
le [Module 02](../02-contexte-et-memoire/) résout.

**Étape 5 — quitter, puis reprendre.**

```text
> /exit
```
```bash
claude -c      # reprend la dernière conversation de ce dossier
```

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| Lancer `claude` depuis `$HOME` | L'agent explore tout le disque, le contexte explose | Toujours depuis la racine du dépôt |
| Valider les permissions par réflexe | Un jour, c'est un `DROP TABLE` qui passe | Lire chaque commande proposée |
| Accepter une explication sans références | Une hallucination plausible devient une vérité d'équipe | Exiger fichiers et lignes |
| Attendre qu'il devine vos conventions | Du code qui ne ressemble pas au vôtre | Module 02 : `CLAUDE.md` |
| Travailler sur l'original de `ecommerce-app/` | Le dépôt de formation est modifié | Toujours une copie (`~/lab-ecommerce`) |

---

## 6. Checklist de sortie

- [ ] Je sais lancer une session dans le bon dossier et la reprendre (`claude -c`).
- [ ] Je sais expliquer la boucle **agir → observer → corriger**.
- [ ] Je distingue ce qui part vers le modèle, vers le harnais (`/`) et vers le shell (`!`).
- [ ] J'ai vu une demande de permission et je sais ce qu'elle protège.
- [ ] J'ai constaté que l'agent ignore les conventions de mon équipe.

---

## 7. La limite suivante

Vous savez le faire **parler** et **agir**. Mais quand il part dans une mauvaise direction —
un refactoring qui touche dix fichiers de trop —, vous ne savez ni l'arrêter proprement, ni
revenir en arrière, ni voir ce qu'il a réellement en tête.

> **→ [Module 01 — Commandes natives](../01-commandes-natives/) :** les commandes du harnais qui
> cadrent, mesurent et annulent — sans rien installer.
