# Labs — les cas d'usage Dev & DevOps

Onze labs et un capstone. Là où les [modules](../modules/) enseignent **une brique**, un lab
résout **un problème de votre métier** en mobilisant les briques déjà vues — et révèle, à la fin,
la limite qui justifie la suivante.

## Canevas commun

1. **Objectif** — ce que vous aurez produit.
2. **Pré-requis** — labs et outils.
3. **Briques mobilisées — et pourquoi chacune** : pourquoi *cette* brique, et pas une autre.
4. **Déroulé pas-à-pas** — à taper dans un terminal, avec ce qui doit se passer.
5. **Livrable** · 6. **Garde-fous** (et leur niveau de garantie) · 7. **Pour aller plus loin**.
8. **La limite révélée** — le cas d'usage que le lab ne résout pas, et où il est traité.

Chaque lab a un dossier **`solution/`** : le corrigé, à utiliser **après avoir essayé**. La
mention « vérifié » indique ce qui a été réellement exécuté en écrivant le corrigé.

## Table des labs

| Lab | Cas d'usage | Après | Briques nouvellement mobilisées | Durée |
|:---:|---|:---:|---|:---:|
| [01](lab-01-git-github/) | **Git & GitHub** : un correctif jusqu'à la PR | M03 | Mémoire, commandes perso | 60 min |
| [02](lab-02-tests/) | **Tests** : catalogue et commande, faux Catalog | M05 | Skill `gen-tests`, hooks `PostToolUse` et `Stop` | 60 min |
| [03](lab-03-securite-secrets/) | **Sécurité & secrets** : poste, dépendances, CI | M06 | Permissions, hooks d'écriture et d'audit, plugins (officiel + équipe) | 60 min |
| [04](lab-04-postgresql/) | **Créer la base PostgreSQL** ✨ | M08 | Skill `ef-migration`, hook `guard-migrations`, `db-reviewer`, MCP DBHub, context7 | 90 min |
| [05](lab-05-frontend/) | **Améliorer le frontend** ✨ | M08 | Plugin `frontend-design`, MCP `claude-in-chrome`, `a11y-reviewer` | 75 min |
| [06](lab-06-ci-cd/) | **CI/CD** avec revue headless | Annexe | `claude -p` dans GitHub Actions | 60 min |
| [07](lab-07-docker/) | **Conteneurisation** avec PostgreSQL | Lab 06 | Skill `containerize`, hook de scan d'image | 45 min |
| [08](lab-08-kubernetes/) | **Kubernetes** : app + base, Secret, pannes | Lab 07 | Skill `k8s-bootstrap`, sous-agent `k8s-debug-pod` | 60 min |
| [09](lab-09-helm/) | **Helm** multi-environnements | Lab 08 | Skill `helm-package` ; relire le rendu | 30–45 min |
| [10](lab-10-observabilite/) | **Observabilité** — parcours Dev / DevOps | Lab 09 | MCP Aspire, plugin `grafana-mcp` | 60 min |
| [11](lab-11-incident-postmortem/) | **Incident & post-mortem** — scénario Dev / DevOps | Lab 10 | `incident-analyst`, `git bisect run`, skill `postmortem` | 45–60 min |
| [🏁](capstone/) | **Capstone** : une fonctionnalité de bout en bout | tout | Tout | 2 h |

✨ = nouveaux labs de ce parcours. Les labs Multipass, Terraform et Ansible du parcours Ops n'en
font pas partie ; observabilité et incident y sont **adaptés** aux deux métiers.

## Quelle brique pour quel lab

|  | Mémoire | Cmd perso | Hooks | Skills | Plugins | Sous-agents | MCP | Headless |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 01 Git | ● | ● | | | | | | |
| 02 Tests | ● | ● | ● | ● | | | | |
| 03 Sécurité | | | ● | | ● | | | |
| 04 PostgreSQL | | ● | ● | ● | ● | ● | ● | |
| 05 Frontend | | ● | ● | ● | ● | ● | ● | |
| 06 CI/CD | | | | ● | | ● | ● | ● |
| 07 Docker | | | ● | ● | | | | |
| 08 Kubernetes | | | ● | ● | | ● | | |
| 09 Helm | | | ● | ● | | ● | | |
| 10 Observabilité | | | ● | ● | ● | | ● | |
| 11 Incident | | | ● | ● | | ● | ● | |
| 🏁 Capstone | ● | ● | ● | ● | ● | ● | ● | ● |

## Dépendances techniques

| Lab | Exige | Ce qui manque sinon |
|:---:|---|---|
| 02 → 11 | Lab 01 | Le dépôt Git et GitHub |
| 05 (filtres), 10, 11 A | Lab 04 | La base, les catégories, les tests Testcontainers |
| 08 | Lab 07 | Les images `ecommerce-*:dev` |
| 09, 10 B, 11 B | Lab 08 | Le cluster `ecom-dev` et le Secret `catalog-db` |
| 11 A | Lab 10 (Dev) | La télémétrie métier et le serveur MCP Aspire |

> **La chaîne critique : 04 → 07 → 08.** Sans base, pas de données ; sans images, pas de
> cluster. Les labs 09 et 10 B sont les variables d'ajustement de J4.

## Où travailler

```bash
export FORMATION="$PWD"                           # racine du dépôt de formation
cp -r ecommerce-app ~/lab-ecommerce && cd ~/lab-ecommerce
claude
```

Chaque énoncé se termine par la commande exacte pour appliquer son corrigé. Les corrigés sont
**cumulatifs** : celui d'un lab suppose les précédents appliqués.

## Rappel permanent

Tous les labs respectent les [garde-fous](../docs/garde-fous.md) : aucune donnée réelle, aucun
accès à un système de production, aucune action destructive sans validation humaine explicite,
aucun secret dans un fichier, un prompt ou une sortie.
