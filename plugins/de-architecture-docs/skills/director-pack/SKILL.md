---
name: director-pack
description: >-
  Use when writing or revising the Data Director documents for a data platform:
  solution architecture, operating model and RACI, data governance and
  security, data quality and SLA framework, delivery plan, and cost model and
  FinOps (DIR-01..06). Logical design, ownership and trade-offs, tables over prose.
---

# Director Pack (Data Director)

Give the person accountable for the platform, team, roadmap and budget what they
need to own it.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- Phase 4 of `architecture-docs`, after the engineer pack.
- "Write the solution architecture / RACI / delivery plan / cost model."

Not for: build detail (engineer pack) or the exec brief (executive pack).

## Inspect first

1. The facts file, the ADRs and the engineer pack.
2. The reader: technical enough to challenge a design, not writing the code;
   decides scope, sequencing, staffing, standards, governance, build vs buy.
3. The real team: roles and people available, not an ideal org chart.

## Procedure

Write `director/DIR-01..06` from [assets/templates/](assets/templates/):

| Doc | Must hold |
|---|---|
| DIR-01 Solution architecture | Single action at top; logical diagram (10 to 20 boxes); layers, domains, data products; NFR table with design response; key ADRs with the trade-off; alternatives |
| DIR-02 Operating model and RACI | One A per row; only real roles or named hires; intake, support tiers, forums |
| DIR-03 Governance and security | Each data class mapped to a control; owner and steward per domain; retention; compliance evidence |
| DIR-04 DQ and SLA | Each SLA with a measurement and owner; severity with pipeline behavior; reconciliation |
| DIR-05 Delivery plan | Exit criteria per phase; capacity vs effort with the gap stated; dependencies with owners |
| DIR-06 Cost and FinOps | Unit x volume x frequency and price date per line; 2x and 3x scaling; levers |

## Standards

- **MUST** state trade-offs explicitly and name key-person risk.
- **MUST** use the facts file for every number.
- **SHOULD** prefer tables over prose; 4 to 12 pages per doc.
- **SHOULD** explain vendor-specific terms in one line.

## Failure modes

| Failure | Prevention |
|---|---|
| Plan assumes heroics | Capacity vs effort table with the gap |
| SLA nobody can measure | Measurement and owner per SLA |
| Ownership split so nobody owns it | One A per RACI row |

## Verify

The `data-director-reader` review passes, and five facts match the other packs.

## Output

`docs/architecture/director/DIR-01..06`.
