# Module 01 — Les commandes natives

> **Durée :** 45 min · **Pré-requis :** [Module 00](../00-prise-en-main/)
> · **Suivant :** [Module 02 — Contexte & mémoire](../02-contexte-et-memoire/)

---

## 1. La limite — d'où l'on vient

Au module 00, l'agent a lu, expliqué et lancé un build. Maintenant, demandez-lui une vraie
modification :

> *« Ajoute la pagination à `GET /api/products`. »*

Il modifie l'endpoint, le client Web, la page Blazor… et peut-être le modèle au passage. Trois
questions surgissent, et un prompt ne répond à aucune :

| Besoin | Cas d'usage Dev | Cas d'usage DevOps |
|---|---|---|
| **Voir avant d'agir** | Lire le plan de la pagination avant qu'il touche quatre fichiers | Lire ce qu'il va changer dans le `docker-compose.yml` avant de l'autoriser |
| **Revenir en arrière proprement** | Le refactoring dérape : restaurer l'état exact d'avant | Une modification de `appsettings.json` casse le démarrage |
| **Voir ce qu'il a en tête** | Il « oublie » une contrainte donnée dix messages plus tôt | Les réponses deviennent incohérentes après une longue investigation |

## 2. Le concept — le harnais, pas le modèle

Une commande `/` ne part **pas** vers le modèle : elle est exécutée par le **harnais**, le
programme qui héberge l'agent. Elle est donc fiable et instantanée.

```
   « annule ce que tu viens de faire »   ──▶  le MODÈLE interprète   (probabiliste)
   /rewind                               ──▶  le HARNAIS exécute    (déterministe)
```

Retenez la règle : **tout ce qui doit marcher à coup sûr passe par le harnais.** C'est ce même
principe qui fondera les hooks au module 04.

> La liste exacte dépend de votre version : tapez `/` dans une session, c'est la seule source de
> vérité. Ce module couvre Claude Code **2.1.x**.

---

## 3. Anatomie — les commandes par intention

### 3.1 Démarrer

| Commande | Ce qu'elle fait | Réflexe |
|---|---|---|
| `/init` | Analyse le dépôt et **génère un `CLAUDE.md`** | **Premier geste** sur un dépôt (détaillé au module 02) |
| `/status` · `/doctor` | Version, modèle, compte · diagnostic d'installation | Avant d'ouvrir un ticket de support |

### 3.2 Cadrer

| Commande | Ce qu'elle fait | Réflexe |
|---|---|---|
| `/plan` (ou `Maj+Tab`) | **Mode Plan** : l'agent explore et propose, sans rien modifier, puis attend votre accord | Toute modification qui touche plus d'un fichier |
| `/goal` | Fixe l'objectif de la session ; l'agent signale les dérives | Chantier de plus d'une heure |
| `/model` · `/effort` | Modèle et niveau de raisonnement | `/effort high` avant une revue de migration ou un diagnostic difficile |
| `/add-dir <chemin>` | Ouvre un dossier supplémentaire | Les charts Helm vivent dans un autre dépôt |

### 3.3 Reprendre la main

| Commande | Ce qu'elle fait | Réflexe |
|---|---|---|
| `/rewind` (ou `Échap` `Échap`) | **Revient à un checkpoint** : code, conversation, ou les deux | La bonne réponse à « annule » |
| `/btw` | Glisse une précision **sans interrompre** la tâche | « au fait, on cible .NET 10, pas 8 » |
| `/compact` | Résume la conversation pour libérer du contexte | `/context` dépasse 70 % et la tâche continue |
| `/clear` | Repart à vide (la mémoire projet reste chargée) | Changement complet de sujet |
| `/resume` · `/export` · `/rename` | Reprendre · archiver · renommer une session | Passer la main à un collègue |

**`/rewind` vs « annule ».** Demander d'annuler, c'est demander au modèle de *deviner* ce qu'il
faut défaire. `/rewind` restaure un **checkpoint réel**. Attention : les checkpoints couvrent les
fichiers édités par l'agent, pas les effets d'une commande shell (une migration appliquée, une
image construite). Pour ceux-là, Git et les garde-fous restent indispensables.

### 3.4 Voir

| Commande | Ce qu'elle fait |
|---|---|
| `/context` | **Ce qui occupe la fenêtre de contexte**, source par source : la commande de diagnostic n°1 |
| `/usage` · `/insights` | Coût et limites · statistiques d'usage |
| `/tasks` | Ce qui tourne en arrière-plan (un `dotnet watch`, un sous-agent) : voir, arrêter |

### 3.5 Qualité et sécurité

