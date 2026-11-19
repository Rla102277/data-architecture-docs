---
name: data-profiling
description: >-
  Use when you need to know what is actually in a table before trusting,
  modeling or migrating it: row counts, nulls, distinct values, ranges,
  lengths, top values, candidate keys and duplicate checks, and hints of PII.
  Generates read-only profiling SQL for SQL Server, Fabric Warehouse,
  Snowflake and Spark lakehouse tables, with sampling for big tables.
---

# Data Profiling

Measure the data instead of trusting the column names.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Before modeling a source table, choosing a key or writing a contract.
- When code says one thing and you suspect the data says another.
- Step 7 of `reverse-engineer-data-system`, for the tables that matter.

Not for: ongoing monitoring (use `data-observability`), or pass/fail tests in a
pipeline (use `data-quality-checks`).

## Inspect first

1. Table size (`inventory/rowcounts.csv`). Over about 50 million rows, profile a
   sample first (`--sample`), then confirm specific findings on the full table.
2. Column list and types (`inventory/columns.csv`).
3. Workload: profile replicas or off-peak. Full scans on a busy OLTP primary hurt
   real users. Ask before scanning a production transactional database.

## Procedure

1. Generate the SQL:
   ```bash
   python3 <skill-dir>/scripts/make_profile_sql.py --dialect tsql \
     --table dbo.Orders --columns-csv docs/reverse-engineering/inventory/columns.csv \
     --keys OrderID --keys CustomerID,OrderDate --sample 1000000 \
     --out docs/reverse-engineering/profiles/dbo.Orders.sql
   ```
   Dialects: `tsql` (SQL Server, Azure SQL, Fabric Warehouse), `snowflake`,
   `spark` (Fabric or Databricks lakehouse).
2. Run it read-only. Save results next to the SQL as CSV.
3. Write `profiles/<table>.md`:
   - rows, and the grain you believe the table has (one row per what?)
   - candidate key verdicts from the key checks
   - columns that are always null, constant, or near-unique
   - suspicious values: sentinel dates (`1900-01-01`, `9999-12-31`), `-1`, `'N/A'`,
     empty strings vs nulls, negative amounts, future dates
   - likely PII: names, emails, phones, addresses, national IDs (from names and
     value patterns). Flag, do not copy values into docs.
   - mismatches with code or business rules ("rule says no internal customers; 41 found")
4. For key date columns, add a distribution by month to spot gaps and load changes.

## Standards

- **MUST** be read-only, and ask before full scans of production OLTP systems.
- **MUST NOT** paste PII or sensitive values into docs. Top-value lists for
  sensitive columns are summarized (counts and patterns), not copied.
- **MUST** state whether a result came from a sample or the full table.
- **SHOULD** check uniqueness on the key you intend to use, not the one the
  table claims. Declared keys are often missing or untrusted (`is_not_trusted`).
- **SHOULD** compare empty string and NULL separately; legacy systems mix them.

## Failure modes

| Failure | Prevention |
|---|---|
| Choosing a key that has duplicates | Candidate key check with duplicate group count |
| Sample hides rare bad values | Confirm important findings on the full table |
| PII copied into Git through a profile | Sensitive columns summarized, not listed |
| Profiling slows production | Replica, off-peak or sample, and ask first |
| Min/max on text-cast numbers misleads | Numeric and date ranges checked with typed queries |

## Verify

- Row count in the profile matches `SELECT COUNT(*)` (or the sample size).
- For each declared grain, the key check shows zero duplicate groups and zero null keys.

## Output

`docs/reverse-engineering/profiles/<table>.sql`, `<table>.csv`, `<table>.md`.
