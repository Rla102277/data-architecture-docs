# Parity testing

Compare a legacy output and its dbt replacement on the same inputs and as-of time.

## 1. Row counts and key coverage (both directions)

```sql
-- keys in legacy but not in new, and in new but not in legacy
SELECT 'missing_in_new' AS side, COUNT(*) AS n
FROM legacy.FactSales l
LEFT JOIN new_marts.fct_sales n ON n.order_line_id = l.OrderLineID
WHERE n.order_line_id IS NULL
UNION ALL
SELECT 'extra_in_new', COUNT(*)
FROM new_marts.fct_sales n
LEFT JOIN legacy.FactSales l ON l.OrderLineID = n.order_line_id
WHERE l.OrderLineID IS NULL;
```

## 2. Column-by-column mismatches on matched keys

```sql
SELECT
  SUM(CASE WHEN l.Amount <> n.amount OR (l.Amount IS NULL) <> (n.amount IS NULL) THEN 1 ELSE 0 END) AS amount_mismatch,
  SUM(CASE WHEN l.CustomerKey <> n.customer_key THEN 1 ELSE 0 END) AS customer_mismatch,
  COUNT(*) AS matched_rows
FROM legacy.FactSales l
JOIN new_marts.fct_sales n ON n.order_line_id = l.OrderLineID;
```

T-SQL has no `IS DISTINCT FROM` before SQL Server 2022; use the null-safe form
above. Snowflake and Spark: `l.amount IS DISTINCT FROM n.amount`.

## 3. Aggregate checks people will notice

Totals by month and by top dimension members (region, product line). If line
level matches but totals do not, there is a duplicate or a filter difference.

## 4. dbt helpers

- `dbt-audit-helper` package: `compare_relations`, `compare_column_values` and
  `compare_all_columns` macros produce the same comparisons inside dbt.
  Check the package version against your dbt version before installing.

## 5. Report

For each output and day: matched rows, missing, extra, mismatches per column,
and an explanation for every non-zero line (approved rule change, documented
legacy bug, or new bug with a fix ticket).
