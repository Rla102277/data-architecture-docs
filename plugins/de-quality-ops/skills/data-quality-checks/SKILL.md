---
name: data-quality-checks
description: >-
  Use when deciding what data quality checks a pipeline or data product needs
  and wiring them in: completeness, uniqueness, validity, referential
  integrity, freshness and volume checks, severity (block vs warn), where each
  check runs (landing, staging, marts), quarantine of bad rows, ownership, and
  tooling (dbt tests, Great Expectations, Soda, platform constraints).
---

# Data Quality Checks

Check what would make a decision wrong, at the point where it is cheapest to
catch, and decide in advance what happens when it fails.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New pipeline or data product.
- After an incident: add the check that would have caught it.

Not for: reconciling totals to a system of record (use `data-reconciliation`),
or alerting and dashboards (use `data-observability`).

## Inspect first

1. Consumers and their tolerance: what decision, how wrong is too wrong, how late is too late.
2. The data's known problems (profiles, past incidents, open questions).
3. Existing tooling: dbt tests, a DQ tool, platform constraints.

## Procedure

1. **List failure modes per dataset** from the consumer backwards: duplicates,
   missing keys, orphans, invalid codes, out-of-range amounts, stale data, sudden
   volume drops, schema changes.
2. **Assign each a check, a layer and a severity**
   ([assets/dq-plan-template.md](assets/dq-plan-template.md)):
   - landing: schema and volume (did we get a file, with the right columns, roughly the right size?)
   - staging: types, nulls on keys, accepted values, duplicates
   - marts: grain, referential integrity, business rules, reconciliation hooks
   - severity `block` (stop publish) or `warn` (publish and flag)
3. **Decide failure behavior**: block the publish (dbt `error` tests gate
   downstream), quarantine bad rows to a `_rejected` table with the reason and
   keep the good rows, or publish with a flag. Quarantine only when partial data
   is still correct for consumers.
4. **Assign an owner** per check: who fixes the data, who gets paged.
5. **Implement** in the existing tool. Prefer dbt tests for warehouse data;
   dataframe checks (Great Expectations, Soda, Deequ) for Spark and files.
6. **Record results** in a table (check, run, status, failing row count) so trends
   are visible and `data-observability` can alert.

## Standards

- **MUST** block publish for any check whose failure makes a published number wrong.
- **MUST** give every check an owner.
- **MUST** keep quarantined rows queryable with the failure reason, and count
  them; silent dropping is data loss.
- **SHOULD** check volume against history (e.g. outside plus or minus 3 standard
  deviations of the same weekday) rather than fixed thresholds alone.
- **SHOULD** start small: grain, keys, freshness, volume on every dataset, then
  rules where they matter. Hundreds of noisy warnings train people to ignore all.

## Failure modes

| Failure | Prevention |
|---|---|
| Bad data published because checks only warn | Block severity for number-changing checks |
| Alert fatigue from noisy checks | Few, owned checks; tune or remove noisy ones |
| Rows silently dropped by a filter | Quarantine with reason and count |
| Checks only at the end, failures expensive to trace | Checks per layer |
| Nobody fixes failing checks | Owner per check |

## Verify

Inject a known bad row (duplicate key, null key, invalid code) in a test
environment and confirm the right check fails with the right severity and
behavior.

## Output

A DQ plan per dataset, implemented checks, quarantine tables where used, and a
results table.
