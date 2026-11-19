#!/usr/bin/env python3
"""Structural checks for this skills repo. Standard library only.

    python3 scripts/verify_repo.py

Checks every SKILL.md under skills/: front matter name + description, name
format, name matches its folder, unique names, description length, relative
links resolve (errors for first-party skills, warnings for vendored ones),
first-party SKILL.md under 500 lines, vendored folders carry UPSTREAM.md and
LICENSE, and repo symlinks resolve. Exit 1 on any error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FIRST_PARTY = {"data-architecture-docs"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def front_matter(text: str) -> dict[str, str]:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    fm: dict[str, str] = {}
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            key = km.group(1)
            val = km.group(2).strip()
            fm[key] = "" if val in (">-", ">", "|", "|-") else val
        elif key and line.startswith(" "):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    names: dict[str, Path] = {}

    for skill_md in sorted(SKILLS.rglob("SKILL.md")):
        rel = skill_md.relative_to(ROOT)
        top = skill_md.relative_to(SKILLS).parts[0]
        first_party = top in FIRST_PARTY
        text = skill_md.read_text(encoding="utf-8")
        fm = front_matter(text)
        name, desc = fm.get("name", ""), fm.get("description", "")
        if not name or not desc:
            errors.append(f"{rel}: front matter needs name and description")
            continue
        if not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{rel}: bad skill name '{name}'")
        if name != skill_md.parent.name:
            (errors if first_party else warnings).append(
                f"{rel}: name '{name}' does not match folder '{skill_md.parent.name}'")
        if len(desc) > 1024:
            errors.append(f"{rel}: description over 1024 chars")
        if name in names:
            errors.append(f"{rel}: duplicate skill name '{name}' (also {names[name]})")
        names[name] = rel
        if first_party and len(text.splitlines()) > 500:
            errors.append(f"{rel}: over 500 lines")
        for link in LINK_RE.findall(text):
            if re.match(r"^[a-z]+:", link):
                continue
            if not (skill_md.parent / link).exists():
                (errors if first_party else warnings).append(f"{rel}: broken link {link}")

    for vendored in sorted(p for p in SKILLS.iterdir() if p.is_dir() and p.name not in FIRST_PARTY):
        for req in ("UPSTREAM.md", "LICENSE"):
            if not (vendored / req).exists():
                errors.append(f"skills/{vendored.name}: missing {req}")

    for link in ROOT.rglob("*"):
        if ".git" in link.parts:
            continue
        if link.is_symlink() and not link.exists():
            errors.append(f"{link.relative_to(ROOT)}: broken symlink")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(names)} skills, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
