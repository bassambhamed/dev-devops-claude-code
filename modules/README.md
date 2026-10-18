# Modules — les briques de Claude Code

Neuf modules, une **brique** chacun, à suivre **dans l'ordre** — plus une annexe hors chaîne.
Chaque module s'ouvre sur une **limite** rencontrée au module ou au lab précédent, sur un cas
d'usage réel, et se termine sur la limite suivante. C'est ce fil qui justifie chaque nouvelle
brique — résumé dans [`docs/choisir-sa-brique.md`](../docs/choisir-sa-brique.md).

| # | Module | La limite qu'il lève | Cas d'usage déclencheur | Durée |
|:---:|---|---|---|:---:|
| [00](00-prise-en-main/) | Prise en main | « Que voit-il, que fait-il sans me demander ? » | Expliquer comment Ordering valide un produit | 45 min |
| [01](01-commandes-natives/) | Commandes natives | « Je ne sais ni l'arrêter, ni annuler, ni voir ce qu'il a en tête. » | Une pagination qui touche quatre fichiers | 45 min |
| [02](02-contexte-et-memoire/) | Contexte & mémoire | « Il ignore nos conventions à chaque session. » | Une URL de service codée en dur | 40 min |
| [03](03-commandes-personnalisees/) | Commandes personnalisées | « Je retape le même prompt de revue tous les jours. » | `/review-diff`, `/ship` | 30 min |
| [04](04-hooks/) | Hooks | « Ma commande *dit* de ne pas committer de secret ; rien ne l'*empêche*. » | Un mot de passe dans `appsettings` ; `docker compose down -v` | 50 min |
| [05](05-skills/) | Skills | « Un hook sait dire non, pas *faire* une procédure. » | Ajouter un SKU : migration, SQL, tests | 45 min |
| [06](06-plugins/) | Plugins | « Douze collègues, huit dépôts — et je réinvente ce qui existe. » | `csharp-lsp`, toolkit d'équipe, poste standard | 60 min |
| [07](07-sous-agents/) | Sous-agents | « La revue sature ma session et valide par complaisance. » | Relecteur sécurité indépendant, en parallèle | 45 min |
| [08](08-mcp/) | MCP | « Il ne voit ni la base, ni le navigateur, ni les traces. » | Schéma réel, page rendue, doc à jour, GitHub | 60 min |

### Annexe — hors de la chaîne

| | Annexe | Ce qu'elle montre | Cas d'usage | Durée |
|:---:|---|---|---|:---:|
| [A](annexe-agent-sans-terminal/) | L'agent sans terminal | **Un mode d'exécution, pas une brique** : les mêmes briques, lancées par `claude -p` ou `/loop` | Revue du SQL des migrations sur chaque PR ([Lab 06](../labs/lab-06-ci-cd/)) | 40 min |

## Pourquoi cet ordre

```
 commandes → mémoire → commandes perso → HOOKS → SKILLS → PLUGINS → SOUS-AGENTS → MCP
   cadrer    retenir     rejouer         imposer   savoir-   partager   déléguer     voir
                                                   faire
```

- **Les hooks avant les skills.** Dès qu'on capitalise un prompt (`/ship`), on découvre qu'une
  consigne n'est pas un contrôle. La garantie passe avant le savoir-faire : en banque, on pose
  les garde-fous avant d'outiller la productivité.
- **Les plugins avant les sous-agents et le MCP.** Une fois qu'on a quelque chose à partager, on
  apprend à consommer et à distribuer — et on découvre dans les plugins officiels des sous-agents
  (`pr-review-toolkit`) et des serveurs MCP (`context7`, `github`) : les deux briques suivantes.
- **Les sous-agents avant le MCP.** Le MCP ouvre l'agent sur l'extérieur — c'est la brique la
  plus risquée (R6). On l'aborde quand on sait déjà restreindre les outils et isoler un contexte,
  pour pouvoir réserver un serveur à un seul sous-agent.
- **La chaîne s'arrête au MCP.** Chaque maillon est une brique de Claude Code, qu'on configure.
  Le mode headless et la CI n'en sont pas : le premier est une autre façon de **lancer** l'agent
  (comme l'IDE ou l'application de bureau), la seconde un **cas d'usage**. D'où l'annexe, puis le
  Lab 06 — plutôt qu'un dixième maillon qui mélangerait l'outil et le métier.

## Canevas commun

1. **La limite** — le cas d'usage qui justifie la brique, côté Dev et côté DevOps.
2. **Le concept** — ce que c'est, et un tableau « en quoi ça diffère de la brique précédente ».
3. **Anatomie** — fichiers, syntaxe, ce qui est obligatoire.
4. **Mini-lab** — 15 à 35 min, clavier en main, sur l'application fil rouge.
5. **Erreurs fréquentes** — ce qui va rater, et pourquoi.
6. **Checklist de sortie** — ce que vous devez savoir faire avant de continuer.
7. **La limite suivante** — le cas d'usage que la brique ne résout pas.

## Modules et labs s'alternent

Les modules enseignent une brique ; les labs l'appliquent et révèlent la limite suivante. L'ordre
de passage sur les quatre jours est dans le [README principal](../README.md#programme-4-jours).

```
J1  00 → 01 → 02 → 03
J2  Lab 01 → 04 → 05 → Lab 02 → 06 → Lab 03
J3  07 → 08 → Lab 04 → Lab 05 → Annexe → Lab 06
J4  Lab 07 → Lab 08 → Lab 09 → Lab 10 → Lab 11 → Capstone
```

## Où travailler

Sauf mention contraire, tous les mini-labs se déroulent dans **votre copie** de l'application :

```bash
export FORMATION="$PWD"                         # depuis la racine du dépôt de formation
cp -r ecommerce-app ~/lab-ecommerce && cd ~/lab-ecommerce
claude
```

Les versions de référence de ce que vous produisez sont dans [`labs/*/solution/`](../labs/) et
dans [`plugins/oddo-dev-toolkit/`](../plugins/oddo-dev-toolkit/).
