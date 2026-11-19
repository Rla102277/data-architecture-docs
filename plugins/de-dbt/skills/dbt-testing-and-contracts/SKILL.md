---
name: dbt-testing-and-contracts
description: >-
  Use when adding or reviewing tests in a dbt project: generic tests (unique,
  not_null, relationships, accepted_values), dbt-utils and dbt-expectations
  tests, singular tests, unit tests on fixed inputs (dbt 1.8+), model
  contracts with enforced data types and constraints, severity and warn/error
  thresholds, store_failures, and source freshness.
---

# dbt Testing and Contracts

Decide what must never break, test exactly that, and let contracts stop bad
shapes before they ship.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Every new model; every bug fix (test first).
- Publishing a mart other teams or reports depend on (contracts).

Not for: production monitoring dashboards (`data-observability`).

## Inspect first

1. The model's grain, keys and business rules (`rules/` catalog if it exists).
2. Who consumes it, and what a bad row would cost them. That sets severity.
3. dbt version (unit tests need 1.8+) and adapter support for contracts and constraints.

## Procedure

1. **Baseline tests on every model** (in the model's `.yml`):
   - grain key: `unique` and `not_null` (or `dbt_utils.unique_combination_of_columns`)
   - foreign keys to dimensions: `relationships`
   - categorical columns: `accepted_values`
2. **Business rule tests**: singular tests in `tests/` named for the rule
   (`assert_no_internal_customers_in_revenue.sql`) that return offending rows.
3. **Unit tests** for tricky logic (dedupe, SCD, date math, allocation):
   ```yaml
   unit_tests:
     - name: latest_row_wins_on_tie_by_loaded_at
       model: int_order_lines__deduped
       given:
         - input: ref('stg_erp__order_lines')
           rows:
             - {order_line_id: 1, amount: 10, modified_at: "2026-01-01 10:00", loaded_at: "2026-01-01 11:00"}
             - {order_line_id: 1, amount: 12, modified_at: "2026-01-01 10:00", loaded_at: "2026-01-01 12:00"}
       expect:
         rows:
           - {order_line_id: 1, amount: 12}
   ```
4. **Contracts** on published marts: `contract: {enforced: true}` with
   `data_type` on every column, plus `constraints` (not_null, primary_key) where
   the platform enforces or at least records them.
5. **Severity**: `error` for anything that makes a number wrong; `warn` for
   anomalies to investigate; thresholds with `warn_if` / `error_if` for tests
   that tolerate a few known exceptions (document why).
6. **Failures you can read**: `store_failures: true` on important tests so the
   bad rows land in a table people can query.
7. **Source freshness**: `loaded_at_field` and thresholds on every source; run
   `dbt source freshness` before builds in production.

## Standards

- **MUST** test the grain of every model.
- **MUST** use `error` severity for tests protecting published numbers, so
  `dbt build` stops downstream models from building on bad data.
- **MUST** write the test before the fix for any data bug.
- **SHOULD** enforce contracts on every model exposed to BI or other teams.
- **SHOULD** keep tests fast: filter big-table tests to recent partitions with
  `where:` config when full scans are too costly, and say so.
- **SHOULD NOT** mute a failing test with `warn` to get a green build. Fix it or
  record the exception with a threshold and an owner.

## Failure modes

| Failure | Prevention |
|---|---|
| Tests pass, number is wrong (rule untested) | Singular tests per business rule |
| Logic bug in edge case never caught | Unit tests with edge rows |
| Column type silently changes and breaks Power BI | Enforced contract |
| Warn-level tests ignored forever | Error for published numbers; warn has an owner |
| Test on huge table times out builds | `where:` filter with a documented window |

## Verify

Break the model on purpose (duplicate a row, flip a filter) and confirm
`dbt build` fails on the test you expect.

## Output

Updated `.yml` files with tests and contracts, singular tests in `tests/`, unit
tests, and freshness on sources.
