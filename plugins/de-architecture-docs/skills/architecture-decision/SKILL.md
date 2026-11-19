---
name: architecture-decision
description: >-
  Use when a data platform choice must be made or recorded: platform,
  table format, layering (medallion, Data Vault), modeling, ingestion (CDC vs
  watermark), transform tool, orchestration, environments, access model, BI
  mode. Writes an ADR with options, the status quo, a steelman of the rejected
  option and a falsifiable validation test.
---

# Architecture Decision

Record one real decision so the next person knows what was chosen, what was
rejected, and what would make us revisit it.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- Phase 2 of `architecture-docs`, once per real decision.
- Any time a platform, pattern or tool choice is about to be made or was made without a record.

Not for: small implementation choices inside one model or pipeline.

## Inspect first

1. The facts file: drivers (NFRs, KPIs, terrain) the decision must serve.
2. Whether the decision was already made. If so, record it honestly; do not invent
   a comparison that never happened.
3. Existing ADRs this one supersedes or depends on.

## Procedure

1. Copy [assets/adr-template.md](assets/adr-template.md) to
   `docs/architecture/engineer/adr/ADR-####-<slug>.md` and mirror it in the facts
   file `decisions:` list.
2. List at least two viable options plus the **status quo** when one exists. For
   ingestion, compare **CDC against timestamp watermarks** explicitly.
3. Score each on correctness under failure and replay, operational burden,
   latency, governance and security, build and run cost, reversibility, and
   whether **this team** can operate it today.
4. **Steelman** the strongest option you reject.
5. Decide, tied to the drivers. Write the consequences, including the trade-off accepted.
6. Write a **validation test**: a measurable result by a date that would make us revisit.
7. Write the **exec one-liner** the executive pack will reuse.
8. Common candidates: platform; table format; layering (medallion, Data Vault);
   consumption modeling; ingestion per source class; transform tool;
   orchestration; environment topology; identity and access; data quality
   tooling; BI connection mode; CI/CD; historization; naming; build vs buy.
   Write only the real ones.

## Standards

- **MUST** justify by terrain, never by habit, vendor preference or resume value.
- **MUST** include a falsifiable validation test.
- **MUST** stay `proposed` until a named human accepts it.
- **SHOULD** link superseding ADRs both ways.

## Failure modes

| Failure | Prevention |
|---|---|
| One-option "decision" | Two options plus status quo required |
| Strawman of the rejected option | Steelman section |
| Decision never revisited when facts change | Validation test with a date |

## Verify

Every ADR has two or more options, a steelman, a validation test and an exec one-liner.

## Output

`docs/architecture/engineer/adr/ADR-####-<slug>.md` and its entry in the facts file.
