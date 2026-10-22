#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["lizard>=1.17,<2"]
# ///
"""Moteur Code Health local du référentiel ecom-modernizer (aucune clé d'API).

La santé d'un fichier est notée de 1 à 10 à partir de métriques open source (lizard :
complexité cyclomatique, complexité cognitive, imbrication, taille, paramètres), d'une
détection de duplication et des règles versionnées dans rules.json. Les règles de
bloqueurs du référentiel sont appliquées en complément (elles n'influent pas sur la note).

Commandes :
  score <fichier>                 note du fichier
  review <fichier>                note, code smells, bloqueurs et duplications
  scan [chemins...]               analyse du périmètre (--out, --write-baseline)
  delta [--base REF]              comparaison avec une référence git (régressions)
  safeguard                       contrôle des fichiers indexés avant un commit
  blockers [chemins...]           règles de bloqueurs du référentiel
  hotspots [--since "6 months"]   fréquence de modification git x santé du code
Option commune : --json (sortie machine).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import lizard

HERE = Path(__file__).resolve().parent
KEYWORDS = {"if", "for", "foreach", "while", "switch", "using", "lock", "catch", "else", "do"}


# --------------------------------------------------------------------------- outils

def git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def project_root() -> Path:
    env = os.environ.get("CODE_HEALTH_ROOT")
    if env:
        return Path(env).resolve()
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout
        return Path(top.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


ROOT = project_root()


def load_rules() -> dict:
    path = Path(os.environ.get("CODE_HEALTH_RULES", HERE / "rules.json"))
    return json.loads(path.read_text(encoding="utf-8"))


RULES = load_rules()


def glob_to_regex(pattern: str) -> re.Pattern:
    out, i = "", 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif c == "*":
            out, i = out + "[^/]*", i + 1
        elif c == "?":
            out, i = out + "[^/]", i + 1
        elif c == "{":
            end = pattern.index("}", i)
            out += "(?:" + "|".join(re.escape(p) for p in pattern[i + 1:end].split(",")) + ")"
            i = end + 1
        else:
            out, i = out + re.escape(c), i + 1
    return re.compile("^" + out + "$")


@lru_cache(maxsize=None)
def _compiled(pattern: str) -> re.Pattern:
    return glob_to_regex(pattern)


def matches(rel: str, patterns: list[str] | str) -> bool:
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(_compiled(p).match(rel) for p in patterns)


def rel_path(path: str) -> str:
    p = Path(path)
    p = (ROOT / p) if not p.is_absolute() else p
    p = p.resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        raise SystemExit(f"Chemin hors du projet : {path}")


def language(rel: str) -> str | None:
    return RULES["languages"].get(Path(rel).suffix.lower())


def is_source(rel: str) -> bool:
    return bool(language(rel)) and matches(rel, RULES["include"]) and not matches(rel, RULES["exclude"])


def source_files(paths: list[str] | None = None) -> list[str]:
    roots = [ROOT / p for p in paths] if paths else [ROOT]
    files: set[str] = set()
    for base in roots:
        candidates = [base] if base.is_file() else base.rglob("*")
        for f in candidates:
            if f.is_file():
                rel = f.resolve().relative_to(ROOT).as_posix()
                if is_source(rel):
                    files.add(rel)
    return sorted(files)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


def waivers() -> list[dict]:
    path = HERE / "waivers.json"
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("waivers", [])


def waived(rel: str, key: str, function: str | None = None) -> dict | None:
    for w in waivers():
        if w.get("rule") == key and matches(rel, w.get("file", "**")) and (not w.get("function") or w.get("function") == function):
            return w
    return None


# --------------------------------------------------------------------------- duplication

def normalized_lines(code: str) -> list[tuple[int, str]]:
    out = []
    for n, line in enumerate(code.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith(("//", "/*", "*", "#", "using ", "import ", "namespace ")):
            continue
        if s in {"{", "}", "};", ");", "})", "});", "]", "],", "),"}:
            continue
        out.append((n, re.sub(r"\s+", " ", s)))
    return out


def windows(code: str, size: int):
    lines = normalized_lines(code)
    for k in range(len(lines) - size + 1):
        chunk = lines[k:k + size]
        digest = hashlib.sha1("\n".join(s for _, s in chunk).encode()).hexdigest()
        yield digest, chunk[0][0], chunk[-1][0]


@lru_cache(maxsize=1)
def duplication_index() -> dict[str, list[tuple[str, int, int]]]:
    size = RULES["smells"]["code_duplication"]["min_lines"]
    index: dict[str, list[tuple[str, int, int]]] = {}
    for rel in source_files():
        for digest, start, end in windows(read(rel), size):
            index.setdefault(digest, []).append((rel, start, end))
    return index


def duplicated_blocks(rel: str, code: str) -> list[dict]:
    size = RULES["smells"]["code_duplication"]["min_lines"]
    index = duplication_index()
    hits = []
    for digest, start, end in windows(code, size):
        others = [o for o in index.get(digest, []) if o[0] != rel or not (o[1] <= end and start <= o[2])]
        if others:
            hits.append((start, end, sorted({o[0] for o in others})))
    blocks: list[dict] = []
    for start, end, others in hits:
        if blocks and start <= blocks[-1]["end"] + 1:
            blocks[-1]["end"] = max(blocks[-1]["end"], end)
            blocks[-1]["with"] = sorted(set(blocks[-1]["with"]) | set(others))
        else:
            blocks.append({"start": start, "end": end, "with": others})
    return blocks


# --------------------------------------------------------------------------- analyse

ANALYZER = lizard.FileAnalyzer(lizard.get_extensions(["ns", "cognitive"]))


def threshold(smell: str, lang: str | None) -> dict:
    rule = dict(RULES["smells"][smell])
    rule.update(RULES.get("language_overrides", {}).get(lang or "", {}).get(smell, {}))
    return rule


def blockers_in(rel: str, code: str) -> list[dict]:
    found = []
    for rule in RULES.get("blocker_rules", []):
        if not matches(rel, rule["glob"]):
            continue
        flags = re.M | (re.S if rule.get("multiline") else 0)
        if rule.get("unless") and re.search(rule["unless"], code, flags):
            continue
        if rule.get("type") == "require":
            hits = [] if re.search(rule["pattern"], code, flags) else [1]
        else:
            hits = [code.count("\n", 0, m.start()) + 1 for m in re.finditer(rule["pattern"], code, flags)]
        for line in hits:
            w = waived(rel, rule["id"])
            found.append({"id": rule["id"], "severity": rule["severity"], "category": rule["category"],
                          "title": rule["title"], "location": f"{rel}:{line}", "owner": rule.get("owner"),
                          "advice": rule.get("advice"), "status": "waived" if w else "open"})
    return found


def analyze(rel: str, code: str | None = None) -> dict:
    code = read(rel) if code is None else code
    lang = language(rel)
    info = ANALYZER.analyze_source_code(rel, code)
    smells, functions = [], []
    for f in info.function_list:
        short = f.name.split("::")[-1]
        if short in KEYWORDS:
            continue
        metrics = {"cyclomatic_complexity": f.cyclomatic_complexity, "nloc": f.nloc,
                   "parameter_count": f.parameter_count,
                   "max_nested_structures": getattr(f, "max_nested_structures", 0) or 0,
                   "cognitive_complexity": getattr(f, "cognitive_complexity", 0) or 0}
        functions.append({"name": f.name, "line": f.start_line, **metrics})
        for key, base in RULES["smells"].items():
            if base.get("scope") != "function":
                continue
            rule, value = threshold(key, lang), metrics.get(base["metric"])
            severity = "critical" if value >= rule["critical"] else "warning" if value >= rule["warning"] else None
            if severity:
                smells.append({"smell": key, "label": rule["label"], "severity": severity, "function": f.name,
                               "line": f.start_line, "metric": base["metric"], "value": value,
                               "threshold": rule[severity], "advice": rule["advice"],
                               "waived": bool(waived(rel, key, f.name))})
    file_rule = threshold("large_file", lang)
    if info.nloc >= file_rule["warning"]:
        severity = "critical" if info.nloc >= file_rule["critical"] else "warning"
        smells.append({"smell": "large_file", "label": file_rule["label"], "severity": severity, "function": None,
                       "line": 1, "metric": "file_nloc", "value": info.nloc, "threshold": file_rule[severity],
                       "advice": file_rule["advice"], "waived": bool(waived(rel, "large_file"))})
    blocks = duplicated_blocks(rel, code)
    if blocks:
        dup = RULES["smells"]["code_duplication"]
        smells.append({"smell": "code_duplication", "label": dup["label"], "severity": "warning", "function": None,
                       "line": blocks[0]["start"], "metric": "duplicated_blocks", "value": len(blocks),
                       "threshold": 1, "advice": dup["advice"], "waived": bool(waived(rel, "code_duplication")),
                       "blocks": blocks})
    return {"file": rel, "language": lang, "nloc": info.nloc, "score": score(smells), "band": None,
            "functions": functions, "smells": smells, "blockers": blockers_in(rel, code)}


def score(smells: list[dict]) -> float:
    penalty = 0.0
    weights = RULES["penalty"]
    for s in smells:
        if s.get("waived"):
            continue
        rule = RULES["smells"][s["smell"]]
        if s["smell"] == "code_duplication":
            penalty += min(rule["max_penalty"], rule["weight"] * s["value"] * weights["warning"])
        else:
            penalty += weights[s["severity"]] * rule["weight"]
    return round(max(1.0, 10.0 - penalty), 1)


def band(value: float) -> str:
    b = RULES["bands"]
    return "healthy" if value >= b["healthy"] else "problematic" if value >= b["problematic"] else "unhealthy"


def full(rel: str, code: str | None = None) -> dict:
    result = analyze(rel, code)
    result["band"] = band(result["score"])
    return result


def at_revision(rel: str, rev: str) -> dict | None:
    content = git("show", f"{rev}:{rel}")
    return None if content is None else full(rel, content)


def project(files: list[str]) -> dict:
    results = [full(f) for f in files]
    total = sum(r["nloc"] for r in results) or 1
    avg = round(sum(r["score"] * r["nloc"] for r in results) / total, 2) if results else 10.0
    blockers = [b for r in results for b in r["blockers"]]
    return {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "root": str(ROOT), "files_scanned": len(results), "code_health_avg": avg,
            "code_health_min": min((r["score"] for r in results), default=10.0),
            "bands": {k: sum(1 for r in results if r["band"] == k) for k in ("healthy", "problematic", "unhealthy")},
            "blockers_open": {s: sum(1 for b in blockers if b["severity"] == s and b["status"] == "open")
                              for s in ("B0", "B1", "B2", "B3")},
            "files": results, "blockers": blockers}


def compare(pairs: list[tuple[str, dict | None, dict | None]]) -> dict:
    tolerance, healthy = RULES.get("regression_tolerance", 0.0), RULES["bands"]["healthy"]
    rows, regressions = [], []
    for rel, before, after in pairs:
        if after is None:
            continue
        row = {"file": rel, "before": before["score"] if before else None, "after": after["score"]}
        if before is not None and after["score"] < before["score"] - tolerance:
            row["regression"] = "score en baisse"
        elif before is None and after["score"] < healthy:
            row["regression"] = f"nouveau fichier sous le seuil {healthy}"
        new_smells = {(s["smell"], s["function"]) for s in after["smells"]} - \
                     ({(s["smell"], s["function"]) for s in before["smells"]} if before else set())
        row["new_smells"] = sorted(f"{a}{'@' + b if b else ''}" for a, b in new_smells)
        rows.append(row)
        if "regression" in row:
            regressions.append(row)
    return {"files": rows, "regressions": regressions, "pass": not regressions}


# --------------------------------------------------------------------------- commandes

def cmd_delta(base: str) -> dict:
    changed = (git("diff", "--name-only", "--diff-filter=ACMR", base) or "").splitlines()
    changed += (git("ls-files", "--others", "--exclude-standard") or "").splitlines()
    files = sorted({f for f in changed if is_source(f) and (ROOT / f).is_file()})
    result = compare([(f, at_revision(f, base), full(f)) for f in files])
    result["base"] = base
    return result


def cmd_safeguard() -> dict:
    staged = [f for f in (git("diff", "--cached", "--name-only", "--diff-filter=ACMR") or "").splitlines() if is_source(f)]
    pairs = []
    for rel in staged:
        content = git("show", f":{rel}")
        pairs.append((rel, at_revision(rel, "HEAD"), full(rel, content) if content is not None else None))
    return compare(pairs)


def cmd_hotspots(since: str, top: int) -> dict:
    log = git("log", f"--since={since}", "--format=", "--name-only")
    if log is None:
        return {"error": "dépôt git requis pour l'analyse des hotspots", "hotspots": []}
    churn: dict[str, int] = {}
    for line in (l.strip() for l in log.splitlines()):
        if line and is_source(line) and (ROOT / line).is_file():
            churn[line] = churn.get(line, 0) + 1
    rows = []
    for rel, commits in sorted(churn.items(), key=lambda kv: -kv[1])[:top]:
        s = full(rel)["score"]
        rows.append({"file": rel, "commits": commits, "score": s, "priority": round(commits * (11 - s), 1)})
    return {"since": since, "hotspots": sorted(rows, key=lambda r: -r["priority"])}


def text_review(r: dict) -> str:
    lines = [f"Code Health de {r['file']} : {r['score']} ({r['band']}), {r['nloc']} lignes utiles"]
    for s in r["smells"]:
        where = f" dans {s['function']}" if s["function"] else ""
        lines.append(f"  - {s['label']}{where} (ligne {s['line']}) : {s['metric']}={s['value']} "
                     f"≥ {s['threshold']} [{s['severity']}{', dérogé' if s['waived'] else ''}] → {s['advice']}")
    for b in r["blockers"]:
        lines.append(f"  ! {b['id']} {b['severity']} {b['category']} {b['location']} : {b['title']} [{b['status']}]")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Moteur Code Health local (référentiel ecom-modernizer)")
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("score", "review"):
        sub.add_parser(name).add_argument("file")
    p = sub.add_parser("scan"); p.add_argument("paths", nargs="*"); p.add_argument("--out")
    p.add_argument("--write-baseline", action="store_true")
    p = sub.add_parser("delta"); p.add_argument("--base", default="HEAD")
    sub.add_parser("safeguard")
    p = sub.add_parser("blockers"); p.add_argument("paths", nargs="*")
    p = sub.add_parser("hotspots"); p.add_argument("--since", default=RULES["hotspots"]["since"])
    p.add_argument("--top", type=int, default=RULES["hotspots"]["top"])
    args = parser.parse_args(argv)

    if args.cmd in ("score", "review"):
        result = full(rel_path(args.file))
        if args.cmd == "score":
            result = {k: result[k] for k in ("file", "score", "band", "nloc")} | {"smells": len(result["smells"])}
            text = f"Code Health de {result['file']} : {result['score']} ({result['band']})"
        else:
            text = text_review(result)
    elif args.cmd == "scan":
        result = project(source_files(args.paths or None))
        if args.out:
            Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.write_baseline:
            baseline = {"generated_at": result["generated_at"], "code_health_avg": result["code_health_avg"],
                        "files": {r["file"]: r["score"] for r in result["files"]}}
            (HERE / "baseline.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
        text = (f"{result['files_scanned']} fichiers · Code Health moyenne {result['code_health_avg']} · "
                f"min {result['code_health_min']} · bloqueurs ouverts {result['blockers_open']}")
    elif args.cmd == "delta":
        result = cmd_delta(args.base)
        text = f"{len(result['files'])} fichiers modifiés depuis {args.base} · régressions : {len(result['regressions'])}"
    elif args.cmd == "safeguard":
        result = cmd_safeguard()
        text = "OK : aucune régression" if result["pass"] else f"Refus : {len(result['regressions'])} régression(s)"
    elif args.cmd == "blockers":
        result = {"blockers": [b for f in source_files(args.paths or None) for b in blockers_in(f, read(f))]}
        text = "\n".join(f"{b['id']} {b['severity']} {b['location']} : {b['title']} [{b['status']}]"
                         for b in result["blockers"]) or "Aucun bloqueur détecté par les règles"
    else:
        result = cmd_hotspots(args.since, args.top)
        text = "\n".join(f"{h['priority']:>6}  {h['commits']:>3} commits  {h['score']:>4}  {h['file']}"
                         for h in result.get("hotspots", [])) or result.get("error", "Aucun hotspot")

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else text)
    if args.cmd == "safeguard" and not result["pass"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
