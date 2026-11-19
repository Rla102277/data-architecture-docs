#!/usr/bin/env python3
"""Summarize SSIS packages (.dtsx) and ADF / Fabric / Synapse pipeline JSON.

    python3 analyze_etl_package.py <file-or-folder>... --out docs/reverse-engineering/etl

Standard library only. Read-only: it parses files, it never runs anything.
For each package or pipeline it writes <name>.md with:
  - connections (SSIS connection managers / linked services and datasets referenced)
  - tasks or activities in order, with type and dependencies (precedence constraints, dependsOn)
  - every SQL statement or stored procedure call found, with where it came from
  - data flow sources and destinations (SSIS) or copy source and sink (pipelines)
and writes sql/<name>__<n>.sql for each SQL statement so lineage-extraction can parse them,
plus summary.csv across all packages.

Expressions, parameters and variables that build SQL at run time are listed as
"dynamic" because their final text is not in the file.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SQL_KEYS = {"sqlreaderquery", "query", "sqlreaderstoredprocedurename", "storedprocedurename",
            "prescript", "precopyscript", "sqlstatementsource", "sqlcommand", "openrowset",
            "sqlcommandvariable", "script"}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def attr(el: ET.Element, name: str) -> str | None:
    for k, v in el.attrib.items():
        if local(k).lower() == name.lower():
            return v
    return None


def analyze_dtsx(path: Path) -> dict:
    root = ET.parse(path).getroot()
    pkg = {"name": attr(root, "ObjectName") or path.stem, "kind": "SSIS", "file": str(path),
           "connections": [], "steps": [], "sql": [], "flows": [], "dependencies": [], "dynamic": []}
    for el in root.iter():
        tag = local(el.tag)
        if tag == "ConnectionManager" and attr(el, "ObjectName"):
            cs = ""
            for inner in el.iter():
                cs = attr(inner, "ConnectionString") or cs
            pkg["connections"].append((attr(el, "ObjectName"), attr(el, "CreationName") or "", cs))
        elif tag == "Executable" and attr(el, "ObjectName"):
            pkg["steps"].append((attr(el, "refId") or attr(el, "ObjectName"), attr(el, "ExecutableType") or "", ""))
        elif tag == "SqlTaskData":
            stmt = attr(el, "SqlStatementSource")
            src_type = attr(el, "SqlStmtSourceType") or "DirectInput"
            if stmt and src_type.lower() == "directinput":
                pkg["sql"].append(("Execute SQL task", stmt))
            elif stmt:
                pkg["dynamic"].append(f"Execute SQL from {src_type}: {stmt}")
        elif tag == "PrecedenceConstraint":
            pkg["dependencies"].append((attr(el, "From") or "", attr(el, "To") or "",
                                        attr(el, "Value") or "success"))
        elif tag == "component":
            cname = attr(el, "name") or ""
            cls = attr(el, "componentClassID") or ""
            props = {}
            for prop in el.iter():
                if local(prop.tag) == "property" and attr(prop, "name"):
                    props[attr(prop, "name")] = (prop.text or "").strip()
            role = "source" if "Source" in cls or "source" in cname.lower() else \
                   "destination" if "Destination" in cls or "dest" in cname.lower() else "transform"
            target = props.get("OpenRowset") or props.get("SqlCommand") or props.get("TableOrViewName") or ""
            pkg["flows"].append((role, cname, cls.split(".")[-1], target[:200]))
            if props.get("SqlCommand"):
                pkg["sql"].append((f"Data flow {role}: {cname}", props["SqlCommand"]))
            if props.get("SqlCommandVariable"):
                pkg["dynamic"].append(f"{cname}: SQL from variable {props['SqlCommandVariable']}")
        elif tag == "Variable" and attr(el, "EvaluateAsExpression") in ("True", "1"):
            pkg["dynamic"].append(f"Variable {attr(el, 'ObjectName')} built by expression {attr(el, 'Expression') or ''}")
    return pkg


def walk_json(obj, path=""):
    """Yield (path, value) for every node. Expression objects are yielded whole, not descended."""
    if isinstance(obj, dict):
        if obj.get("type") == "Expression" and "value" in obj:
            yield path, obj
            return
        for k, v in obj.items():
            yield from walk_json(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_json(v, f"{path}[{i}]")
    else:
        yield path, obj


def analyze_pipeline(path: Path) -> dict | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    props = data.get("properties", data)
    activities = props.get("activities")
    if activities is None:
        return None  # dataset or linked service file, not a pipeline
    pkg = {"name": data.get("name") or path.stem, "kind": "Pipeline", "file": str(path),
           "connections": [], "steps": [], "sql": [], "flows": [], "dependencies": [], "dynamic": []}

    def visit(acts, parent=""):
        for a in acts:
            name = a.get("name", "?")
            full = f"{parent}/{name}" if parent else name
            tp = a.get("typeProperties", {}) or {}
            pkg["steps"].append((full, a.get("type", ""), a.get("description", "") or ""))
            for d in a.get("dependsOn", []) or []:
                pkg["dependencies"].append((d.get("activity", ""), full, ",".join(d.get("dependencyConditions", []))))
            for ref in (a.get("inputs") or []) + (a.get("outputs") or []):
                pkg["connections"].append((ref.get("referenceName", ""), "dataset", ""))
            if a.get("linkedServiceName"):
                pkg["connections"].append((a["linkedServiceName"].get("referenceName", ""), "linked service", ""))
            nested = {"activities", "ifTrueActivities", "ifFalseActivities", "cases", "defaultActivities"}
            shallow = {k: v for k, v in tp.items() if k not in nested}
            for p, v in walk_json(shallow):
                clean = re.sub(r"\[\d+\]", "", p).lower()
                leaf = clean.split(".")[-1]
                is_sql = leaf in SQL_KEYS or (leaf == "text" and "scripts" in clean)
                if isinstance(v, dict):  # Expression object
                    if is_sql:
                        pkg["dynamic"].append(f"{full} ({p}): SQL built by expression {str(v.get('value', ''))[:200]}")
                    continue
                if not is_sql or v in (None, ""):
                    continue
                if isinstance(v, str) and v.strip().startswith("@"):
                    pkg["dynamic"].append(f"{full} ({p}): SQL built by expression {v[:200]}")
                elif "storedprocedurename" in leaf:
                    pkg["sql"].append((f"{full} ({p})", f"EXEC {v}"))
                else:
                    pkg["sql"].append((f"{full} ({p})", str(v)))
            for side in ("source", "sink"):
                if isinstance(tp.get(side), dict):
                    pkg["flows"].append((side, full, tp[side].get("type", ""), ""))
            for key in ("activities", "ifTrueActivities", "ifFalseActivities"):
                if isinstance(tp.get(key), list):
                    visit(tp[key], full)
            for case in tp.get("cases", []) or []:
                visit(case.get("activities", []), f"{full}[{case.get('value')}]")
            if isinstance(tp.get("defaultActivities"), list):
                visit(tp["defaultActivities"], f"{full}[default]")
            if a.get("type") in ("ExecutePipeline", "InvokePipeline"):
                ref = (tp.get("pipeline") or {}).get("referenceName") or tp.get("pipelineId") or ""
                pkg["dependencies"].append((full, f"pipeline:{ref}", "calls"))

    visit(activities)
    return pkg


def write(pkg: dict, out: Path) -> None:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", pkg["name"])
    sql_dir = out / "sql"
    sql_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# {pkg['name']}", "", f"- Kind: {pkg['kind']}", f"- File: `{pkg['file']}`", ""]
    lines += ["## Connections", "", "| Name | Type | Detail |", "|---|---|---|"]
    for n, t, d in sorted(set(pkg["connections"])):
        d = re.sub(r"(?i)(password|pwd)=[^;]*", r"\1=***", d)
        lines.append(f"| {n} | {t} | {d[:120]} |")
    lines += ["", "## Steps", "", "| Step | Type | Notes |", "|---|---|---|"]
    lines += [f"| {s} | {t} | {d[:120]} |" for s, t, d in pkg["steps"]]
    lines += ["", "## Dependencies", "", "| From | To | Condition |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {c} |" for a, b, c in pkg["dependencies"]]
    lines += ["", "## Data movement", "", "| Role | Component | Type | Object or query |", "|---|---|---|---|"]
    lines += [f"| {r} | {c} | {t} | {o.replace('|', '/')} |" for r, c, t, o in pkg["flows"]]
    lines += ["", "## SQL found", ""]
    for i, (where, sql) in enumerate(pkg["sql"], 1):
        fname = f"{safe}__{i}.sql"
        (sql_dir / fname).write_text(f"-- {pkg['name']} :: {where}\n{sql}\n", encoding="utf-8")
        lines.append(f"{i}. {where}: `sql/{fname}`")
    lines += ["", "## Dynamic (not resolvable from the file)", ""]
    lines += [f"- {d}" for d in pkg["dynamic"]] or ["- none found"]
    (out / f"{safe}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", default="etl")
    args = ap.parse_args()
    files: list[Path] = []
    for p in map(Path, args.paths):
        files += [f for f in sorted(p.rglob("*")) if f.suffix.lower() in (".dtsx", ".json")] if p.is_dir() else [p]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in files:
        try:
            pkg = analyze_dtsx(f) if f.suffix.lower() == ".dtsx" else analyze_pipeline(f)
        except (ET.ParseError, json.JSONDecodeError, UnicodeDecodeError) as err:
            rows.append([f.name, "unreadable", 0, 0, 0, str(err)[:120]])
            continue
        if pkg is None:
            continue
        write(pkg, out)
        rows.append([pkg["name"], pkg["kind"], len(pkg["steps"]), len(pkg["sql"]), len(pkg["dynamic"]), str(f)])
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["package", "kind", "steps", "sql_statements", "dynamic_items", "file"])
        w.writerows(rows)
    print(f"{len(rows)} packages/pipelines -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
