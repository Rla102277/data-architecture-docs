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

Catch what a machine can catch, then check what only a reader can.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- Phase 7 of `architecture-docs`, and after any doc edit.
- In CI on `docs/architecture/**`.

Not for: reviewing content quality (use `review-architecture-docs`).

## Inspect first

1. Which packs exist (`--packs` limits the check to them).
2. Python 3 is available (the linter uses the standard library only).

## Procedure

1. Run the linter:
   ```bash
   python3 <this-skill-dir>/scripts/validate_docs.py docs/architecture
   python3 <this-skill-dir>/scripts/validate_docs.py docs/architecture --packs executive
   ```
   It fails on missing docs, a missing facts file, an empty `ground.single_action`,
   missing front matter, `{{...}}` placeholders, `lorem`, `TBD` without an ID,
   untagged ASSUMPTION / OPEN QUESTION, undefined IDs, unbalanced fences, empty
   Mermaid blocks, exec docs over their ceiling, reviews without a VERDICT line.
   It warns on em dashes, filler phrases, missing change logs, no reviews,
   `status: approved`, and exec diagrams over 7 nodes.
2. Fix every error. Each warning gets a fix or a one-line reason in the README.
3. Walk [references/quality-gates.md](references/quality-gates.md): ground gate,
   persona consistency (trace five facts through all packs), per-pack gates,
   decisions, wind patterns, reviews, writing.

## Standards

- **MUST** report "all checks passed" only if the linter exited 0 in this session.
- **MUST** fix errors before review.
- **SHOULD** run the linter in CI for any repo with `docs/architecture/`.

## Failure modes

| Failure | Prevention |
|---|---|
| Claimed pass without running | Exit code reported |
| Consistent-looking but wrong numbers across packs | Manual five-fact trace |
| Warnings ignored silently | Reason recorded in the README |

## Verify

Linter exit code 0, and the quality-gate checklist completed.

## Output

A short report: passed, fixed, and remaining items with IDs.
