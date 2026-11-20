---
name: target-state-options
description: >-
  Use when designing what a data system should become: clean-sheet target
  architecture options built backward from the decisions and data products
  people need, not from the legacy shape. Produces at least three genuinely
  different options (evolve, re-platform, reimagine) plus the status quo,
  scored on value, cost, risk and team fit, with steelmen, a recommendation and
  the target architecture with diagrams and what disappears.
---

# Target State Options

Design the future from the decisions it must serve, offer real choices, and
recommend one honestly.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Phase 3 of `reimagine-data-system`.
- "What should our data platform look like in two years?"

Not for: a single technology choice (use `architecture-decision`).

## Inspect first

1. The ground gate (decision, outcome, terrain, falsifiers, owner, single action).
2. The assessment: scores, causes, dispositions, quick wins.
3. The confirmed business rules and the sources that must keep flowing.
4. The team: size, skills, appetite for change, and what platforms are already owned.

## Procedure

1. **Work backward from decisions.** List the 5 to 10 decisions the data must
   serve, then the data products each needs (grain, freshness, consumers), then
   the capabilities to produce them (ingest, model, quality, serve, govern,
   operate). This capability map is the design input; the legacy object list is not.
2. **Design three options** that differ in approach, not just vendor
   ([assets/options-matrix.md](assets/options-matrix.md)):
   - **Evolve**: keep the platform, fix the causes (rebuild the worst pipelines,
     add tests, orchestration, a semantic layer).
   - **Re-platform**: same shape of solution on a modern platform (for example
     SQL Server warehouse to Fabric or Snowflake with dbt).
   - **Reimagine**: a different model and operating approach (for example
     data products with contracts, a Data Vault core with marts, mirroring
     instead of ETL, a governed semantic layer replacing report sprawl, or
     buying instead of building ingestion).
   - plus **Status quo** with its real cost of doing nothing.
3. **Score each** on value delivered to the decisions, total cost (build and
   three-year run, with basis), delivery risk, team can operate it, time to
   first value, reversibility, and what it lets you retire.
4. **Steelman** each option you do not recommend: its best honest case.
5. **Recommend** one, tied to the ground gate, and say what would change the
   recommendation (falsifiers).
6. **Draw the target** for the recommendation in
   `docs/reimagine/03-target-architecture.md`: principles, a context diagram,
   logical layers and data products, platform components, what each legacy
   object becomes (from dispositions), and a "what disappears" table with savings.
7. **Checkpoint**: present the options table and recommendation to the user.
   The choice is the owner's.

## Standards

- **MUST** design from decisions and data products backward.
- **MUST** offer options that differ in design, plus the status quo.
- **MUST** show cost basis and a three-year view for each option.
- **MUST** include "team can operate it" as a scored criterion.
- **SHOULD** prefer the simplest option that meets the decisions; complexity is a cost.
- **SHOULD** use platforms already owned unless the evidence says otherwise, and say so.

## Failure modes

| Failure | Prevention |
|---|---|
| Three options that are the same design with different logos | Evolve / re-platform / reimagine differ in approach |
| Recommending what the architect wants to build | Scored against the ground gate, steelmen written |
| Ignoring the cost of doing nothing | Status quo scored with its real cost |
| A target the current team cannot run | Team fit scored; hiring or partner plan required if low |
| Legacy shape copied into the new platform | Capability map from decisions is the input |

## Verify

- Each option has scores with reasons, a cost basis and a steelman (except the recommendation).
- Every "rebuild" and "replace" disposition maps to a target component.
- The recommendation traces to the ground gate in one sentence.

## Output

`docs/reimagine/02-options.md` and `docs/reimagine/03-target-architecture.md`.
