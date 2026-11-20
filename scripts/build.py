#!/usr/bin/env python3
"""Build every generated file in the factory. Standard library only.

    python3 scripts/build.py          # write generated files
    python3 scripts/build.py --check  # exit 1 if anything is out of date (CI)

A first-party plugin is any plugins/<name>/ with a plugin.meta.json. For each:
- every skill gets references/doctrine.md (from factory/doctrine.md), plus any
  files named in plugin.meta.json "build.references" ({name: source path}, copied
  into references/) or "build.files" ({path inside skill: source path})
- .claude-plugin/plugin.json and .cursor-plugin/plugin.json are generated from
  plugin.meta.json (agents/ and rules/ are wired in automatically)
Across the repo:
- .claude-plugin/marketplace.json and .cursor-plugin/marketplace.json
- catalog/SKILLS.md and catalog/skills.json (every skill in every plugin)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
DOCTRINE = ROOT / "factory" / "doctrine.md"
MARKET = ROOT / "marketplace.meta.json"
ORDER = [
    "de-reverse-engineering", "de-modernization", "de-sql", "de-dbt", "de-modeling", "de-pipelines",
    "de-platforms", "de-quality-ops", "de-architecture-docs", "de-factory-line", "de-skill-factory",
    "data-warrior", "gordonmurray-data-engineering",
]


def j(obj: object) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def front_matter(text: str) -> dict[str, str]:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    fm: dict[str, str] = {}
    if not m:
        return fm
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            key, val = km.group(1), km.group(2).strip()
            fm[key] = "" if val in (">-", ">", "|", "|-") else val.strip('"')
        elif key and line.startswith(" "):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def first_party() -> list[Path]:
    return sorted(p for p in PLUGINS.iterdir() if (p / "plugin.meta.json").exists())


def plugin_sort(name: str) -> tuple[int, str]:
    return (ORDER.index(name) if name in ORDER else len(ORDER), name)


def targets() -> dict[Path, str]:
    out: dict[Path, str] = {}
    doctrine = DOCTRINE.read_text(encoding="utf-8")
    manifests: dict[str, dict] = {}

    for plugin in first_party():
        meta = json.loads((plugin / "plugin.meta.json").read_text(encoding="utf-8"))
        build = meta.get("build", {})
        extra = {f"references/{t}": s for t, s in build.get("references", {}).items()}
        extra.update(build.get("files", {}))  # {"assets/x.tmpl": "factory/templates/x.tmpl"}
        extra_content = {t: (ROOT / s).read_text(encoding="utf-8") for t, s in extra.items()}
        for skill in sorted((plugin / "skills").iterdir()):
            if (skill / "SKILL.md").exists():
                out[skill / "references" / "doctrine.md"] = doctrine
                for target, content in extra_content.items():
                    out[skill / target] = content

        common = {k: v for k, v in meta.items()
                  if not k.startswith("_") and k not in ("claude", "cursor", "build", "category")}
        claude = dict(common)
        cursor = dict(common, displayName=meta.get("displayName", plugin.name))
        cursor.pop("icon", None)
        claude.pop("displayName", None)
        agents = sorted((plugin / "agents").glob("*.md")) if (plugin / "agents").is_dir() else []
        if agents:
            claude["agents"] = [f"./agents/{a.name}" for a in agents]
            cursor["agents"] = "./agents/"
        cursor["skills"] = "./skills/"
        if (plugin / "rules").is_dir():
            cursor["rules"] = "./rules/"
        if "icon" in meta:
            cursor["logo"] = meta["icon"]
        claude.update(meta.get("claude", {}))
        cursor.update(meta.get("cursor", {}))
        out[plugin / ".claude-plugin" / "plugin.json"] = j(claude)
        out[plugin / ".cursor-plugin" / "plugin.json"] = j(cursor)
        manifests[plugin.name] = dict(claude, category=meta.get("category", "productivity"))

    market = json.loads(MARKET.read_text(encoding="utf-8"))
    entries, catalog = [], []
    for plugin in sorted(PLUGINS.iterdir(), key=lambda p: plugin_sort(p.name)):
        mpath = plugin / ".claude-plugin" / "plugin.json"
        pm = manifests.get(plugin.name) or (json.loads(mpath.read_text()) if mpath.exists() else None)
        if not pm:
            continue
        entries.append({
            "name": pm["name"],
            "source": f"./plugins/{plugin.name}",
            "description": pm.get("description", ""),
            "version": pm.get("version", "0.0.0"),
            "category": pm.get("category", "productivity"),
        })
        for skill_md in sorted((plugin / "skills").rglob("SKILL.md")):
            fm = front_matter(skill_md.read_text(encoding="utf-8"))
            catalog.append({
                "plugin": plugin.name,
                "skill": fm.get("name", skill_md.parent.name),
                "first_party": plugin.name in manifests,
                "description": fm.get("description", ""),
                "path": skill_md.parent.relative_to(ROOT).as_posix(),
            })
    body = {"name": market["name"], "owner": market["owner"],
            "metadata": market["metadata"], "plugins": entries}
    out[ROOT / ".claude-plugin" / "marketplace.json"] = j(body)
    out[ROOT / ".cursor-plugin" / "marketplace.json"] = j(body)
    out[ROOT / "catalog" / "skills.json"] = j(catalog)

    lines = ["# Skill catalog", "",
             "Generated by `scripts/build.py`. Do not edit.", "",
             f"{len(catalog)} skills in {len(entries)} plugins.", ""]
    current = None
    for row in catalog:
        if row["plugin"] != current:
            current = row["plugin"]
            tag = "" if row["first_party"] else " (vendored)"
            lines += ["", f"## {current}{tag}", "", "| Skill | Use when |", "|---|---|"]
        desc = row["description"].replace(chr(0x2014), "-")
        desc = re.sub(r"^Use when\s+", "", desc).split(". ")[0].rstrip(".")
        lines.append(f"| [{row['skill']}](../{row['path']}/SKILL.md) | {desc.replace('|', '/')} |")
    out[ROOT / "catalog" / "SKILLS.md"] = "\n".join(lines).replace("\n\n\n", "\n\n") + "\n"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    stale = []
    for path, content in targets().items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            stale.append(path.relative_to(ROOT))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if args.check:
        for s in stale:
            print(f"OUT OF DATE {s}  (run: python3 scripts/build.py)")
        return 1 if stale else 0
    print(f"built {len(stale)} file(s)" if stale else "everything up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
