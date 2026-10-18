# oddo-dev-toolkit

Plugin Claude Code des équipes **Dev & DevOps** de la formation : ce que l'équipe sait faire
(skills, commandes), ses relecteurs (sous-agents en lecture seule) et ses garde-fous (hooks
déterministes), installables en une commande.

> **Plugin de référence.** La version que vous distribuerez est celle que *vous* aurez construite
> avec vos conventions ([module 06](../../modules/06-plugins/)). Celle-ci sert de modèle et de corrigé.

## Installer

```bash
claude plugin marketplace add <chemin-ou-dépôt-de-la-formation>
claude plugin install oddo-dev-toolkit@oddo-dev-marketplace --scope project
claude plugin details oddo-dev-toolkit      # ≈ 1 300 tokens permanents ; les hooks ne coûtent rien en contexte
```

Ou le poste standard complet (ce plugin + `csharp-lsp`, `context7`, `security-guidance`) :

```bash
claude plugin install oddo-dev-standard@oddo-dev-marketplace
```

## Contenu

| Type | Nom (préfixé `oddo-dev-toolkit:`) | Rôle |
|---|---|---|
| Commande | `ship` · `review-diff` | Livrer en étapes validées · relire le diff (lecture seule) |
| Skill | `git-commit` · `open-pr` | Commits conventionnels et PR documentées, validation avant toute action distante |
| Skill | `gen-tests` (+ `doctrine.md`) | Tests d'intégration : WebApplicationFactory, faux services, Testcontainers |
| Skill | `ef-migration` (+ `checklist-revue.md`) | Migrations EF Core : générer, relire le SQL, appliquer en local |
| Skill | `ui-modernize` (+ `a11y-checklist.md`) | Blazor : états, responsive, accessibilité, logique métier intacte |
| Skill | `containerize` · `ci-pipeline` | Images chiselées non-root · workflows à gate humain |
| Skill | `postmortem` (+ `TEMPLATE.md`) | Post-mortem blameless, actions assignées |
| Agent | `test-engineer` · `security-reviewer` · `db-reviewer` · `a11y-reviewer` · `k8s-debug-pod` · `incident-analyst` | Relecteurs et analystes, **sans outil d'écriture** |
| Hook | `session-start` | Branche, SDK, Docker, contexte kubectl ; alerte sur `main` |
| Hook | `guard-destructive` · `secret-scan` | Bloque l'irréversible ; bloque un commit avec secret (gitleaks si présent) |
| Hook | `scan-secrets-on-write` · `guard-migrations` | Bloque l'écriture d'un secret ; interdit d'éditer une migration committée |
| Hook | `format-cs` · `audit-log` | Formate chaque `.cs` écrit ; journal JSON Lines hors dépôt (DORA) |

## Réglage

| Option (`userConfig`) | Défaut | Effet |
|---|---|---|
| `audit_dir` | `~/.claude/audit` | Dossier du journal d'audit — toujours hors d'un dépôt Git |

## Avertissement

Ce plugin exécute des scripts shell sur le poste. Avant un déploiement en entreprise : relire
chaque hook, l'adapter aux commandes de votre environnement, et le faire valider par l'équipe
sécurité. Les sous-agents de plugin ne peuvent pas déclarer de serveur MCP : la version de
`db-reviewer` reliée à la base est fournie au [lab 04](../../labs/lab-04-postgresql/).
