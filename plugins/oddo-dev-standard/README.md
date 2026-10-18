# oddo-dev-standard

Un plugin **sans aucun composant** : seulement des `dependencies`. L'installer installe le poste
de travail standard de l'équipe.

| Dépendance | Marketplace | Apport |
|---|---|---|
| `oddo-dev-toolkit` | `oddo-dev-marketplace` | Skills, sous-agents et garde-fous de l'équipe |
| `csharp-lsp` | `claude-plugins-official` | Diagnostics du compilateur après chaque édition (binaire `csharp-ls` requis) |
| `context7` | `claude-plugins-official` | Documentation à jour des bibliothèques (MCP) |
| `security-guidance` | `claude-plugins-official` | Avertissements de sécurité à l'édition, revue du diff en fin de tâche |

Les dépendances vers le marketplace officiel ne s'installent que parce que le marketplace racine
l'autorise (`allowCrossMarketplaceDependenciesOn` dans `.claude-plugin/marketplace.json`).
Installation vérifiée : `(+ 4 dependencies: oddo-dev-toolkit, csharp-lsp, context7, security-guidance)`.
