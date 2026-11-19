-- Microsoft Fabric inventory. Read-only.
-- Fabric Warehouse and the Lakehouse SQL analytics endpoint support a SUBSET of SQL Server catalog
-- views. Recheck current support before relying on a view; if one errors, record it and move on.
-- Guidance checked 2026-11; recheck before citing.

-- ===== Warehouse / SQL analytics endpoint (T-SQL) =====

-- 1) objects.csv
SELECT s.name AS schema_name, o.name AS object_name, o.type_desc, o.create_date, o.modify_date
FROM sys.objects AS o
JOIN sys.schemas AS s ON s.schema_id = o.schema_id
WHERE o.is_ms_shipped = 0
ORDER BY s.name, o.type_desc, o.name;

-- 2) columns.csv
SELECT TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION, COLUMN_NAME, DATA_TYPE,
       CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;

-- 3) code : views, procedures, functions
SELECT OBJECT_SCHEMA_NAME(m.object_id) AS schema_name, OBJECT_NAME(m.object_id) AS object_name,
       o.type_desc, m.definition
FROM sys.sql_modules AS m
JOIN sys.objects AS o ON o.object_id = m.object_id;

-- 4) query-history.csv : Query Insights (last 30 days kept by Fabric)
SELECT TOP 1000 start_time, end_time, login_name, status, total_elapsed_time_ms, row_count, command
FROM queryinsights.exec_requests_history
ORDER BY start_time DESC;

-- 5) frequent-queries.csv
SELECT TOP 200 * FROM queryinsights.frequently_run_queries;

-- ===== Lakehouse (Spark SQL in a notebook) =====
-- SHOW TABLES IN <lakehouse>;
-- DESCRIBE TABLE EXTENDED <lakehouse>.<table>;      -- schema, location, properties
-- DESCRIBE DETAIL <lakehouse>.<table>;              -- files, size, partition columns
-- DESCRIBE HISTORY <lakehouse>.<table> LIMIT 50;    -- writes: who, when, operation, metrics

-- ===== Pipelines, notebooks, semantic models =====
-- Not in SQL. Use the workspace Git integration (item definitions as files) or the Fabric REST API
-- "Get Item Definition". Hand pipeline JSON to the etl-package-analysis skill.
