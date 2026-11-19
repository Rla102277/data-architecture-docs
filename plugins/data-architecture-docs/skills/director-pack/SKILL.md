---
name: director-pack
description: >-
  Use when writing or revising the Data Director documents for a data platform:
  solution architecture, operating model and RACI, data governance and
  security, data quality and SLA framework, delivery plan, and cost model and
  FinOps (DIR-01..06). Logical design, ownership and trade-offs, tables over prose.
---

# Director Pack (Data Director)

Write `docs/architecture/director/DIR-01..06` from
[assets/templates/](assets/templates/). Read the facts file, the ADRs and the
engineer pack first. Follow [references/conventions.md](references/conventions.md).

## The reader

Owns the platform, the team, the roadmap and the budget. Translates strategy
into delivery. Technical enough to challenge a design, not writing the code.
Decides scope, sequencing, staffing, standards, governance model, build vs buy,
and which trade-offs are acceptable.

Cares about: logical architecture (domains, layers, data products); who owns
what (RACI, stewardship, intake, support); governance, classification, access
and compliance; quality and reliability (SLOs, DQ, incidents); phases,
dependencies, capacity and hiring; cost and FinOps; adoption.

## Voice

Clear and structured. Confident recommendations, explicit trade-offs. Data
vocabulary is fine (medallion, CDC, SCD2, semantic model); explain anything
vendor-specific in one line.

## Rules per doc

| Doc | Must hold |
|---|---|
| DIR-01 Solution architecture | Single action at the top; logical diagram (10 to 20 boxes); layers, domains, data products; NFR table with design response; key ADRs with the trade-off accepted; alternatives considered |
| DIR-02 Operating model and RACI | Exactly one A per row; only roles the team has or a named hire; intake, support tiers, forums |
| DIR-03 Governance and security | Every data class mapped to a control; owner and steward per domain; retention; compliance mapping with evidence |
| DIR-04 DQ and SLA | Every SLA has a measurement and an owner; severity levels with pipeline behavior; reconciliation approach |
| DIR-05 Delivery plan | Every phase has exit criteria; capacity versus effort with the gap stated honestly; dependencies with owners |
| DIR-06 Cost and FinOps | Unit x volume x frequency and price date for every line; scaling curve at 2x and 3x; levers with trade-offs |

Length: 4 to 12 pages per doc. Name key-person risk wherever only one person
could run something.
