---
name: data-reconciliation
description: >-
  Use when warehouse or lakehouse numbers must tie to a system of record:
  source-to-target row and amount reconciliation, GL tie-outs for revenue,
  COGS and margin, tolerance rules, timing differences, reconciliation
  evidence for SOX and audit, and automated reconciliation reports that run
  with every load.
---

# Data Reconciliation

Prove the platform's numbers tie to the books, explain every difference, and keep
the evidence.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Finance-facing data products (revenue, margin, AR, AP, inventory value).
- Migrations (with `legacy-to-dbt-migration` parity) and audits.

Not for: generic data quality checks (use `data-quality-checks`).

## Inspect first

1. The system of record for each number (GL in the ERP, the billing system) and
   who owns the tie-out (Controller, accounting).
2. Timing: when the source closes a period, cutoffs, posting lags, time zones.
3. Known legitimate differences: manual journal entries not in subledgers,
   intercompany eliminations, currency revaluation, accruals.

## Procedure

1. **Define each reconciliation** ([assets/recon-definition.md](assets/recon-definition.md)):
   measure, grain (period, entity, account), source query, target query,
   tolerance (absolute and percent), and owner.
2. **Reconcile at three levels**:
   - counts: rows or documents per period
   - amounts: sums per period, entity, account
   - drill-down: list the specific documents that differ when a level fails
3. **Classify differences**: timing (will clear next period), known adjustment
   (documented, with the journal reference), data error (bug, fix it), unknown
   (investigate, owner assigned).
4. **Automate**: run after every load into a `recon_results` table (run id,
   check, period, source value, target value, difference, status) and block or
   flag publish per the severity agreed with finance.
5. **Evidence**: keep results, queries and sign-offs for the retention period your
   audit requires; sign-off per period by the owner.

## Standards

- **MUST** reconcile to the system of record, not to another report.
- **MUST** use the same period definition, cutoff and currency on both sides.
- **MUST** explain every difference above tolerance; "rounding" needs to be shown.
- **MUST** keep recon queries in version control, so the evidence is reproducible.
- **SHOULD** tie out at the account level for GL-based measures, not only totals;
  offsetting errors hide in totals.

## Failure modes

| Failure | Prevention |
|---|---|
| Totals tie while two accounts are off in opposite directions | Account-level reconciliation |
| Timing differences mistaken for bugs (or bugs for timing) | Explicit timing classification and next-period clearance check |
| Currency or sign conventions differ | Same currency and sign rules documented on both sides |
| Evidence cannot be reproduced at audit time | Queries versioned, results stored |
| Differences accepted without an owner | Owner sign-off per period |

## Verify

The last closed period ties within tolerance at every level, with each remaining
difference classified and signed off.

## Output

Reconciliation definitions, automated recon queries, a `recon_results` table, and
per-period sign-off records.
