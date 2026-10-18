#!/usr/bin/env bash
# Vérifie l'outillage de la formation « Claude Code pour les Dev & DevOps ».
# N'installe rien, ne modifie rien. Code de sortie 0 = tout l'indispensable est présent.

set -uo pipefail
export PATH="$PATH:/usr/local/share/dotnet:$HOME/.dotnet/tools:$HOME/.aspire/bin"

ok=0; ko=0; warn=0

check() {                      # check <commande> <libellé> <req|opt> [commande-de-version]
  local bin="$1" label="$2" level="$3" vcmd="${4:-}"
  if command -v "$bin" >/dev/null 2>&1; then
    local v=""
    [ -n "$vcmd" ] && v="$(eval "$vcmd" 2>/dev/null | head -1)"
    printf '  \033[32m OK \033[0m %-12s %s\n' "$label" "$v"
    ok=$((ok+1))
  elif [ "$level" = "req" ]; then
    printf '  \033[31mMANQ\033[0m %-12s (indispensable)\n' "$label"
    ko=$((ko+1))
  else
    printf '  \033[33mABS \033[0m %-12s (optionnel : labs concernés en observation)\n' "$label"
    warn=$((warn+1))
  fi
}

echo
echo "Formation Claude Code pour les Dev & DevOps — vérification des pré-requis"
echo "------------------------------------------------------------------------"
echo
echo "J1-J2 — indispensable"
check claude  "claude"  req 'claude --version'
check git     "git"     req 'git --version'
check gh      "gh"      req 'gh --version | head -1'
check dotnet  "dotnet"  req 'dotnet --version'
check jq      "jq"      req 'jq --version'

echo
echo "J2-J3 — sécurité, base de données, MCP"
check docker   "docker"   req 'docker --version'
check gitleaks "gitleaks" opt 'gitleaks version'
check trivy    "trivy"    opt 'trivy --version | head -1'
check npx      "npx"      req 'npx --version'
if dotnet ef --version >/dev/null 2>&1; then
  printf '  \033[32m OK \033[0m %-12s %s\n' "dotnet-ef" "$(dotnet ef --version 2>/dev/null | tail -1)"; ok=$((ok+1))
else
  printf '  \033[31mMANQ\033[0m %-12s (dotnet tool install --global dotnet-ef)\n' "dotnet-ef"; ko=$((ko+1))
fi
check csharp-ls "csharp-ls" opt 'echo installé'

echo
echo "J4 — conteneurs, Kubernetes, observabilité"
check kubectl "kubectl" opt 'kubectl version --client 2>/dev/null | head -1'
check k3d     "k3d"     opt 'k3d version | head -1'
check helm    "helm"    opt 'helm version --short'
check aspire  "aspire"  opt 'aspire --version'

echo
if docker info >/dev/null 2>&1; then
  echo "  Docker : moteur démarré."
else
  echo "  Docker : moteur ARRÊTÉ — démarrez Docker Desktop avant les labs 04 et suivants."
fi

echo "------------------------------------------------------------------------"
printf 'Présents : %d   Manquants (bloquants) : %d   Absents (optionnels) : %d\n' "$ok" "$ko" "$warn"
echo

if [ "$ko" -gt 0 ]; then
  echo "=> Installez les outils bloquants : voir docs/prerequis.md"
  exit 1
fi
echo "=> Poste prêt pour la formation."
