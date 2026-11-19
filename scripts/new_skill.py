#!/usr/bin/env python3
"""Scaffold a new first-party skill and its eval scenario. Standard library only.

    python3 scripts/new_skill.py --plugin de-dbt --name dbt-snapshots \
        --trigger "tracking history of mutable source tables with dbt snapshots"

Creates plugins/<plugin>/skills/<name>/SKILL.md from factory/templates/SKILL.md.tmpl,
evals/scenarios/<plugin>/<name>.json from factory/templates/eval.json.tmpl, then
runs scripts/build.py so doctrine and the catalog are generated. Refuses to
overwrite and refuses names already used by any skill in the repo.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plugin", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--trigger", required=True, help="when to use it, in the user's words")
    ap.add_argument("--title")
    args = ap.parse_args()

    plugin = ROOT / "plugins" / args.plugin
    if not (plugin / "plugin.meta.json").exists():
        sys.exit(f"{args.plugin} is not a first-party plugin (no plugin.meta.json). "
                 f"Create plugins/{args.plugin}/plugin.meta.json first, or pick an existing plugin.")
    if not NAME_RE.match(args.name) or len(args.name) > 64:
        sys.exit("name must be kebab-case, 64 characters or fewer")
    taken = {p.parent.name for p in (ROOT / "plugins").rglob("SKILL.md")}
    if args.name in taken:
        sys.exit(f"a skill named {args.name} already exists")

    skill = plugin / "skills" / args.name
    (skill / "references").mkdir(parents=True)
    title = args.title or args.name.replace("-", " ").title()
    tmpl = (ROOT / "factory" / "templates" / "SKILL.md.tmpl").read_text(encoding="utf-8")
    body = (tmpl.replace("{{name}}", args.name)
                .replace("{{title}}", title)
                .replace("{{trigger}}", args.trigger.rstrip(".")))
    (skill / "SKILL.md").write_text(body, encoding="utf-8")

    evals = ROOT / "evals" / "scenarios" / args.plugin
    evals.mkdir(parents=True, exist_ok=True)
    scenario = json.loads((ROOT / "factory" / "templates" / "eval.json.tmpl").read_text(encoding="utf-8")
                          .replace("{{name}}", args.name).replace("{{plugin}}", args.plugin))
    (evals / f"{args.name}.json").write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py")], check=True)
    print(f"Created {skill.relative_to(ROOT)}/SKILL.md and {(evals / (args.name + '.json')).relative_to(ROOT)}")
    print("Next: replace every {{...}} placeholder, then run python3 scripts/verify_repo.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
