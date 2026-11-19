#!/usr/bin/env python3
"""Vendor upstream skill repos as plugins under plugins/<plugin>/.

    python3 scripts/sync_upstream.py                 # all upstreams
    python3 scripts/sync_upstream.py data-warrior    # one
    python3 scripts/sync_upstream.py data-warrior --from /path/to/local/clone

Upstream stays canonical. Never hand-edit a vendored plugin; change upstream and
re-run. Writes skills/, extras, UPSTREAM.md and both plugin manifests
(.claude-plugin/plugin.json, .cursor-plugin/plugin.json). Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONF = ROOT / "scripts" / "upstreams.json"


def skill_dirs(src: Path) -> list[Path]:
    found = []
    for skill_md in sorted(src.rglob("SKILL.md")):
        rel = skill_md.relative_to(src)
        if any(part.startswith(".") for part in rel.parts):
            continue
        found.append(skill_md.parent)
    return found


def sync(up: dict, local: str | None) -> None:
    name = up["plugin"]
    dest = ROOT / "plugins" / name
    with tempfile.TemporaryDirectory() as tmp:
        if local:
            repo = Path(local).resolve()
        else:
            repo = Path(tmp) / "src"
            subprocess.run(["git", "clone", "--quiet", "--depth", "1", up["repo"], str(repo)], check=True)
        commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True).stdout.strip() or "unknown"
        src = (repo / up["skills_dir"]).resolve()

        if dest.exists():
            shutil.rmtree(dest)
        (dest / "skills").mkdir(parents=True)
        paths = []
        for d in skill_dirs(src):
            rel = d.relative_to(src)
            shutil.copytree(d, dest / "skills" / rel, symlinks=False)
            paths.append(f"./skills/{rel.as_posix()}")
        # bucket READMEs (data-warrior groups skills in ring folders)
        for readme in src.glob("*/README.md"):
            target = dest / "skills" / readme.relative_to(src)
            if target.parent.exists():
                shutil.copy2(readme, target)
        for extra in up.get("extras", []):
            p = repo / extra
            if p.is_file():
                shutil.copy2(p, dest / p.name)

    today = dt.date.today().isoformat()
    (dest / "UPSTREAM.md").write_text(
        f"# Upstream: {name}\n\n"
        f"Vendored from {up['repo']} at commit `{commit}` on {today}.\n\n"
        f"Do not edit files in this plugin. Change them upstream and run "
        f"`python3 scripts/sync_upstream.py {name}`. License: see LICENSE here.\n",
        encoding="utf-8")

    base = {
        "name": name,
        "version": f"0.0.0-upstream.{commit}",
        "description": up["description"],
        "author": {"name": up["author"]},
        "repository": up["repo"].removesuffix(".git"),
        "license": up["license"],
        "keywords": up.get("keywords", []),
    }
    nested = any(p.count("/") > 2 for p in paths)
    claude = dict(base)
    cursor = dict(base, displayName=name.replace("-", " ").title())
    if nested:  # explicit list so nested bucket folders are found by both hosts
        claude["skills"] = paths
        cursor["skills"] = paths
    for folder, manifest in ((".claude-plugin", claude), (".cursor-plugin", cursor)):
        (dest / folder).mkdir(exist_ok=True)
        (dest / folder / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{name}: {len(paths)} skills from {commit}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plugin", nargs="?")
    ap.add_argument("--from", dest="local")
    args = ap.parse_args()
    ups = json.loads(CONF.read_text())["upstreams"]
    if args.plugin:
        ups = [u for u in ups if u["plugin"] == args.plugin]
        if not ups:
            print(f"unknown upstream {args.plugin}", file=sys.stderr)
            return 2
    if args.local and len(ups) != 1:
        print("--from needs a single upstream name", file=sys.stderr)
        return 2
    for up in ups:
        sync(up, args.local)
    return 0


if __name__ == "__main__":
    sys.exit(main())
