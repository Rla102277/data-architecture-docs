---
name: backfill-and-replay
description: >-
  Use when historical data must be loaded, reloaded or reprocessed: initial
  history loads, rebuilding after a logic fix, replaying from raw after a bad
  run, or recovering a missed window. Plans scope, ordering, isolation, cost and
  validation, runs in chunks with checkpoints, and protects production
  consumers while it runs.
---

# Backfill and Replay

Reprocess history without breaking today's data, the source, the budget or the
people reading the reports.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- First load of years of history.
- A logic bug fixed; history must be recomputed.
- A pipeline missed days and must catch up.

Not for: routine incremental loads (use `incremental-ingestion`).

## Inspect first

1. **Scope**: which tables, which date range, which downstream models depend on
   them (`dbt ls --select model+`, lineage).
2. **Where the replay comes from**: raw landed data (best), the source system
   (load and retention limits), or backups and time travel.
3. **Cost and load**: rows, size, warehouse or capacity cost, source system load
   limits, how long one chunk takes.
4. **Who reads the affected outputs** and when. A backfill during month-end close
   is a bad idea.

## Procedure

1. **Write the plan** ([assets/backfill-plan.md](assets/backfill-plan.md)): scope,
   source, chunking, order, isolation, validation, rollback, communication. Get
   approval from the data owner for anything that changes published numbers.
2. **Isolate**: build into a separate schema or table version when possible, then
   swap; or pause downstream refreshes during the run.
3. **Chunk** by the partition or date grain (day, month), oldest first, so each
   chunk is idempotent and restartable. Record each chunk's status in a
   checkpoint table.
4. **Throttle**: limit concurrency to protect the source and the platform
   (Snowflake warehouse size, Fabric capacity, Spark cluster).
5. **Validate each chunk**: row counts and totals against the source or the
   expected change; stop at the first failure.
6. **Swap or resume** downstream refreshes, then rebuild dependents in order.
7. **Announce** what changed: which numbers, which periods, by how much, and why.

## Standards

- **MUST** get owner approval before restating published numbers.
- **MUST** be restartable: chunked, idempotent, with checkpoints.
- **MUST** validate before exposing results to consumers.
- **MUST** keep a rollback path: previous table version, time travel, or a copy.
- **SHOULD** replay from your own raw layer rather than hammering the source.
- **SHOULD** run outside business-critical windows (close, board reporting).
- **SHOULD** for dbt, use `--full-refresh` only on models that need it; use
  vars-driven or microbatch windows for partial history.

## Failure modes

| Failure | Prevention |
|---|---|
| Backfill overwrites good data with bad | Isolated build, validation before swap |
| Run dies at 70 percent, restart redoes everything | Checkpointed chunks |
| Source system slowed for users | Throttling and off-hours scheduling |
| Capacity throttling takes down daily loads (Fabric) | Size the run against capacity, schedule around daily jobs |
| Restated numbers surprise finance | Owner approval and a change note |
| Downstream models not rebuilt | Dependency list and ordered rebuild |

## Verify

- Every chunk's checkpoint shows succeeded with validated counts.
- Period totals before and after, with every difference explained by the fix.

## Output

The backfill plan, checkpoint log, validation results, and the change note sent
to consumers.
