#!/usr/bin/env python3
"""Run skill evals: each scenario with and without its plugin, graded by patterns.

    python3 scripts/run_evals.py --dry-run                         # list runs, spend nothing
    python3 scripts/run_evals.py --plugin de-reverse-engineering   # one plugin
    python3 scripts/run_evals.py --plugin de-dbt --skill dbt-model-development --repeat 3
    python3 scripts/run_evals.py --no-baseline --model sonnet

Needs the Claude Code CLI, signed in (`claude -p` headless mode). Each run happens
in a fresh temporary folder (with the scenario's fixture copied in), with
read-only tools (Read, Grep, Glob). Writes evals/results/<stamp>.json, .md and
transcripts/. Standard library only.

Scenario file: evals/scenarios/<plugin>/<skill>.json
  {"skill": "...", "plugin": "...", "scenarios": [
     {"id": "...", "prompt": "...", "fixture": "evals/fixtures/<dir>" | null,
      "must_include": ["regex", ...], "must_not_include": ["regex", ...]}]}

Score per run = (must_include hits / total) - 0.25 x must_not_include hits, floored at 0.
Lift = with-plugin score - baseline score. Regex grading is a screen: read transcripts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "evals" / "scenarios"
OUT = ROOT / "evals" / "results"
PENALTY = 0.25


def grade(text: str, must: list[str], must_not: list[str]) -> dict:
    hits = [p for p in must if re.search(p, text, re.I | re.M)]
    bad = [p for p in must_not if re.search(p, text, re.I | re.M)]
    base = len(hits) / len(must) if must else 1.0
    return {"score": round(max(0.0, base - PENALTY * len(bad)), 3),
            "hits": hits, "missed": [p for p in must if p not in hits], "violations": bad}


def load(plugin: str | None, skill: str | None) -> list[dict]:
    items = []
    for f in sorted(SCEN.rglob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        if plugin and data["plugin"] != plugin:
            continue
        if skill and data["skill"] != skill:
            continue
        for s in data["scenarios"]:
            if any("{{" in str(v) for v in s.values()):
                continue  # unfilled template
            items.append({**s, "skill": data["skill"], "plugin": data["plugin"], "file": str(f.relative_to(ROOT))})
    return items


def command(s: dict, with_plugin: bool, model: str | None) -> list[str]:
    cmd = ["claude", "-p", s["prompt"], "--output-format", "text", "--allowedTools", "Read", "Grep", "Glob"]
    if with_plugin:
        cmd += ["--plugin-dir", str(ROOT / "plugins" / s["plugin"])]
        if s["plugin"] != "data-warrior" and (ROOT / "plugins" / "data-warrior").exists():
            cmd += ["--plugin-dir", str(ROOT / "plugins" / "data-warrior")]
    if model:
        cmd += ["--model", model]
    return cmd


def run_one(s: dict, with_plugin: bool, model: str | None, timeout: int) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        if s.get("fixture"):
            shutil.copytree(ROOT / s["fixture"], tmp, dirs_exist_ok=True)
        try:
            r = subprocess.run(command(s, with_plugin, model), cwd=tmp, capture_output=True,
                               text=True, timeout=timeout)
            return r.stdout + ("\n[stderr]\n" + r.stderr if r.returncode else "")
        except subprocess.TimeoutExpired:
            return "[timeout]"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plugin")
    ap.add_argument("--skill")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--no-baseline", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    scenarios = load(args.plugin, args.skill)
    if not scenarios:
        print("No filled scenarios match.")
        return 1
    modes = [True] if args.no_baseline else [True, False]
    total = len(scenarios) * len(modes) * args.repeat
    print(f"{len(scenarios)} scenarios x {len(modes)} modes x {args.repeat} repeats = {total} headless runs")
    if args.dry_run:
        for s in scenarios:
            for m in modes:
                print(("PLUGIN   " if m else "BASELINE ") + " ".join(
                    c if " " not in c else repr(c) for c in command(s, m, args.model)[:4]) + " ...")
        return 0
    if not shutil.which("claude"):
        sys.exit("Claude Code CLI not found. Install it and sign in, or use --dry-run.")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    tdir = OUT / stamp / "transcripts"
    tdir.mkdir(parents=True, exist_ok=True)
    results = []
    for s in scenarios:
        row = {"id": s["id"], "skill": s["skill"], "plugin": s["plugin"]}
        for m in modes:
            key = "with_plugin" if m else "baseline"
            scores = []
            for i in range(args.repeat):
                text = run_one(s, m, args.model, args.timeout)
                (tdir / f"{s['id']}__{key}__{i + 1}.txt").write_text(text, encoding="utf-8")
                g = grade(text, s.get("must_include", []), s.get("must_not_include", []))
                scores.append(g["score"])
                row.setdefault(f"{key}_details", []).append(g)
            row[key] = round(sum(scores) / len(scores), 3)
        if not args.no_baseline:
            row["lift"] = round(row["with_plugin"] - row["baseline"], 3)
        results.append(row)
        print(f"{s['id']}: {row.get('with_plugin')} vs {row.get('baseline', '-')} lift {row.get('lift', '-')}")

    (OUT / stamp / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = [f"# Eval results {stamp}", "", "| Scenario | Skill | With plugin | Baseline | Lift |", "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['id']} | {r['skill']} | {r['with_plugin']} | {r.get('baseline', '-')} | {r.get('lift', '-')} |")
    lines += ["", "Regex grading is a screen. Read the transcripts in `transcripts/` before concluding."]
    (OUT / stamp / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report: {(OUT / stamp / 'results.md').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
