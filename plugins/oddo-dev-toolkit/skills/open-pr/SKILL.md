---
name: open-pr
description: Pousse la branche courante et ouvre une Pull Request GitHub documentée (contexte, changements, tests, risques, checklist de revue) avec la CLI gh. À utiliser quand l'utilisateur veut ouvrir, préparer ou publier une PR. Demande validation avant de pousser et ne merge jamais.
---

# Skill : open-pr

Objectif : transformer une branche de travail en **Pull Request qu'un relecteur peut juger en
cinq minutes**.

## Pré-requis

- `gh auth status` valide (sinon proposer `gh auth login` et s'arrêter).
- Au moins un commit sur une branche autre que `main`.

## Procédure

1. **Vérifier la branche** — refuser sur `main`.
2. **Récapituler** — `git log --oneline main..HEAD` et `git diff main...HEAD --stat`.
3. **Contrôler avant de publier** — `dotnet build ECommerce.slnx` et `dotnet test ECommerce.slnx`.
   Si un test échoue : s'arrêter et le dire. On ne publie pas une PR rouge.
4. **Pousser** — **demander confirmation**, puis `git push -u origin <branche>`.
5. **Rédiger la PR** :
   ```markdown
   ## Contexte
   <pourquoi ce changement, lien vers le ticket>

   ## Changements
   - <point 1>
   - <point 2>

   ## Tests
   <ce qui a été ajouté ou exécuté, résultat de dotnet test>

   ## Risques
   <migration de base ? contrat d'API modifié ? configuration ? impact déploiement ?>

   ## Checklist de revue
   - [ ] Aucun secret ni donnée client
   - [ ] Tests ajoutés pour le comportement modifié
   - [ ] Migration EF Core relue (si présente)
   - [ ] Contrat d'API inchangé, ou consommateurs mis à jour
   ```
6. **Créer** — `gh pr create --title "<titre conventionnel>" --body-file <fichier>`, puis
   afficher l'URL.

## Garde-fous

- Ne **jamais** merger (`gh pr merge`) : le merge est une décision humaine.
- Ne jamais forcer un push.
- Une PR qui touche `Migrations/`, `.github/`, `k8s/` ou `helm/` le dit explicitement dans « Risques ».
