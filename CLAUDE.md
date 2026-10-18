# CLAUDE.md — dépôt de formation « Claude Code pour les Dev & DevOps »

Contexte destiné à Claude Code lorsqu'il travaille **sur ce dépôt de formation** (pas sur
l'application fil rouge, qui reçoit son propre `CLAUDE.md` au lab 01).

## Nature du dépôt

Contenu **pédagogique** (4 jours, développeurs .NET et ingénieurs DevOps), jumeau de
`../Ops_Claude_code/` :
- `docs/` — dont `choisir-sa-brique.md`, le fil rouge qui justifie chaque transition de brique ;
- `modules/` — 9 modules (00 à 08), une brique chacun, et `modules/annexe-agent-sans-terminal/` (headless, `/loop`,
  CI) **hors chaîne** ; `modules/08-mcp/exemple-serveur-mcp-csharp/` est du code compilable ;
- `labs/` — 11 labs + capstone, corrigés **cumulatifs** dans `solution/` ;
- `plugins/oddo-dev-toolkit/` (plugin d'équipe) et `plugins/oddo-dev-standard/` (bundle de dépendances),
  catalogués par `.claude-plugin/marketplace.json` ;
- `ecommerce-app/` — l'application fil rouge, **livrée nue** ; `tp/` — le TP de prompting du J1 (Markdown, exécuté dans l'application Claude).
- `slides/` — **PDF seulement**. Les sources Beamer sont dans `../dev-devops-claude-code_latex/`
  (`make all` compile en deux passes et publie ici) : ne jamais éditer un PDF, ne jamais committer
  de `.aux`/`.log`. Tout changement de module ou de lab se reporte dans le deck correspondant (02 ou 03).

## Règles de contenu

- **Langue : français.** Code, identifiants et configuration en anglais.
- **Deux publics** : chaque module ouvre sur la limite rencontrée avec un cas d'usage **Dev** et un
  cas **DevOps** ; les labs 10 et 11 ont un parcours par métier.
- **Cadre bancaire (DORA, RGPD)** : chaque lab énonce ses garde-fous et leur niveau de garantie
  (consigne, contrôle, plateforme). Aucune action destructive, aucun secret, aucune donnée réelle.
- **Canevas des modules** : La limite · Le concept · Anatomie · Mini-lab · Erreurs fréquentes ·
  Checklist de sortie · La limite suivante.
- **Canevas des labs** : Objectif · Pré-requis · Briques mobilisées (et pourquoi) · Déroulé ·
  Livrable · Garde-fous · Pour aller plus loin · La limite révélée · Corrigé.
- Les énoncés citent `$FORMATION` (racine de ce dépôt) et travaillent dans `~/lab-ecommerce`.

## Invariants à ne pas casser

- **L'ordre des briques est délibéré** : commandes natives → mémoire → commandes perso → **hooks →
  skills → plugins → sous-agents → MCP**. La chaîne s'arrête au MCP : le mode headless et la CI ne
  sont **pas** des briques (un mode d'exécution, un cas d'usage) — ils restent en annexe et au Lab 06.
  Ne pas réordonner sans demande ; toute nouvelle
  brique doit être justifiée par une limite de la précédente.
- `ecommerce-app/` reste sans `.claude/`, sans tests, sans Dockerfile, sans manifeste, sans CI.
  Tout artefact produit va dans `labs/lab-NN-*/solution/`.
- Les corrigés sont **cumulatifs** : modifier un fichier d'un lab impose de vérifier les labs
  suivants qui fournissent le même fichier (ex. `OrderingEndpoints.cs` : labs 01 et 10).
- Les modules 06 (plugins) et 08 (MCP) présentent d'abord l'existant (officiel, intégré), **puis** l'interne.
- Pas de labs Multipass, Terraform ni Ansible dans ce parcours.

## Vérifier

```bash
export PATH="/usr/local/share/dotnet:$PATH"
cd ecommerce-app && dotnet build ECommerce.slnx && cd ..
claude plugin validate plugins/oddo-dev-toolkit --strict
claude plugin validate plugins/oddo-dev-standard --strict
claude plugin validate .
helm lint labs/lab-09-helm/solution/helm/ecommerce
```

Ne jamais laisser de `bin/`, `obj/` ou `TestResults/` dans le dépôt après une vérification.
