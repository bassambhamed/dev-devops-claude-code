#!/usr/bin/env bash
# FORMATEUR UNIQUEMENT — scénario A du lab 11 : rupture de contrat entre services.
#
# Un commit « cosmétique » renomme le champ JSON `price` du Catalog en `unitPrice`.
# Les tests de Catalog passent (ils désérialisent avec la même classe), ceux d'Ordering
# aussi (ils utilisent un faux Catalog) : rien ne rougit. Mais en vrai, Ordering et Web
# lisent `price` -> 0. La régression est noyée entre des commits anodins pour `git bisect`.
#
# Usage : ./inject-contract-break.sh <chemin-du-depot-participant>
set -euo pipefail

repo="${1:?usage: inject-contract-break.sh <repo>}"
cd "$repo"
model="src/ECommerce.Catalog.Api/Models/Product.cs"

git diff --quiet && git diff --cached --quiet || { echo "Dépôt non propre : commitez d'abord." >&2; exit 1; }
grep -q 'public decimal Price { get; set; }' "$model" || { echo "Cible introuvable dans $model (lab 04 fait ?)" >&2; exit 1; }
grep -q 'using System.Text.Json.Serialization;' "$model" || { echo "Le modèle doit importer System.Text.Json.Serialization (lab 04)." >&2; exit 1; }

printf '\n<!-- relu le %s -->\n' "$(date +%F)" >> README.md
git commit -qam "docs: update readme review date"

sed -i.bak 's/    public decimal Price { get; set; }/    [JsonPropertyName("unitPrice")]                    \/\/ align with front naming\n    public decimal Price { get; set; }/' "$model" && rm -f "$model.bak"
git commit -qam "style(catalog): align product price naming with front conventions"

printf '\n' >> src/ECommerce.Ordering.Api/README.md
git commit -qam "docs(ordering): fix typo"
printf '\n' >> src/ECommerce.Web/README.md
git commit -qam "docs(web): fix typo"

echo "Scénario A injecté. Symptôme à annoncer : « des commandes sont enregistrées à 0,00 € »."
