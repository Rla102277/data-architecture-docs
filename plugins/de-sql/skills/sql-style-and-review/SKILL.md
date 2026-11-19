---
name: sql-style-and-review
description: >-
  Use when writing new analytical SQL or reviewing a SQL change, query, view,
  stored procedure or dbt model before it merges: T-SQL, Snowflake or Spark
  SQL. Applies a house style (CTEs, explicit columns, naming, null-safe logic)
  and a correctness-first review checklist covering grain, joins, fan-out,
  nulls, dates, time zones, determinism and security.
---

# SQL Style and Review

Write SQL a stranger can read and review SQL for the bugs that pass tests.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Writing a new query, view, model or procedure.
- Reviewing someone's SQL in a PR.

Not for: making a slow query fast (use `sql-performance-tuning`), or cleaning up
legacy code with parity proof (use `sql-refactoring`).

## Inspect first

1. The dialect and engine version (T-SQL on SQL Server 2019 vs 2022 vs Fabric
   Warehouse, Snowflake, Spark). Features differ.
2. The grain of every input table and the intended grain of the output.
3. Existing project style: `.sqlfluff`, dbt conventions, a style guide. The
   project's style wins over this one where they conflict.

## Procedure

**Writing**
1. State the output grain in a comment on line one: `-- grain: one row per order line`.
2. Build with CTEs, one job each, in reading order: `source` CTEs, then
   `filtered`, `joined`, `aggregated`, `final`. End with `select * from final`
   only in dbt, otherwise list columns.
3. Join on keys you have proven unique on one side. Name the relationship in a
   comment if it is not obvious (`-- many orders to one customer`).
4. Make null and empty handling explicit.
5. Run it, check the row count against the grain, and look at 20 rows.

**Reviewing** (use [references/review-checklist.md](references/review-checklist.md))
1. Read the grain claim, then check each join against it for fan-out.
2. Walk the checklist. Every finding gets a severity: blocker, should-fix, nit.
3. Ask for evidence when a claim needs data: "show the row count before and
   after this join".

## Standards

- **MUST** list columns explicitly past the staging layer. `SELECT *` hides
  schema drift and breaks consumers silently.
- **MUST** qualify every column with its table alias when more than one table is in scope.
- **MUST** use `LEFT JOIN` only when you mean "keep rows with no match", and say
  what null means for the right side.
- **MUST** use half-open date ranges: `>= '2026-01-01' AND < '2026-02-01'`, never
  `BETWEEN` on timestamps (it misses or double-counts boundary rows).
- **MUST NOT** use `NOLOCK` / `READ UNCOMMITTED` for anything that feeds a number
  people trust. It returns dirty, missing and duplicated rows.
- **SHOULD** use lowercase keywords or uppercase consistently (follow the
  project linter, e.g. sqlfluff). Leading commas or trailing: pick one, enforce it.
- **SHOULD** name things for the business: `order_amount_usd`, not `amt2`.
  Booleans `is_` / `has_`, timestamps `_at` or `_utc`, dates `_date`.
- **SHOULD** avoid functions on filtered columns (`WHERE YEAR(order_date) = 2026`);
  write the range instead. It is clearer and sargable.
- **MAY** use `QUALIFY` (Snowflake, Spark, Databricks) for window filters; in
  T-SQL wrap the window in a CTE.

## Failure modes

| Failure | Prevention |
|---|---|
| Join fan-out inflates sums | Grain comment plus uniqueness proof on the "one" side |
| `NOT IN` with a NULL in the subquery returns nothing | Use `NOT EXISTS` |
| `COUNT(col)` vs `COUNT(*)` confusion | Say which you mean; nulls are not counted by `COUNT(col)` |
| Integer division (`1/2 = 0` in T-SQL) | Cast to decimal before dividing |
| Non-deterministic `ROW_NUMBER()` dedupe | `ORDER BY` must include a unique tiebreaker |
| Time zone drift | Store UTC; convert once at the edge with an explicit zone |
| Implicit conversion (`varchar` vs `nvarchar`, string vs date) | Compare like types; cast literals |

## Verify

- Row count matches the stated grain: `COUNT(*) = COUNT(DISTINCT <grain key>)`.
- Totals match a trusted source or the previous version for the same period.
- Linter passes (`sqlfluff lint` with the project config).

## Output

The SQL, with the grain comment, and for reviews a list of findings with
severity, line and suggested fix.
