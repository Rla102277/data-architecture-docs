# Set-based replacements

## Cursor computing a running total -> window function

```sql
-- before: cursor over orders, adding amount to @running per customer
-- after (T-SQL 2012+, Snowflake, Spark):
SELECT customer_id, order_id, order_date, amount,
       SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_amount
FROM sales.orders;
```
Use `ROWS`, not the default `RANGE`, or ties on `order_date` get the same total.

## Loop that keeps "latest row per key" -> ROW_NUMBER

```sql
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC, source_row_id DESC) AS rn
  FROM stage.customers
)
SELECT * FROM ranked WHERE rn = 1;
```
Always end the `ORDER BY` with a unique column so the pick is deterministic.

## Correlated subquery for "previous value" -> LAG

```sql
SELECT order_id, customer_id, order_date,
       LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS previous_order_date
FROM sales.orders;
```

## Row-by-row upsert -> one MERGE (or delete + insert)

```sql
MERGE dw.dim_customer AS t
USING stage.customers_latest AS s
  ON t.customer_id = s.customer_id
WHEN MATCHED AND (t.name <> s.name OR t.segment <> s.segment) THEN
  UPDATE SET t.name = s.name, t.segment = s.segment, t.updated_at = SYSUTCDATETIME()
WHEN NOT MATCHED BY TARGET THEN
  INSERT (customer_id, name, segment, updated_at) VALUES (s.customer_id, s.name, s.segment, SYSUTCDATETIME());
```
`MERGE` needs a unique source key (dedupe first) and a terminating semicolon in
T-SQL. The `<>` change check is not null-safe; on SQL Server 2022, Snowflake and
Spark use `IS DISTINCT FROM`, otherwise compare a hash of the columns.

## Scalar UDF per row -> inline expression or lookup join

Replace `dbo.fn_GetRegion(state_code)` with a join to a region lookup table, or
an inline `CASE` if the logic is small and stable.

## Gaps and islands (consecutive runs) -> difference of row numbers

```sql
WITH x AS (
  SELECT customer_id, activity_date,
         DATEADD(day, -ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY activity_date), activity_date) AS grp
  FROM sales.daily_activity
)
SELECT customer_id, MIN(activity_date) AS streak_start, MAX(activity_date) AS streak_end, COUNT(*) AS days
FROM x GROUP BY customer_id, grp;
```
