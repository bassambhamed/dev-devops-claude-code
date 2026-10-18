---
name: helm-package
description: Crée ou fait évoluer le chart Helm de l'ecommerce-app (helm/ecommerce) et ses values par environnement. À utiliser pour transformer des manifestes en chart, ajouter un paramètre, un environnement ou un service, ou préparer un helm upgrade. Relit le RENDU (helm template), pas seulement les templates, et ne lance jamais d'upgrade sans --dry-run validé.
---

# Skill : helm-package

Objectif : un seul jeu de templates, des différences entre environnements **explicites et
relues**.

## Procédure

1. **Paramétrer, pas copier** — une boucle `range` sur `.Values.services` plutôt qu'un fichier par
   service ; aucune valeur en dur dans `templates/` ; le namespace vient de `.Release.Namespace`.
2. **Secrets** — jamais dans `values*.yaml` : le chart référence un Secret existant
   (`database.existingSecret`) et le dit dans `NOTES.txt`.
3. **Valider** — `helm lint helm/ecommerce` puis `helm lint … -f values-<env>.yaml` pour chaque environnement.
4. **Relire le rendu** — `helm template ecommerce helm/ecommerce -n ecommerce -f values-<env>.yaml`.
   Comparer au manifeste d'origine (ou à l'environnement voisin) : probes, ressources, variables,
   securityContext. Signaler toute valeur de values **sans effet** dans le rendu.
5. **Simuler** — `helm upgrade --install … --dry-run` ; présenter la sortie à l'humain.
6. **Versionner** — incrémenter `version` dans `Chart.yaml` à chaque changement de templates ou de values.

## Garde-fous

- Jamais de `helm upgrade` ou `helm install` réel sans `--dry-run` présenté et validé.
- `helm uninstall` : bloqué par `guard-destructive` ; le proposer, ne pas le lancer.
- Aucun mot de passe, jeton ou chaîne de connexion complète dans les values.
