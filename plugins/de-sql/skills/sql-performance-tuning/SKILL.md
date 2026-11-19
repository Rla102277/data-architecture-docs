---
name: sql-performance-tuning
description: >-
  Use when a query, view, procedure, dbt model or report is slow or expensive
  on SQL Server, Azure SQL, Fabric Warehouse, Snowflake or Spark. Measures
  first (execution plans, STATISTICS IO/TIME, Query Store, Snowflake Query
  Profile, Fabric Query Insights, Spark UI), finds the real bottleneck, applies
  the smallest fix and proves the before/after with the same result.
---

# SQL Performance Tuning

Measure, find the one thing that dominates, fix it, prove it. Never tune by folklore.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "This model takes 40 minutes." "Our Snowflake bill doubled." "The report times out."

Not for: style or correctness review (use `sql-style-and-review`).

## Inspect first

1. The exact query and parameters that are slow, and how slow (duration, CPU,
   reads, credits or capacity units). A baseline you can reproduce.
2. Data volume: rows in each input, and how much the filters should keep.
3. The plan or profile for a real run (not an estimate when you can get actual):
   - **SQL Server / Azure SQL**: actual execution plan; `SET STATISTICS IO, TIME ON`;
     Query Store (`sys.query_store_runtime_stats`) for history and plan changes.
   - **Fabric Warehouse**: `queryinsights.exec_requests_history` and
     `queryinsights.long_running_queries`; the query plan via `SHOWPLAN_XML` where supported.
   - **Snowflake**: Query Profile; `ACCOUNT_USAGE.QUERY_HISTORY` columns
     `partitions_scanned`, `partitions_total`, `bytes_spilled_to_local_storage`,
     `bytes_spilled_to_remote_storage`, `queued_overload_time`.
   - **Spark (Fabric, Databricks)**: Spark UI stages and tasks, skew, shuffle
     size, spill; `EXPLAIN FORMATTED`.

## Procedure

1. **Reproduce** the slow run and record the baseline numbers and the result
   checksum (row count plus a sum of a key measure).
2. **Find the dominant operator.** In the plan: the step with most time, reads
   or rows. Ignore the rest until that one is fixed.
3. **Match it to a cause** ([references/causes.md](references/causes.md)):
   scans that should seek or prune, estimate vs actual row gaps (stale
   statistics, parameter sniffing), implicit conversions, spills, skew,
   exploding joins, row-by-row logic, too-small or queued compute.
4. **Apply the smallest fix** that addresses that cause: rewrite a predicate,
   update statistics, add or change one index or clustering key, pre-aggregate,
   change one join, right-size compute. One change at a time.
5. **Re-measure** with the same parameters and data. Keep the change only if it
   is faster AND the result checksum is identical.
6. **Write it up** in the PR or ticket: baseline, cause with plan evidence,
   change, after, and any cost (index storage, write overhead, credits).

## Standards

- **MUST** prove identical results (row count and checksum) before and after.
- **MUST** change one thing at a time and measure each.
- **MUST NOT** add `NOLOCK`, `OPTION (FORCE ORDER)` or other hints as a first fix.
  Hints freeze today's plan into tomorrow's bug; use them only with plan evidence
  and a comment saying why.
- **SHOULD** fix the query before scaling compute. Bigger warehouses and
  capacities hide bad SQL and bill you for it every day.
- **SHOULD** in Snowflake, scale up (bigger warehouse) for spilling and complex
  single queries; scale out (multi-cluster) for queueing from concurrency.
- **SHOULD** in SQL Server analytics workloads, consider clustered columnstore
  for large fact tables before piling on rowstore indexes.
- **SHOULD** in Fabric Warehouse, rely on automatic statistics but create
  statistics manually on join and filter columns when estimates are badly off;
  there are no user-defined indexes to add.

## Failure modes

| Failure | Prevention |
|---|---|
| "Faster" query returns different rows | Checksum gate before and after |
| Tuning a query that runs once a month | Baseline includes frequency and total cost |
| Index added that slows every load | Write cost recorded; index count per table watched |
| Parameter sniffing "fixed" with RECOMPILE everywhere | Use RECOMPILE only on the statement with the evidence, measure compile cost |
| Warehouse upsized instead of fixing a missing filter | Query fixed first, compute last |

## Verify

Before/after table with duration, reads or bytes scanned, partitions scanned,
spill, cost unit, and the identical checksum.

## Output

The changed SQL (or index / statistics / config change) and a short tuning note
with baseline, cause, fix and after.
