---
name: incremental-ingestion
description: >-
  Use when designing or fixing how data is pulled from a source into the
  platform: choosing CDC, SQL Server change tracking, timestamp watermarks,
  full snapshots, file drops or API pagination; making loads idempotent;
  handling deletes, late and corrected rows, schema drift, retries and partial
  failures; and recording watermarks safely.
---

# Incremental Ingestion

Get every change from the source exactly once in effect, survive reruns, and know
when you missed something.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New source onboarding.
- "We're missing rows", "we have duplicates", "deletes never show up".

Not for: one-time historical loads and reprocessing (use `backfill-and-replay`),
SQL Server-specific source setup (also read `sql-server-source-extraction`).

## Inspect first

1. **The source's change signals**, verified, not assumed:
   - CDC or change tracking enabled? Retention period?
   - An `updated_at` column: is it set on every insert AND update, by the
     database or by app code? App-maintained timestamps are often missed by bulk
     updates and fixes. Profile it.
   - Hard deletes or soft deletes?
   - Can old rows change (corrections, back-dated transactions)?
2. Volume: rows per day changed vs total rows. Small tables (under a few million
   rows) are often cheapest as full snapshots.
3. Source load limits: replica available? Maintenance windows? API rate limits?

## Procedure

1. **Choose the pattern** with [references/patterns.md](references/patterns.md)
   and write it as an ADR (`architecture-decision`), comparing CDC against
   watermarks explicitly.
2. **Land raw first**: write exactly what you extracted, append-only, with
   `_loaded_at`, `_batch_id`, `_source_file` or `_lsn`/`_ct_version`. The raw
   layer is your replay buffer.
3. **Make it idempotent**: rerunning a batch must not duplicate data. Use one of:
   overwrite the batch's partition, merge on the business key, or dedupe on
   `(key, change version)` downstream.
4. **Advance the watermark only after the data is committed**, in the same
   transaction or after a verified write. Store it in a control table
   (pipeline, source object, watermark value, batch id, updated_at), never in
   a variable that dies with the run.
5. **Lookback for watermarks**: extract `updated_at > watermark - overlap`
   (minutes to days, depending on clock skew and late commits), and dedupe.
6. **Deletes**: CDC delete events or tombstones; for watermark sources, a
   periodic key reconciliation (all source keys vs target keys) or a scheduled
   snapshot comparison.
7. **Schema drift**: detect new, dropped and retyped columns on every run.
   New nullable columns: add and alert. Dropped or retyped: stop and alert.
8. **Retries and partial failure**: retry transient errors with backoff; a
   failed batch leaves the watermark unchanged so the next run picks it up.
9. **Record every batch**: rows extracted, rows landed, watermark before and
   after, duration, status, in an audit table. Silent zero-row runs alert when
   unexpected.

## Standards

- **MUST** be idempotent: same batch in, same state out.
- **MUST** move the watermark only after the load commits.
- **MUST** have a delete strategy, even if it is "source never deletes" with evidence.
- **MUST** alert on zero rows when the source normally changes daily, and on
  volume swings beyond a threshold.
- **SHOULD** prefer CDC or change tracking over timestamps when available: it
  catches deletes and changes missed by app-maintained timestamps.
- **SHOULD** use UTC for every watermark and record the source time zone.
- **SHOULD** keep raw landed data long enough to replay (retention set on purpose).

## Failure modes

| Failure | Prevention |
|---|---|
| Rows updated in the same second as the watermark are missed | Overlap window plus dedupe |
| Watermark advanced, then the write failed | Advance only after commit |
| CDC retention expired during an outage, changes lost | Monitor lag against retention; full resync procedure ready |
| Deletes never propagate | Delete strategy chosen and tested |
| Bulk fix in the source skips `updated_at` | Prefer CDC; periodic reconciliation |
| A silent zero-row day goes unnoticed for weeks | Expected-volume alerts |
| Masked failure: errors caught and logged but job reports success | Failures raise; audit status checked by the orchestrator |

## Verify

- Run the same batch twice: target unchanged the second time.
- Change, insert and delete one test row in a non-production source: all three
  arrive correctly.
- Key reconciliation: source key count equals target active key count.

## Output

Pipeline code or config, control and audit table DDL
([assets/control-tables.sql](assets/control-tables.sql)), an ADR for the pattern,
and a pipeline spec entry (ENG-03 format if using `de-architecture-docs`).
