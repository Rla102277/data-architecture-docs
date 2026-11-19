#!/usr/bin/env python3
"""Build generated files for the first-party plugin. Standard library only.

    python3 scripts/build.py          # write generated files
    python3 scripts/build.py --check  # exit 1 if anything is out of date (CI)

Generates:
- references/conventions.md in every first-party skill, from
  plugins/data-architecture-docs/shared/conventions.md
- .claude-plugin/plugin.json and .cursor-plugin/plugin.json for the
  first-party plugin, from plugins/data-architecture-docs/plugin.meta.json
- .claude-plugin/marketplace.json and .cursor-plugin/marketplace.json at the
  repo root, listing every plugin under plugins/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "data-architecture-docs"
CANON = PLUGIN / "shared" / "conventions.md"
META = PLUGIN / "plugin.meta.json"
MARKET = ROOT / "marketplace.meta.json"


def j(obj: object) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def targets() -> dict[Path, str]:
    out: dict[Path, str] = {}
    conv = CANON.read_text(encoding="utf-8")
    for skill in sorted((PLUGIN / "skills").iterdir()):
        if (skill / "SKILL.md").exists():
            out[skill / "references" / "conventions.md"] = conv

    meta = json.loads(META.read_text(encoding="utf-8"))
    common = {k: v for k, v in meta.items() if not k.startswith("_") and k not in ("cursor", "claude")}
    claude = dict(common, **meta.get("claude", {}))
    cursor = dict(common, **meta.get("cursor", {}))
    out[PLUGIN / ".claude-plugin" / "plugin.json"] = j(claude)
    out[PLUGIN / ".cursor-plugin" / "plugin.json"] = j(cursor)

    market = json.loads(MARKET.read_text(encoding="utf-8"))
    entries = []
    for plugin_dir in sorted((ROOT / "plugins").iterdir()):
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if plugin_dir.name == PLUGIN.name:
            pm = claude
        elif manifest.exists():
            pm = json.loads(manifest.read_text(encoding="utf-8"))
        else:
            continue
        entries.append({
            "name": pm["name"],
            "source": f"./plugins/{plugin_dir.name}",
            "description": pm.get("description", ""),
            "version": pm.get("version", "0.0.0"),
        })
    # first-party plugin first
    entries.sort(key=lambda e: (e["name"] != PLUGIN.name, e["name"]))
    body = {
        "name": market["name"],
        "owner": market["owner"],
        "metadata": market["metadata"],
        "plugins": entries,
    }
    out[ROOT / ".claude-plugin" / "marketplace.json"] = j(body)
    out[ROOT / ".cursor-plugin" / "marketplace.json"] = j(body)
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
