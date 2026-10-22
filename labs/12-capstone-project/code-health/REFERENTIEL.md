# Référentiel Code Health du projet ECommerce

Ce dossier (`quality/code-health/`) est le **référentiel local de santé du code** du projet.
Il est généré par l'agent CodeScene du plugin `ecom-modernizer`, versionné avec le code, et
fonctionne **sans aucune clé d'API ni service externe** : les métriques proviennent d'outils
open source exécutés localement, les règles sont celles de ce dossier.

## Contenu

| Fichier | Rôle |
|---|---|
| `rules.json` | Règles : code smells (métrique, seuils, pondération), bandes de santé, règles de bloqueurs du projet |
| `code_health.py` | Moteur et CLI : `score`, `review`, `scan`, `delta`, `safeguard`, `blockers`, `hotspots` |
| `server.py` | Serveur MCP local `code-health` (stdio) exposant le moteur aux agents |
| `baseline.json` | Notes de référence par fichier (générées par `scan --write-baseline`) |
| `waivers.json` | Dérogations validées par un humain (gate G1) |
| `history/` | Rapports d'audit et de revue successifs |

## Modèle de notation

1. Les métriques par fonction sont calculées par **lizard** : complexité cyclomatique,
   complexité cognitive, profondeur d'imbrication, lignes utiles, nombre de paramètres.
   Langages : C#, TypeScript, TSX, JavaScript.
2. Chaque métrique est comparée aux seuils `warning` et `critical` du smell correspondant
   (avec d'éventuelles surcharges par langage).
3. Les smells de fichier sont évalués : taille du fichier et **duplication** (fenêtres de
   6 lignes normalisées identiques dans le projet, fusionnées en blocs).
4. Note du fichier : `max(1, 10 − Σ pénalités)`, où une alerte `warning` coûte 0,5 × poids,
   une alerte `critical` 1,0 × poids, et la duplication `min(2, 0,7 × blocs × 0,5)`.
5. Bandes : **healthy** ≥ 9, **problematic** de 4 à 8,9, **unhealthy** < 4.
6. Note d'un périmètre : moyenne des notes pondérée par les lignes utiles.

Le modèle s'inspire des facteurs de la Code Health de CodeScene (Complex Method, Deep Nested
Complexity, Large Method, Excess Function Arguments, Code Duplication…) mais sa formule est
propre au projet, publique et modifiable.

## Règles de bloqueurs

La section `blocker_rules` décrit des motifs propres au projet (expressions régulières par
glob de fichiers) : sondes de santé limitées au développement, base en mémoire,
`EnsureCreated`, `HasData` à identifiants explicites, appel distant dans une boucle, secret en
`NEXT_PUBLIC_*`, sortie `standalone` absente… Elles produisent des bloqueurs B0 à B3 avec un
propriétaire ; elles n'influent pas sur la note.

## Usage

```bash
uv run --script quality/code-health/code_health.py scan --out quality/code-health/history/audit.json
uv run --script quality/code-health/code_health.py review src/ECommerce.Ordering.Api/Endpoints/OrderingEndpoints.cs
uv run --script quality/code-health/code_health.py delta --base main      # avant une pull request
uv run --script quality/code-health/code_health.py safeguard              # avant un commit (code 1 si régression)
uv run --script quality/code-health/code_health.py hotspots --since "6 months"
```

Serveur MCP (n'importe quel client MCP) : `uv run --script quality/code-health/server.py`.

## Gouvernance

- Toute modification de `rules.json` (seuils, pondérations, règles) ou de `waivers.json`
  passe par une pull request validée par un humain (gate G1).
- Une dérogation précise la règle, le fichier, la fonction éventuelle, le motif, l'approbateur.
- La baseline n'est régénérée qu'après une revue (`scan --write-baseline`).
