#!/usr/bin/env python3
"""Install the plugins in this repo. Standard library only.

Cursor (local plugins; Cursor skips symlinks, so this copies):
    python3 scripts/install.py cursor
    python3 scripts/install.py cursor --plugins data-architecture-docs

Claude Code (adds this checkout as a marketplace and installs the plugins):
    python3 scripts/install.py claude

Skills only, into one project or your user folder (Codex, or no plugin support):
    python3 scripts/install.py skills --target ~/code/my-project --tool claude
    python3 scripts/install.py skills --global --tool codex

--plugins takes a comma list. Default: every plugin under plugins/.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
MARKETPLACE = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())["name"]
SKILL_DIRS = {"claude": ".claude/skills", "cursor": ".cursor/skills", "codex": ".agents/skills"}
AGENT_DIRS = {"claude": ".claude/agents", "cursor": ".cursor/agents"}
USER_SKILLS = {"claude": "~/.claude/skills", "cursor": "~/.cursor/skills", "codex": "~/.codex/skills"}
USER_AGENTS = {"claude": "~/.claude/agents", "cursor": "~/.cursor/agents"}
IGNORE = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store")


def pick(names: str | None) -> list[Path]:
    available = {p.name: p for p in sorted(PLUGINS.iterdir()) if (p / ".claude-plugin").is_dir()}
    if not names:
        return list(available.values())
    chosen = []
    for n in names.split(","):
        n = n.strip()
        if n not in available:
            sys.exit(f"Unknown plugin '{n}'. Available: {', '.join(available)}")
        chosen.append(available[n])
    return chosen


def install_cursor(plugins: list[Path]) -> None:
    base = Path("~/.cursor/plugins/local").expanduser()
    base.mkdir(parents=True, exist_ok=True)
    for p in plugins:
        dest = base / p.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(p, dest, symlinks=False, ignore=IGNORE)
        print(f"Cursor: {p.name} -> {dest}")
    print("Next: Cursor > Developer: Reload Window, then check Customize for the plugins.")
    job = base / "de-factory-line" / "skills" / "run-factory-job" / "scripts" / "job.py"
    if job.exists():
        print(f"Job line: add to ~/.zshrc ->  alias job='python3 {job}'")


def install_claude(plugins: list[Path]) -> None:
    cmds = [["claude", "plugin", "marketplace", "add", str(ROOT)]]
    cmds += [["claude", "plugin", "install", f"{p.name}@{MARKETPLACE}"] for p in plugins]
    if not shutil.which("claude"):
        print("Claude Code CLI not found. Run these yourself:")
        for c in cmds:
            print("  " + " ".join(c))
        return
    for c in cmds:
        print("$ " + " ".join(c))
        subprocess.run(c, check=False)


def skill_folders(plugin: Path) -> list[Path]:
    return sorted(s.parent for s in (plugin / "skills").rglob("SKILL.md"))


def install_skills(plugins: list[Path], tool: str, target: str | None, global_: bool) -> None:
    if global_:
        sdir = Path(USER_SKILLS[tool]).expanduser()
        adir = Path(USER_AGENTS[tool]).expanduser() if tool in USER_AGENTS else None
    else:
        root = Path(target).expanduser().resolve()
        if not root.is_dir():
            sys.exit(f"Target not found: {root}")
        sdir = root / SKILL_DIRS[tool]
        adir = root / AGENT_DIRS[tool] if tool in AGENT_DIRS else None
    sdir.mkdir(parents=True, exist_ok=True)
    for p in plugins:
        way = p / "THE_WAY.md"
        count = 0
        for folder in skill_folders(p):
            dest = sdir / folder.name  # flatten bucket folders; names are unique
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(folder, dest, symlinks=False, ignore=IGNORE)
            if way.exists():  # Data Warrior skills say "follow THE_WAY.md"
                shutil.copy2(way, dest / "THE_WAY.md")
            count += 1
        print(f"{p.name}: {count} skills -> {sdir}")
        agents = p / "agents"
        if agents.is_dir():
            if adir is None:
                print(f"  {tool} has no subagent folder; reviewers skipped (skills fall back to single-agent review)")
                continue
            adir.mkdir(parents=True, exist_ok=True)
            for a in sorted(agents.glob("*.md")):
                shutil.copy2(a, adir / a.name)
            print(f"  {len(list(agents.glob('*.md')))} reviewer agents -> {adir}")
    print("Install for one of claude or cursor per project, not both: Cursor also reads .claude/, and would list everything twice.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["cursor", "claude", "skills"])
    ap.add_argument("--plugins")
    ap.add_argument("--tool", choices=list(SKILL_DIRS), default="claude")
    ap.add_argument("--target")
    ap.add_argument("--global", dest="global_", action="store_true")
    args = ap.parse_args()
    plugins = pick(args.plugins)
    if args.mode == "cursor":
        install_cursor(plugins)
    elif args.mode == "claude":
        install_claude(plugins)
    else:
        if bool(args.target) == args.global_:
            sys.exit("skills mode needs exactly one of --target <project> or --global")
        install_skills(plugins, args.tool, args.target, args.global_)
    return 0


if __name__ == "__main__":
    sys.exit(main())
