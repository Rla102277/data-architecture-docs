#!/usr/bin/env python3
"""Structural checks for this marketplace repo. Standard library only.

    python3 scripts/verify_repo.py

Errors (exit 1):
- generated files out of date (scripts/build.py --check)
- marketplace entries that do not resolve, or names that disagree with plugin.json
- plugins missing a Claude or Cursor manifest, or manifest paths that do not exist
- skills without name/description, bad names, duplicate names across plugins
- first-party skills: name != folder, over 500 lines, broken links, missing conventions copy
- agents without valid front matter, or name != file name
- vendored plugins without UPSTREAM.md and LICENSE
- any symlink in the repo
Warnings: vendored skill issues (fix upstream).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST_PARTY = "data-architecture-docs"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def front_matter(text: str) -> dict[str, str] | None:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm: dict[str, str] = {}
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            key, val = km.group(1), km.group(2).strip()
            if val.startswith('"'):
                try:
                    val = json.loads(val)
                except json.JSONDecodeError:
                    return None
            fm[key] = "" if val in (">-", ">", "|", "|-") else val
        elif key and line.startswith(" "):
            fm[key] = (fm[key] + " " + line.strip()).strip()
        elif line.strip():
            return None
    return fm


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    r = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "build.py"), "--check"],
                       capture_output=True, text=True)
    if r.returncode:
        errors.extend(line for line in r.stdout.splitlines() if line.strip())

    for link in ROOT.rglob("*"):
        if ".git" not in link.parts and link.is_symlink():
            errors.append(f"{link.relative_to(ROOT)}: symlink (not allowed; hosts skip or mishandle them)")

    for host in (".claude-plugin", ".cursor-plugin"):
        mp = ROOT / host / "marketplace.json"
        data = json.loads(mp.read_text())
        for e in data["plugins"]:
            pdir = (ROOT / e["source"]).resolve()
            pm = pdir / host / "plugin.json"
            if not pm.exists():
                errors.append(f"{host}/marketplace.json: {e['name']} -> {e['source']} has no {host}/plugin.json")
            elif json.loads(pm.read_text())["name"] != e["name"]:
                errors.append(f"{host}/marketplace.json: {e['name']} disagrees with its plugin.json name")

    skill_names: dict[str, str] = {}
    for pdir in sorted((ROOT / "plugins").iterdir()):
        first = pdir.name == FIRST_PARTY
        bucket = errors if first else warnings
        for host in (".claude-plugin", ".cursor-plugin"):
            pm = pdir / host / "plugin.json"
            if not pm.exists():
                errors.append(f"plugins/{pdir.name}: missing {host}/plugin.json")
                continue
            m = json.loads(pm.read_text())
            if m["name"] != pdir.name or not NAME_RE.match(m["name"]):
                errors.append(f"plugins/{pdir.name}/{host}: name '{m['name']}' must match folder, kebab-case")
            for key in ("skills", "agents", "rules"):
                vals = m.get(key)
                for v in ([vals] if isinstance(vals, str) else vals or []):
                    if not (pdir / v).exists():
                        errors.append(f"plugins/{pdir.name}/{host}: {key} path {v} does not exist")
        if not first:
            for req in ("UPSTREAM.md", "LICENSE"):
                if not (pdir / req).exists():
                    errors.append(f"plugins/{pdir.name}: missing {req}")

        for skill_md in sorted((pdir / "skills").rglob("SKILL.md")):
            rel = str(skill_md.relative_to(ROOT))
            text = skill_md.read_text(encoding="utf-8")
            fm = front_matter(text) or {}
            name, desc = fm.get("name", ""), fm.get("description", "")
            if not name or not desc:
                errors.append(f"{rel}: front matter needs name and description")
                continue
            if not NAME_RE.match(name) or len(name) > 64 or len(desc) > 1024:
                errors.append(f"{rel}: bad name or description over 1024 chars")
            if name in skill_names:
                errors.append(f"{rel}: duplicate skill name '{name}' (also {skill_names[name]})")
            skill_names[name] = rel
            if name != skill_md.parent.name:
                bucket.append(f"{rel}: name '{name}' != folder '{skill_md.parent.name}'")
            for link in LINK_RE.findall(text):
                if not re.match(r"^[a-z]+:", link) and not (skill_md.parent / link).exists():
                    bucket.append(f"{rel}: broken link {link}")
            if first:
                if len(text.splitlines()) > 500:
                    errors.append(f"{rel}: over 500 lines")
                if not (skill_md.parent / "references" / "conventions.md").exists():
                    errors.append(f"{rel}: missing references/conventions.md (run scripts/build.py)")
                if "\u2014" in text:
                    errors.append(f"{rel}: em dash")

        agents = pdir / "agents"
        if agents.is_dir():
            for a in sorted(agents.glob("*.md")):
                fm = front_matter(a.read_text(encoding="utf-8"))
                if not fm or fm.get("name") != a.stem or not fm.get("description"):
                    errors.append(f"{a.relative_to(ROOT)}: agent front matter needs name (= file name) and description")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(skill_names)} skills, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
