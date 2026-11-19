---
name: dimensional-modeling
description: >-
  Use when designing or reviewing analytics tables for reporting and BI: Kimball
  star schemas, choosing the grain, fact types (transaction, periodic snapshot,
  accumulating snapshot, factless), conformed dimensions, slowly changing
  dimensions (Type 1, 2, 3, mini-dimensions), surrogate keys, date dimensions,
  role-playing and junk dimensions, and bus matrices for Power BI and other tools.
---

# Dimensional Modeling

Model for the questions people ask, at a grain you can defend.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Designing marts or a gold layer for Power BI, Tableau or SQL users.
- Reviewing a mart that gives "different numbers in different reports".

Not for: integration and history layers built for auditability across many
sources (use `data-vault-modeling`), or OLTP design.

## Inspect first

1. The business process and the questions: "revenue by customer segment and
   month", "days from order to delivery". Get 5 to 10 real questions.
2. Source data at its lowest grain (profile it: `data-profiling`).
3. Existing conformed dimensions (customer, product, date, location, employee).
   Reuse before you create.

## Procedure

Kimball's four steps, made concrete, plus keys and a spec.

1. **Pick the business process**: one fact table per process (orders, shipments,
   invoices), not per report.
2. **Declare the grain** in one sentence before choosing columns:
   "one row per order line as of its latest state". Atomic grain first;
   aggregates are built from it later.
3. **Choose dimensions** that describe the grain: who, what, where, when, why,
   how. Build a bus matrix ([assets/bus-matrix-template.md](assets/bus-matrix-template.md)):
   processes as rows, conformed dimensions as columns.
4. **Choose facts**: additive (amount, quantity), semi-additive (balances: add
   across accounts, not across time), non-additive (ratios: store the parts,
   compute the ratio in the semantic layer).
5. **Pick the fact type**:
   - transaction: one row per event
   - periodic snapshot: one row per entity per period (inventory per day)
   - accumulating snapshot: one row per pipeline instance with milestone dates
     (order to ship to deliver), updated as it moves
   - factless: events with no measure (attendance, coverage)
6. **Decide history per dimension attribute** ([references/scd.md](references/scd.md)):
   Type 1 overwrite, Type 2 new row with `valid_from`/`valid_to`/`is_current`,
   Type 3 previous-value column, mini-dimension for fast-changing attributes.
7. **Keys**: surrogate keys on dimensions (hash of business key, or sequence),
   with an unknown member row (`-1` or a fixed hash) so facts never point at nothing.
   Facts carry dimension surrogate keys plus degenerate dimensions (order number).
8. **Write it down** as a model spec per table: grain, keys, columns, SCD type,
   source mapping, tests.

## Standards

- **MUST** declare the grain before adding a single column, and test it.
- **MUST** use conformed dimensions across facts so filters mean the same thing everywhere.
- **MUST** give every fact row a valid dimension key (unknown member for missing).
- **MUST** store additive components, not precomputed ratios or percentages.
- **SHOULD** keep facts narrow and dimensions wide.
- **SHOULD** build a real date dimension (fiscal calendar, holidays, week rules)
  rather than date functions in every report.
- **SHOULD** use Type 2 only for attributes where "as it was" reporting is needed.
  Type 2 everything multiplies rows and confuses users.
- **SHOULD** for Power BI: one-to-many relationships from dimension to fact,
  single-direction filters, no snowflaking unless a dimension is huge.

## Failure modes

| Failure | Prevention |
|---|---|
| Mixed grain in one fact (orders and lines) | Grain sentence plus uniqueness test |
| Different "customer" in two reports | Conformed dimension with one owner |
| Averages of averages | Store numerator and denominator, compute in the semantic layer |
| Balances summed across months | Mark semi-additive facts; use last-period logic in measures |
| Facts dropped by inner joins to missing dimension rows | Unknown member row |
| SCD2 join picks multiple rows | Join on surrogate key, or on business key plus date between valid_from and valid_to |

## Verify

- Grain test passes (`unique` on the grain key).
- Fact total equals source total for the same period.
- Every fact foreign key resolves to a dimension row (relationships test).
- Each of the original business questions can be answered with one simple query.

## Output

Bus matrix, a model spec per fact and dimension, and the dbt models with tests
(`dbt-model-development`).
