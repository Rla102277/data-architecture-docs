-- Assertion templates. Each returns offending rows. Zero rows = pass.
-- Replace table and column names. Works on T-SQL, Snowflake and Spark unless noted.

-- grain / uniqueness
SELECT order_line_id, COUNT(*) AS n
FROM marts.fct_sales
GROUP BY order_line_id
HAVING COUNT(*) > 1;

-- not null on keys
SELECT * FROM marts.fct_sales
WHERE order_line_id IS NULL OR customer_key IS NULL OR order_date IS NULL;

-- referential integrity: facts without a dimension row
SELECT f.*
FROM marts.fct_sales AS f
LEFT JOIN marts.dim_customer AS d ON d.customer_key = f.customer_key
WHERE d.customer_key IS NULL;

-- accepted values
SELECT * FROM marts.dim_customer
WHERE segment NOT IN ('Retail', 'Wholesale', 'Internal');

-- range
SELECT * FROM marts.fct_sales
WHERE amount_usd < 0 AND is_return = 0;

-- business rule: no internal customers in revenue
SELECT f.*
FROM marts.fct_revenue AS f
JOIN marts.dim_customer AS d ON d.customer_key = f.customer_key
WHERE d.segment = 'Internal';

-- freshness: newest row older than 26 hours (T-SQL form; Snowflake/Spark use DATEADD/timestampadd equivalents)
SELECT MAX(loaded_at_utc) AS newest
FROM marts.fct_sales
HAVING MAX(loaded_at_utc) < DATEADD(hour, -26, SYSUTCDATETIME());

-- parity: keys missing either side
SELECT 'missing_in_new' AS side, o.order_line_id
FROM old_schema.fct_sales AS o
LEFT JOIN marts.fct_sales AS n ON n.order_line_id = o.order_line_id
WHERE n.order_line_id IS NULL
UNION ALL
SELECT 'extra_in_new', n.order_line_id
FROM marts.fct_sales AS n
LEFT JOIN old_schema.fct_sales AS o ON o.order_line_id = n.order_line_id
WHERE o.order_line_id IS NULL;

-- parity: value mismatches on matched keys (null-safe for T-SQL before 2022)
SELECT o.order_line_id, o.amount_usd AS old_amount, n.amount_usd AS new_amount
FROM old_schema.fct_sales AS o
JOIN marts.fct_sales AS n ON n.order_line_id = o.order_line_id
WHERE o.amount_usd <> n.amount_usd
   OR (o.amount_usd IS NULL AND n.amount_usd IS NOT NULL)
   OR (o.amount_usd IS NOT NULL AND n.amount_usd IS NULL);
