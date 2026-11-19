---
name: validate-architecture-docs
description: >-
  Use when a data architecture doc set has been written or changed and must
  be checked before review or hand-off: runs the docs linter (missing docs,
  empty ground gate, front matter, placeholders, undefined IDs, untagged
  assumptions, Mermaid fences, exec word ceilings, review verdicts) and walks
  the persona consistency, decision and wind-pattern gates.
---

# Validate Architecture Docs

## 1. Run the linter

```bash
python3 <this-skill-dir>/scripts/validate_docs.py docs/architecture
# one pack only:
python3 <this-skill-dir>/scripts/validate_docs.py docs/architecture --packs executive
```

Standard library Python only. Exit 1 on any error. Fix every error. Each warning
gets a fix or a one-line reason in the README.

It fails on: missing expected docs, missing facts file, empty
`ground.single_action`, missing front matter fields, leftover `{{...}}`
placeholders, `lorem`, `TBD` without an ID, ASSUMPTION/OPEN QUESTION without an
ID, references to undefined IDs, unbalanced code fences, empty Mermaid blocks,
exec docs over their word ceiling, review files without a VERDICT line.

It warns on: em dashes, filler phrases, missing change logs, no reviews yet,
`status: approved` (confirm a human did it), exec diagrams over 7 nodes.

## 2. Walk the gates

[references/quality-gates.md](references/quality-gates.md): ground gate,
persona consistency (trace five facts through all three packs), per-pack gates,
decisions, wind patterns, reviews, writing.

## 3. Report

List what passed, what you fixed and what is left, with IDs. Do not report
"all checks passed" unless the linter exited 0 in this session.
