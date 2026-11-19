---
name: legacy-to-dbt-migration
description: >-
  Use when moving legacy SQL logic (stored procedures, views, SSIS or ADF
  transforms, SQL Agent jobs) into dbt on Fabric, Snowflake, SQL Server or a
  lakehouse. Plans the cut by subject area, maps each proc step to dbt models,
  carries business rules over explicitly, and proves parity with row and value
  comparisons before switching consumers.
---

# Legacy to dbt Migration

Rebuild legacy transformation logic as dbt models, one subject area at a time,
and prove the new numbers match the old ones before anyone switches over.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "Convert these stored procedures to dbt."
- "Retire the SSIS packages and move the logic into dbt on Fabric."

Not for: greenfield dbt projects (use `dbt-project-setup`), or lifting procs
unchanged into a new server (that is a lift-and-shift, not this).

## Inspect first

Do not start until these exist (from `reverse-engineer-data-system`):
1. Lineage for the subject area (`lineage/`), so you know every input and output.
2. Proc specs for every proc in scope (`procs/`).
3. The rules catalog with owner status (`rules/rules-catalog.md`).
4. Profiles of the source tables (`profiles/`), so keys and grain are known.
5. The consumers of the outputs: reports, extracts, apps.

## Procedure

1. **Pick the slice.** One subject area whose outputs have clear consumers
   (e.g. sales fact and its dims). Not "all procs in schema dbo".
2. **Map old to new.** In `migration/<area>/mapping.md`, one row per legacy step:
   legacy object and lines, new dbt model, layer, and the rules it carries.
   - Temp tables usually become `intermediate` models (ephemeral or views).
   - Staging selects become `stg_<source>__<entity>` models.
   - Final inserts or merges become marts, usually `incremental`.
   - Cursors and loops become set-based SQL. If a loop truly cannot be set-based,
     say why and keep it out of dbt.
3. **Decide each rule.** Every BR in scope is carried as-is, corrected (owner
   approved) or retired (owner approved). Write the decision in the mapping. A
   corrected rule means parity is expected to differ: write down by how much.
4. **Build in dbt** with `dbt-model-development` standards. Keep legacy column
   names in a final compatibility view if consumers depend on them.
5. **Prove parity** (see [references/parity-testing.md](references/parity-testing.md)):
   row counts, key coverage both ways, and column-by-column value comparison on
   the same inputs and the same as-of time. Explain every difference.
6. **Run in parallel** for an agreed period (usually one or two full business
   cycles, including a month end for finance data). Compare daily.
7. **Switch consumers** one at a time, then disable the legacy job. Keep the
   legacy code and a final output snapshot for the retention period agreed.
   Never drop legacy objects without explicit approval.

## Standards

- **MUST** compare on identical inputs and as-of times; otherwise differences are noise.
- **MUST** explain every parity difference: rule change (approved), legacy bug
  (documented, owner agrees), or new bug (fix it).
- **MUST NOT** decommission legacy until parity holds through the agreed period
  and the owner signs off. Ask before any drop or disable.
- **SHOULD** migrate by output consumer, not by legacy object.
- **SHOULD** make the dbt version idempotent even when the proc was not.

## Failure modes

| Failure | Prevention |
|---|---|
| Rules silently changed in translation | Each rule's decision recorded in the mapping |
| Parity "passes" on counts but values differ | Column-level value comparison, not just counts |
| Legacy bug reproduced forever | Bugs are documented and fixed with owner approval |
| Big-bang cutover fails at month end | Parallel run including a month end, per-consumer switch |
| Hidden consumer breaks after the old table disappears | Consumers listed before; compatibility view; staged retire |

## Verify

- Parity report per output: rows, key coverage, column mismatch counts, and
  explanations, for every day of the parallel run.
- `dbt build` passes with tests; the legacy job is disabled only after sign-off.

## Output

`migration/<area>/mapping.md`, `migration/<area>/parity/<date>.md`, the dbt
models and tests, and a cutover checklist with sign-offs.
