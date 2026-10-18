#!/usr/bin/env bash
# FORMATEUR UNIQUEMENT — scénario B du lab 11 : une rotation de mot de passe « à moitié faite ».
#
# On remplace le Secret catalog-db par une nouvelle valeur, comme le ferait une procédure de
# rotation… sans changer le mot de passe dans PostgreSQL (POSTGRES_PASSWORD n'est lu qu'à la
# première initialisation du volume). Puis on simule le redémarrage d'un nœud : les nouveaux pods
# Catalog lisent le nouveau mot de passe, la base refuse, Catalog ne démarre plus.
#
# Usage : ./inject-secret-rotation.sh            (sur le cluster k3d-ecom-dev UNIQUEMENT)
set -euo pipefail

ctx="$(kubectl config current-context)"
if [ "$ctx" != "k3d-ecom-dev" ]; then
  echo "Contexte kubectl inattendu : '$ctx'. Ce script ne s'exécute que sur k3d-ecom-dev." >&2
  exit 1
fi

kubectl -n ecommerce get secret catalog-db >/dev/null

kubectl -n ecommerce create secret generic catalog-db \
  --from-literal=password="$(openssl rand -hex 24)" \
  --dry-run=client -o yaml | kubectl apply -f -

# Le « redémarrage de nœud » : les pods Catalog sont recréés et lisent le nouveau Secret.
kubectl -n ecommerce delete pod -l app=catalog --wait=false

echo "Scénario B injecté. Symptôme à annoncer : « le catalogue est vide et les commandes échouent »."
