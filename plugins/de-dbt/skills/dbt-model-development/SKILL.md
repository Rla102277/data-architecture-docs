---
name: dbt-model-development
description: >-
  Use when writing or changing dbt models: staging, intermediate and mart
  models, choosing materializations, building incremental models (merge,
  delete+insert, append, insert_overwrite, microbatch) with correct unique_key,
  lookback for late data and on_schema_change, snapshots for SCD Type 2,
  ref and source usage, macros, and documentation.
---

# dbt Model Development

Write dbt models that are correct on the first run, correct on every rerun, and
obvious to the next engineer.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New model or a change to an existing one.
- Turning a full-refresh model incremental because it got slow or expensive.
- Tracking history of a mutable source (snapshots).

Not for: tests and contracts in depth (`dbt-testing-and-contracts`), project
structure (`dbt-project-setup`).

## Inspect first

1. The grain of the model you are writing, and the grain and keys of each input
   (profile them if unknown: `data-profiling`).
2. Upstream and downstream: `dbt ls --select +my_model+` and the docs DAG.
3. For incrementals: the source's change signal (reliable `updated_at`? CDC?
   deletes?), how late data can arrive, and the table size.
4. The adapter's supported incremental strategies. Recheck: support differs by
   adapter and version.

## Procedure

**Staging model** (one per source table)
```sql
-- grain: one row per order line   (dialect: T-SQL, Fabric Warehouse / SQL Server)
with source as (
    select * from {{ source('erp', 'order_lines') }}
),
renamed as (
    select
        cast(OrderLineID as bigint)         as order_line_id,
        cast(OrderID as bigint)             as order_id,
        cast(Amount as decimal(18, 2))      as amount,
        cast(ModifiedAt as datetime2(3))    as modified_at,
        _loaded_at                          as loaded_at
    from source
)
select * from renamed
```
Rename, cast, standardize nulls and units. No joins, no business logic.

**Mart model**: build from `ref()` only, with CTEs per step, ending in an explicit column list.

**Incremental model** (see [references/incremental.md](references/incremental.md))
1. Pick the strategy: `merge` (upserts by key), `delete+insert` (replace a key
   or partition set), `insert_overwrite` (replace whole partitions, Spark/BigQuery),
   `append` (immutable events only), `microbatch` (time-sliced, dbt 1.9+).
2. Set `unique_key` to the true grain key, proven unique.
3. Filter with a lookback for late data, not `> max(updated_at)` alone.
4. Set `on_schema_change` (`append_new_columns` is a sane default; `fail` for
   contracted marts).
5. Plan the backfill and full-refresh path before shipping.

**Snapshot** (SCD2 of a mutable source): `strategy: timestamp` with
`updated_at` when it is trustworthy, else `check` with `check_cols`. Snapshot
the source as close to raw as possible, not a transformed model.

**Docs**: every model and column described in the `.yml`; grain in the model description.

## Standards

- **MUST** use `ref()` and `source()`, never hard-coded relation names.
- **MUST** state the grain and prove it with a unique test on the grain key.
- **MUST** include a lookback window on incremental filters for any source with
  late or corrected data.
- **MUST** make incremental models idempotent: rerunning the same window gives
  the same result.
- **SHOULD** default to views for staging, ephemeral or views for intermediate,
  tables for marts; go incremental only when a table build is too slow or costly.
- **SHOULD** keep Jinja light. A model that is mostly macros is unreadable;
  macros are for repeated patterns, not to hide SQL.
- **SHOULD NOT** put business logic in staging.

## Failure modes

| Failure | Prevention |
|---|---|
| Duplicates after merge because `unique_key` is not unique | Unique test on the key, dedupe in the model |
| Late-arriving rows never loaded | Lookback window on the incremental filter |
| Deleted source rows live forever in the incremental | Handle deletes: soft-delete flag, periodic full refresh, or CDC delete events |
| Schema change breaks the run at 2am | `on_schema_change` set on purpose |
| `is_incremental()` first-run bug | Test full-refresh and incremental runs both |
| Snapshot on a transformed model loses history when logic changes | Snapshot near raw |

## Verify

- `dbt build --select my_model+` passes in dev.
- For incrementals: run full refresh, then incremental twice with no new data.
  Row count and checksums must not change.
- Compare a total against the previous version or source for the same period.

## Output

Model SQL, `.yml` with descriptions and tests, and for incrementals a note on
strategy, key, lookback, delete handling and full-refresh plan.
