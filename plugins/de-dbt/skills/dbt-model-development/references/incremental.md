# Incremental models

## Merge with lookback (the default for mutable sources)

```sql
{{
  config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_line_id',
    on_schema_change='append_new_columns'
  )
}}

with src as (
    select * from {{ ref('stg_erp__order_lines') }}
    {% if is_incremental() %}
    -- 3-day lookback catches late and corrected rows; the merge makes reprocessing safe
    where modified_at >= (select dateadd(day, -3, max(modified_at)) from {{ this }})
    {% endif %}
),
deduped as (
    select *,
           row_number() over (partition by order_line_id order by modified_at desc, loaded_at desc) as rn
    from src
)
select order_line_id, order_id, amount, modified_at
from deduped
where rn = 1
```

`dateadd` syntax is T-SQL and Snowflake; use `date_sub` / `interval` on Spark, or
`{{ dbt.dateadd('day', -3, 'max(modified_at)') }}` for a cross-database version.

## Choosing a strategy

| Strategy | Use when | Watch out |
|---|---|---|
| merge | Rows update in place, a unique key exists | Key must be unique in the batch; cost grows with target size on some engines |
| delete+insert | Replace all rows for the keys or dates in the batch | Batch must contain the complete set for each key or date |
| insert_overwrite | Partitioned tables on Spark or BigQuery; replace whole partitions | Partition column must be in the filter; partial partitions get wiped |
| append | Immutable events, never updated | Reruns duplicate rows unless the window is exact |
| microbatch | Large time-series facts; dbt 1.9+ | Needs `event_time`, `batch_size`, `begin`; check adapter support |

Support varies by adapter and version (dbt-fabric, dbt-sqlserver,
dbt-snowflake, dbt-databricks, dbt-fabricspark). Check the adapter docs before
choosing, and record the choice in the model's yml description.

## Deletes

Incremental filters never see deleted source rows. Pick one:
1. Source sends deletes (CDC, soft-delete flag): carry `is_deleted` and filter in marts.
2. Periodic reconciliation model: compare keys with the source and mark missing ones.
3. Scheduled full refresh (weekly) if the table is small enough.

## Full refresh and backfill

- `dbt build --select my_model --full-refresh` rebuilds from scratch. Know how
  long it takes and what it costs before you need it at 2am.
- For a date-range backfill, pass vars (`--vars '{start: 2026-01-01, end: 2026-02-01}'`)
  and filter on them, or use microbatch with `--event-time-start` / `--event-time-end`.
