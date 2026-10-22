#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2.3,<3", "lizard>=1.17,<2"]
# ///
"""Serveur MCP local « code-health » du référentiel ecom-modernizer (stdio, aucune clé d'API).

Expose le moteur code_health.py avec des noms d'outils compatibles avec ceux du serveur
CodeScene, afin que les prompts et les skills de l'agent CodeScene restent inchangés.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import code_health as ch  # noqa: E402
from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer(
    name="code-health",
    version="1.0.0",
    instructions="Santé du code locale (1-10) selon le référentiel versionné du projet (rules.json). "
                 "Outils en lecture seule ; les chemins sont relatifs à la racine du projet.",
)


def as_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


@server.tool()
def code_health_score(file_path: str) -> str:
    """Note de santé (1 à 10) d'un fichier source et sa bande (healthy, problematic, unhealthy)."""
    r = ch.full(ch.rel_path(file_path))
    return f"Code Health de {r['file']} : {r['score']} ({r['band']}) — {len(r['smells'])} smell(s), {r['nloc']} lignes utiles"


@server.tool()
def code_health_review(file_path: str) -> str:
    """Revue détaillée d'un fichier : code smells (métrique, seuil, conseil), duplications et bloqueurs."""
    return as_json(ch.full(ch.rel_path(file_path)))


@server.tool()
def analyze_change_set(base_ref: str = "HEAD") -> str:
    """Compare les fichiers modifiés depuis base_ref (et non suivis) avec leur version de référence ; liste les régressions."""
    return as_json(ch.cmd_delta(base_ref))


@server.tool()
def pre_commit_code_health_safeguard() -> str:
    """Contrôle les fichiers indexés (git add) avant un commit ; pass=false si une régression est détectée."""
    return as_json(ch.cmd_safeguard())


@server.tool()
def project_code_health(path: str = "src") -> str:
    """Synthèse d'un périmètre : moyenne pondérée, minimum, répartition par bande, bloqueurs ouverts."""
    r = ch.project(ch.source_files([path]))
    r["files"] = [{k: f[k] for k in ("file", "score", "band", "nloc")} | {"smells": len(f["smells"])} for f in r["files"]]
    return as_json(r)


@server.tool()
def list_blockers(path: str = "src") -> str:
    """Applique les règles de bloqueurs du référentiel (rules.json, section blocker_rules) à un périmètre."""
    return as_json([b for f in ch.source_files([path]) for b in ch.blockers_in(f, ch.read(f))])


@server.tool()
def list_hotspots(since: str = "6 months", top: int = 10) -> str:
    """Hotspots locaux : fréquence de modification (historique git) croisée avec la santé du code."""
    return as_json(ch.cmd_hotspots(since, top))


@server.tool()
def rules_config_list_thresholds(language: str = "") -> str:
    """Seuils et pondérations des code smells, avec les surcharges éventuelles d'un langage (csharp, tsx...)."""
    smells = {k: ch.threshold(k, language or None) for k in ch.RULES["smells"]}
    return as_json({"bands": ch.RULES["bands"], "penalty": ch.RULES["penalty"], "smells": smells})


@server.tool()
def explain_code_health() -> str:
    """Documentation du modèle de santé du code et du référentiel (REFERENTIEL.md)."""
    doc = Path(__file__).resolve().parent / "REFERENTIEL.md"
    return doc.read_text(encoding="utf-8") if doc.is_file() else "REFERENTIEL.md absent du référentiel."


if __name__ == "__main__":
    server.run("stdio")
