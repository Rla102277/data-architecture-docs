---
name: sql-testing
description: >-
  Use when SQL logic needs proof: unit-style tests on fixed inputs, assertion
  queries that must return zero rows, parity checks between an old and new
  query or table, golden datasets, and regression checks for views, stored
  procedures and dbt models on SQL Server, Fabric, Snowflake or Spark.
---

# SQL Testing

Turn "looks right" into queries that fail loudly when it is not.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New or changed transformation logic.
- Refactors and migrations (parity).
- A bug fix: write the test that would have caught it, first.

Not for: production data quality monitoring (use `data-quality-checks`); dbt
projects (use `dbt-testing-and-contracts`, which builds on this).

## Inspect first

1. What must be true of the output: grain, keys, totals, business rules (`rules/`).
2. Where tests can run: a dev or CI database, dbt, tSQLt (SQL Server), or plain
   assertion scripts in CI.
3. Fixed test inputs: small, hand-built rows that hit each rule and edge case.

## Procedure

1. **Assertions as zero-row queries.** Each test is a `SELECT` that returns the
   bad rows. Zero rows passes. See [references/assertions.sql](references/assertions.sql).
   - grain: duplicates on the key
   - not null on keys and required columns
   - referential: facts without a dimension row
   - accepted values and ranges
   - business rules: e.g. no internal customers in revenue
2. **Unit tests on fixed inputs.** Build tiny input tables (CTEs, seeds or temp
   tables) with one row per case: normal, null, duplicate, late, boundary date,
   negative amount. Assert the exact expected output rows.
3. **Parity tests** when replacing logic: keys both ways and column mismatches
   (template in [references/assertions.sql](references/assertions.sql)).
4. **Wire into CI**: tests run on every change against a CI database; a
   non-empty result fails the build and prints the first rows.
5. **Bug fix rule**: reproduce the bug as a failing test, then fix.

## Standards

- **MUST** make every test return the offending rows, not just a count, so a
  failure explains itself.
- **MUST** use fixed inputs for logic tests. Tests that depend on today's
  production data pass or fail by accident.
- **MUST** name tests for the rule they protect: `assert_no_internal_customers_in_revenue`.
- **SHOULD** cover the edges: nulls, empty strings, duplicates, ties, month
  and year boundaries, time zones, negative and zero amounts.
- **SHOULD** use tSQLt on SQL Server when testing procedures with side effects
  (it fakes tables and isolates each test in a transaction).

## Failure modes

| Failure | Prevention |
|---|---|
| Tests pass because the test data has no edge cases | One fixed row per edge case |
| Test "passes" on an empty output | Assert expected row counts too |
| Parity on counts only | Column-level mismatch checks |
| Flaky tests from live data | Fixed inputs for logic, live data only for monitoring |
| Tests nobody runs | CI gate that fails the build |

## Verify

Break the logic on purpose (flip a filter) and confirm at least one test fails.
A suite that never fails proves nothing.

## Output

Test SQL files (or dbt tests), fixture data, and a CI step that runs them.