| Commande | Ce qu'elle fait | Réflexe |
|---|---|---|
| `/code-review [--fix]` | Revue du diff courant : bugs, simplifications | Avant chaque commit significatif |
| `/security-review` | Analyse de sécurité des changements en cours | Avant chaque PR |
| `/permissions` | Règles `allow` / `ask` / `deny` par outil et par commande | **Avant** de laisser l'agent travailler seul |

### 3.6 Les commandes qui ouvrent sur la suite du parcours

| Commande | Ouvre sur | Commande | Ouvre sur |
|---|---|---|---|
| `/memory` | [Module 02](../02-contexte-et-memoire/) | `/plugin` | [Module 06](../06-plugins/) |
| `/hooks` | [Module 04](../04-hooks/) | `/agents` | [Module 07](../07-sous-agents/) |
| `/skills` | [Module 05](../05-skills/) | `/mcp` · `/chrome` · `/ide` | [Module 08](../08-mcp/) |
| | | `/loop` | [Annexe — l'agent sans terminal](../annexe-agent-sans-terminal/) |

---

## 4. Mini-lab — une vraie modification, sous contrôle (20 min)

```bash
cd ~/lab-ecommerce
claude
```

**1. Mesurer le point de départ**

```text
> /context
```

Notez le pourcentage occupé **avant** d'avoir rien fait.

**2. Planifier avant d'agir**

```text
> /plan Ajoute la pagination à GET /api/products (paramètres page et pageSize, pageSize
  plafonné à 50) et adapte le client Web. Ne touche pas aux modèles.
```

Lisez le plan. Posez une question dessus (« que renvoies-tu si page vaut 0 ? »). **Validez
seulement quand il est juste.**

**3. Corriger le tir en cours de route**

Pendant qu'il implémente :

```text
> /btw les réponses paginées doivent exposer le total dans un en-tête X-Total-Count,
  pas dans le corps
```

La contrainte est intégrée sans que la tâche reparte de zéro.

**4. Faire relire**

```text
> !dotnet build ECommerce.slnx
> /code-review
```

**5. Annuler proprement**

```text
> /rewind
```

Choisissez le checkpoint d'avant la pagination, option *code et conversation*. Vérifiez :

```bash
git status        # si vous avez initialisé Git ; sinon, ouvrez CatalogEndpoints.cs
```

L'état est restauré **sans avoir décrit ce qu'il fallait défaire**.

**6. Poser une première règle de permission**

```text
> /permissions
```

Ajoutez une règle `ask` sur `Bash(dotnet ef:*)`, puis demandez « liste les migrations EF ». Vous
êtes sollicité — c'est le comportement voulu pour tout ce qui touche à une base.

**7. Mesurer**

```text
> /context
> /usage
```

Comparez avec l'étape 1 : vous voyez concrètement ce qui remplit une fenêtre de contexte (les
fichiers lus, les sorties de build).

---

## 5. Erreurs fréquentes

| Erreur | Conséquence | Correctif |
|---|---|---|
| Modifier sans `/plan` | Quatre fichiers changés quand on en attendait un | Mode Plan pour tout ce qui dépasse un fichier |
| Dire « annule » au lieu de `/rewind` | Annulation approximative, état incertain | `/rewind` |
| Croire que `/rewind` annule une commande shell | Une migration appliquée reste appliquée | Checkpoints = fichiers ; le reste se gère avec Git et les garde-fous |
| Couper l'agent pour une précision | La tâche repart de travers | `/btw` |
| Ignorer `/context` jusqu'au blocage | Réponses incohérentes attribuées au modèle | Surveiller, puis `/compact` |
| Croire que `/security-review` remplace une revue humaine | Faux sentiment de sécurité | C'est un filet, pas un contrôle |

---

## 6. Checklist de sortie

- [ ] Je sais travailler en mode Plan et ne valider qu'un plan juste.
- [ ] Je sais revenir en arrière avec `/rewind` et corriger le tir avec `/btw`.
- [ ] Je sais lire `/context` et choisir entre `/compact` et `/clear`.
- [ ] J'ai lancé `/code-review` sur un diff réel.
- [ ] J'ai posé au moins une règle dans `/permissions`.

---

## 7. La limite suivante

Faites `/clear`, puis redemandez la pagination. Il recode une URL de service en dur, utilise
`dotnet build` sans la solution, nomme sa branche `feature-pagination`. Il ne l'a pas *oublié* :
il ne l'a **jamais su**. Chaque session démarre avec la même amnésie.

> **→ [Module 02 — Contexte & mémoire](../02-contexte-et-memoire/) :** donner au projet une
> mémoire versionnée, relue à chaque session, par toute l'équipe.
