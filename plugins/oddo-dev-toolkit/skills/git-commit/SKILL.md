---
name: git-commit
description: Crée un commit Git propre au format Conventional Commits pour l'ecommerce-app. À utiliser quand l'utilisateur demande de committer, d'enregistrer ou de « faire un commit » de ses changements. Analyse le diff, propose le message, et demande TOUJOURS validation avant de committer.
---

# Skill : git-commit

Objectif : un commit **lisible, atomique et sûr**, sans que l'utilisateur rédige le message.

## Procédure

1. **Situer** — `git branch --show-current`. Sur `main` : **refuser** et proposer
   `git switch -c feat/<sujet>` (ou `fix/`, `chore/`, `test/`, `ci/`).
2. **Lire le diff** — `git status`, puis `git diff` et `git diff --staged`. Résumer en une
   phrase ce que font les changements, et signaler s'ils mélangent plusieurs sujets
   (dans ce cas, proposer plusieurs commits).
3. **Indexer** — si rien n'est indexé, proposer les fichiers pertinents. Ne jamais indexer
   `.env`, `*.pem`, `*.key`, `appsettings.*.local.json`, `bin/`, `obj/`, `TestResults/`.
4. **Rédiger** — `type(scope): description à l'impératif, en anglais`.
   - Types : `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`, `build`.
   - Scopes : `catalog`, `ordering`, `gateway`, `web`, `apphost`, `defaults`, `db`, `k8s`, `helm`, `ci`.
   - Un corps qui explique le **pourquoi** dès que le changement n'est pas évident.
   - Une migration EF Core se committe **seule**, avec un message `feat(db): ...` ou `fix(db): ...`.
5. **Valider** — afficher le message et la liste des fichiers, puis **attendre l'accord explicite**.
6. **Committer** puis afficher `git log -1 --oneline`.

## Garde-fous

- Jamais de `git push` dans ce skill : le push est une étape séparée (skill `open-pr`).
- Jamais `--no-verify` : si un hook bloque le commit, on corrige la cause.
- Si un secret est repéré dans le diff : **arrêter** et le signaler, ne pas committer.
