#!/usr/bin/env python3
"""Validate a docs/architecture/ set produced by the data-architecture-docs skill.

Usage:
    python3 validate_docs.py docs/architecture [--packs executive,director,engineer]
                                               [--allow-em-dash]

Standard library only. Exit code 1 if any ERROR is found.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EXPECTED = {
    "executive": [
        "EXE-01-executive-brief.md",
        "EXE-02-strategic-architecture-overview.md",
        "EXE-03-investment-and-roadmap.md",
        "EXE-04-risk-and-governance-summary.md",
    ],
    "director": [
        "DIR-01-solution-architecture.md",
        "DIR-02-operating-model-and-raci.md",
        "DIR-03-data-governance-and-security.md",
        "DIR-04-data-quality-and-sla-framework.md",
        "DIR-05-delivery-plan.md",
        "DIR-06-cost-model-and-finops.md",
    ],
    "engineer": [
        "ENG-01-technical-design-document.md",
        "ENG-02-physical-data-model.md",
        "ENG-03-pipeline-specifications.md",
        "ENG-05-test-strategy.md",
        "ENG-06-environments-and-cicd.md",
        "ENG-07-security-implementation.md",
        "ENG-08-observability-and-runbook.md",
        "ENG-09-engineering-standards.md",
    ],
    "shared": ["glossary.md", "traceability-matrix.md", "raid-log.md"],
}
REQUIRED_FM = ["doc_id", "title", "persona", "status", "version", "last_updated"]
WORD_CEILING = {"EXE-01": 900, "EXE-02": 1200, "EXE-03": 1200, "EXE-04": 1200}
ID_RE = re.compile(
    r"\b(?:REQ|NFR|RSK|SRC|PL|DP|TST|KPI|DC|RB|PH)-\d{3}\b|\bADR-\d{4}\b|\b[AQ]-\d{3}\b"
)
BANNED = [
    "data-driven world", "leverage synergies", "robust and scalable",
    "cutting-edge", "best-in-class", "seamless", "game-changer", "unlock the power",
    "in today's", "paradigm shift",
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"ERROR   {where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"WARN    {where}: {msg}")


def front_matter(text: str) -> dict[str, str] | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm: dict[str, str] = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*?)\s*(?:#.*)?$", line)
        if m:
            fm[m.group(1)] = m.group(2)
    return fm


def strip_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def defined_ids(root: Path, docs: dict[Path, str]) -> set[str]:
    ids: set[str] = set()
    facts = root / "00-project-facts.yaml"
    if facts.exists():
        for m in re.finditer(r"id:\s*([A-Z]{1,3}-\d{3,4})", facts.read_text(encoding="utf-8")):
            ids.add(m.group(1))
    for path, text in docs.items():
        m = re.match(r"(ADR-\d{4})", path.name)
        if m:
            ids.add(m.group(1))
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                ids.update(ID_RE.findall(s))
            elif s.startswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if cells and ID_RE.fullmatch(cells[0]):
                    ids.add(cells[0])
            mm = re.search(r"(?:ASSUMPTION|OPEN QUESTION)\s*\[([AQ]-\d{3})\]", s)
            if mm:
                ids.add(mm.group(1))
            mm = re.match(r"(?:contract_id|doc_id):\s*([A-Z]{1,3}-\d{3,4})", s)
            if mm:
                ids.add(mm.group(1))
    return ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--packs", default="executive,director,engineer,shared")
    ap.add_argument("--allow-em-dash", action="store_true")
    args = ap.parse_args()
    root: Path = args.root
    rep = Report()

    if not root.is_dir():
        print(f"ERROR   {root}: directory not found")
        return 1

    packs = [p.strip() for p in args.packs.split(",") if p.strip()]
    for pack in packs:
        for name in EXPECTED.get(pack, []):
            if not (root / pack / name).exists():
                rep.err(f"{pack}/{name}", "expected doc is missing")
        if pack == "engineer":
            if not list((root / "engineer" / "adr").glob("ADR-*.md")):
                rep.err("engineer/adr", "no ADRs found")
            if not list((root / "engineer" / "ENG-04-data-contracts").glob("*.y*ml")):
                rep.warn("engineer/ENG-04-data-contracts", "no data contract YAML files")
    if not (root / "00-project-facts.yaml").exists():
        rep.err("00-project-facts.yaml", "facts file missing")
    if not (root / "README.md").exists():
        rep.warn("README.md", "reading guide missing")

    docs = {p: p.read_text(encoding="utf-8") for p in root.rglob("*.md")}
    ids = defined_ids(root, docs)

    for path, text in sorted(docs.items()):
        rel = str(path.relative_to(root))
        if path.name != "README.md":
            fm = front_matter(text)
            if fm is None:
                rep.err(rel, "no front matter")
            else:
                for key in REQUIRED_FM:
                    if not fm.get(key):
                        rep.err(rel, f"front matter missing '{key}'")
            if "## Change log" not in text:
                rep.warn(rel, "no '## Change log' section")

        body = strip_code(text)
        if "{{" in text and "}}" in text:
            rep.err(rel, "template placeholders {{...}} left in")
        if re.search(r"\blorem\b", body, re.I):
            rep.err(rel, "lorem ipsum left in")
        for m in re.finditer(r"\bTBD\b(?![^\n]*\b[AQ]-\d{3}\b)", body):
            rep.err(rel, "TBD without an A-/Q- id")
            break
        for m in re.finditer(r"(ASSUMPTION|OPEN QUESTION)(?!\s*\[[AQ]-\d{3}\])", body):
            rep.err(rel, f"{m.group(1)} marker without an id like [A-001]/[Q-001]")
            break

        if text.count("```") % 2:
            rep.err(rel, "unbalanced code fences")
        if "```mermaid" in text:
            for block in re.findall(r"```mermaid\n(.*?)```", text, re.S):
                if not block.strip():
                    rep.err(rel, "empty mermaid block")

        for ref in sorted(set(ID_RE.findall(text)) - ids):
            rep.err(rel, f"references {ref} but it is not defined anywhere")

        if not args.allow_em_dash and "\u2014" in text:
            rep.warn(rel, f"{text.count(chr(0x2014))} em dash(es)")
        low = body.lower()
        for phrase in BANNED:
            if phrase in low:
                rep.warn(rel, f"filler phrase: '{phrase}'")

        m = re.match(r"(EXE-\d{2})", path.name)
        if m and m.group(1) in WORD_CEILING:
            words = len(re.findall(r"\w+", body))
            if words > WORD_CEILING[m.group(1)]:
                rep.err(rel, f"{words} words, ceiling is {WORD_CEILING[m.group(1)]}")
        if path.parent.name == "executive":
            for block in re.findall(r"```mermaid\n(.*?)```", text, re.S):
                nodes = set(re.findall(r"\b([A-Za-z_][\w]*)\s*[\[\(\{]", block))
                if len(nodes) > 7:
                    rep.warn(rel, f"exec diagram has ~{len(nodes)} nodes, target is 7 or fewer")

    for line in rep.errors + rep.warnings:
        print(line)
    print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s), {len(docs)} doc(s) checked")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
