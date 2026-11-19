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

Write one ADR per real decision to `docs/architecture/engineer/adr/ADR-####-<slug>.md`
from [assets/adr-template.md](assets/adr-template.md), and mirror it in the
facts file `decisions:` list. Follow [references/conventions.md](references/conventions.md).

## Discipline (study the wind)

1. Compare at least two viable options, plus the **status quo** when one exists.
2. For ingestion, compare **CDC against timestamp watermarks** explicitly.
3. Score each on: correctness under failure and replay, operational burden,
   latency, governance and security, cost (build and run), reversibility, and
   whether **this team** can operate it today.
4. **Steelman** the strongest option you reject. If you cannot write its best
   honest case, you have not compared fairly.
5. Decide, tied to the decision drivers (NFR, KPI, terrain). Never justify by
   habit, vendor preference or resume value.
6. End with a **validation test**: a measurable result by a date that would make
   us revisit the decision.
7. Write the **exec one-liner** the executive pack will use.

If the user already chose, record the choice honestly: drivers, what was
weighed, and the validation test. Do not invent a comparison that never happened.

## Status

`proposed` until a named human accepts it. Superseding ADRs link both ways.

## Common decisions

Platform; storage and table format; layering pattern; consumption modeling;
ingestion pattern per source class; transformation tool; orchestration;
workspace/account/environment topology; identity and access; data quality
tooling; semantic layer and BI connection mode; source control and CI/CD;
historization; naming; build vs buy for ingestion. Write only the real ones.
