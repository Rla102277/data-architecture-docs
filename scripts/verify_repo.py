#!/usr/bin/env python3
"""Structural checks for the factory. Standard library only. Run before every commit.

    python3 scripts/verify_repo.py

Errors (exit 1):
- generated files out of date (scripts/build.py --check)
- any symlink in the repo
- marketplace entries that do not resolve, or names that disagree with plugin.json
- plugins missing a Claude or Cursor manifest, or manifest paths that do not exist
- any skill without name/description, bad names, duplicate names across all plugins
- first-party skills (plugins with plugin.meta.json) that break factory/SKILL_STANDARD.md:
  name != folder, description not starting "Use when", required sections missing or
  out of order, no doctrine link, over 500 lines, broken links, em dashes, no eval scenario
- agents without front matter (name = file name, description)
- eval scenarios that are invalid JSON or point at a skill that does not exist
- vendored plugins without UPSTREAM.md and LICENSE
Warnings: vendored skill issues (fix upstream, then sync).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
SECTIONS = ["When to use", "Inspect first", "Procedure", "Standards", "Failure modes", "Verify", "Output"]


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

    for p in ROOT.rglob("*"):
        if ".git" not in p.parts and p.is_symlink():
            errors.append(f"{p.relative_to(ROOT)}: symlink (hosts skip or mishandle them)")

    for host in (".claude-plugin", ".cursor-plugin"):
        for e in json.loads((ROOT / host / "marketplace.json").read_text())["plugins"]:
            pm = (ROOT / e["source"]).resolve() / host / "plugin.json"
            if not pm.exists():
                errors.append(f"{host}/marketplace.json: {e['name']} has no {host}/plugin.json")
            elif json.loads(pm.read_text())["name"] != e["name"]:
                errors.append(f"{host}/marketplace.json: {e['name']} disagrees with its plugin.json")

    scenarios: dict[str, set[str]] = {}
    for f in sorted((ROOT / "evals" / "scenarios").rglob("*.json")):
        try:
            d = json.loads(f.read_text())
            scenarios.setdefault(d["plugin"], set()).add(d["skill"])
            assert d["scenarios"] and all("prompt" in s and "must_include" in s for s in d["scenarios"])
        except (json.JSONDecodeError, KeyError, AssertionError):
            errors.append(f"{f.relative_to(ROOT)}: invalid scenario file")

    names: dict[str, str] = {}
    first_party_count = 0
    for pdir in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        first = (pdir / "plugin.meta.json").exists()
        bucket = errors if first else warnings
        for host in (".claude-plugin", ".cursor-plugin"):
            pm = pdir / host / "plugin.json"
            if not pm.exists():
                errors.append(f"plugins/{pdir.name}: missing {host}/plugin.json")
                continue
            m = json.loads(pm.read_text())
            if m["name"] != pdir.name or not NAME_RE.match(m["name"]):
                errors.append(f"plugins/{pdir.name}/{host}: name must match folder, kebab-case")
            for key in ("skills", "agents", "rules", "logo", "icon"):
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
                errors.append(f"{rel}: bad name, or description over 1024 characters")
            if name in names:
                errors.append(f"{rel}: duplicate skill name '{name}' (also {names[name]})")
            names[name] = rel
            if name != skill_md.parent.name:
                bucket.append(f"{rel}: name '{name}' != folder '{skill_md.parent.name}'")
            for link in LINK_RE.findall(text):
                if not re.match(r"^[a-z]+:", link) and not (skill_md.parent / link).exists():
                    bucket.append(f"{rel}: broken link {link}")
            if not first:
                continue
            first_party_count += 1
            if not desc.startswith("Use when"):
                errors.append(f"{rel}: description must start with 'Use when'")
            found = re.findall(r"^## (.+?)\s*$", text, re.M)
            positions = [found.index(s) if s in found else -1 for s in SECTIONS]
            missing = [s for s, pos in zip(SECTIONS, positions) if pos < 0]
            if missing:
                errors.append(f"{rel}: missing sections {missing}")
            elif positions != sorted(positions):
                errors.append(f"{rel}: required sections out of order")
            if "references/doctrine.md" not in text:
                errors.append(f"{rel}: must link references/doctrine.md")
            if len(text.splitlines()) > 500:
                errors.append(f"{rel}: over 500 lines")
            if name not in scenarios.get(pdir.name, set()):
                errors.append(f"{rel}: no eval scenario in evals/scenarios/{pdir.name}/{name}.json")
            for f in skill_md.parent.rglob("*"):
                if f.is_file() and f.suffix in {".md", ".py", ".sql", ".yml", ".yaml", ".tmpl", ".json"} \
                        and chr(0x2014) in f.read_text(encoding="utf-8", errors="ignore"):
                    errors.append(f"{f.relative_to(ROOT)}: em dash")

        agents = pdir / "agents"
        if agents.is_dir():
            for a in sorted(agents.glob("*.md")):
                fm = front_matter(a.read_text(encoding="utf-8"))
                if not fm or fm.get("name") != a.stem or not fm.get("description"):
                    errors.append(f"{a.relative_to(ROOT)}: agent front matter needs name (= file name) and description")

    for plugin, skills in scenarios.items():
        for s in skills:
            if not (PLUGINS / plugin / "skills").exists() or s not in names:
                errors.append(f"evals/scenarios/{plugin}/{s}.json: no such skill")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(names)} skills ({first_party_count} first-party), {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
