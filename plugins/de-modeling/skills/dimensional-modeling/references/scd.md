# Slowly changing dimensions

| Type | Behavior | Use for |
|---|---|---|
| 0 | Never changes after first load | Original values: original credit score, signup channel |
| 1 | Overwrite | Corrections, attributes nobody reports "as was" |
| 2 | New row per change, `valid_from`, `valid_to`, `is_current` | Attributes that change meaning of history: customer segment, sales territory, product category |
| 3 | Keep previous value in an extra column | One planned reorganization you want to compare |
| Mini-dimension | Split fast-changing attributes into their own dimension | Age bands, scores that change monthly on millions of customers |

## Type 2 columns

```sql
customer_key       -- surrogate key, unique per version
customer_id        -- business key, repeats across versions
...attributes...
valid_from         -- inclusive
valid_to           -- exclusive; '9999-12-31' for current
is_current         -- 1 for the current version
row_hash           -- hash of tracked attributes, for change detection
```

Fact load: look up the version where `fact_date >= valid_from AND fact_date < valid_to`,
and store that `customer_key` on the fact. Reports then see history as it was,
and filtering on current attributes uses `is_current` through a separate
current view if needed.

In dbt, Type 2 from a mutable source is usually a snapshot plus a dimension
model that adds the surrogate key and the unknown member.
