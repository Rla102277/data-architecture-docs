-- Snowflake inventory. Read-only. Replace <DB> with the database name.
-- ACCOUNT_USAGE views need IMPORTED PRIVILEGES on the SNOWFLAKE database and lag by up to a few hours.
-- ACCESS_HISTORY needs Enterprise Edition or higher. Recheck view availability for your edition.

-- 0) context.csv
SELECT CURRENT_ACCOUNT() AS account, CURRENT_REGION() AS region, CURRENT_DATABASE() AS database_name,
       CURRENT_ROLE() AS role_name, CURRENT_TIMESTAMP() AS run_at;

-- 1) objects.csv : tables and views with size
SELECT table_schema, table_name, table_type, row_count, bytes, created, last_altered, is_transient, clustering_key
FROM <DB>.INFORMATION_SCHEMA.TABLES
WHERE table_schema <> 'INFORMATION_SCHEMA'
ORDER BY table_schema, table_name;

-- 2) columns.csv
SELECT table_schema, table_name, ordinal_position, column_name, data_type,
       character_maximum_length, numeric_precision, numeric_scale, is_nullable, column_default
FROM <DB>.INFORMATION_SCHEMA.COLUMNS
WHERE table_schema <> 'INFORMATION_SCHEMA'
ORDER BY table_schema, table_name, ordinal_position;

-- 3) code : views, procedures, functions. Write each to code/<schema>.<object>.<type>.sql
SELECT table_schema AS schema_name, table_name AS object_name, 'VIEW' AS object_type, view_definition AS definition
FROM <DB>.INFORMATION_SCHEMA.VIEWS WHERE table_schema <> 'INFORMATION_SCHEMA'
UNION ALL
SELECT procedure_schema, procedure_name, 'PROCEDURE', procedure_definition
FROM <DB>.INFORMATION_SCHEMA.PROCEDURES
UNION ALL
SELECT function_schema, function_name, 'FUNCTION', function_definition
FROM <DB>.INFORMATION_SCHEMA.FUNCTIONS;

-- 4) dependencies.csv : object to object references
SELECT referencing_database, referencing_schema, referencing_object_name, referencing_object_domain,
       referenced_database, referenced_schema, referenced_object_name, referenced_object_domain, dependency_type
FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
WHERE referencing_database = '<DB>' OR referenced_database = '<DB>';

-- 5) tasks.csv, streams.csv, pipes.csv : scheduled and continuous work
SHOW TASKS IN DATABASE <DB>;
SHOW STREAMS IN DATABASE <DB>;
SHOW PIPES IN DATABASE <DB>;
SHOW DYNAMIC TABLES IN DATABASE <DB>;

-- 6) usage.csv : which objects were read or written in the last 90 days (Enterprise+)
SELECT f.value:"objectName"::string AS object_name,
       COUNT(*) AS accesses, MAX(ah.query_start_time) AS last_access
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY AS ah,
     LATERAL FLATTEN(input => ah.base_objects_accessed) AS f
WHERE ah.query_start_time >= DATEADD(day, -90, CURRENT_TIMESTAMP())
  AND f.value:"objectName"::string ILIKE '<DB>.%'
GROUP BY 1
ORDER BY accesses DESC;

-- 7) query-load.csv : who and what hits this database (30 days)
SELECT user_name, role_name, warehouse_name, query_type, COUNT(*) AS queries,
       SUM(total_elapsed_time) / 1000 AS total_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE database_name = '<DB>' AND start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY 1, 2, 3, 4
ORDER BY queries DESC;

-- 8) grants.csv
SHOW GRANTS ON DATABASE <DB>;
SELECT grantee_name, privilege, granted_on, name AS object_name, table_schema
FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES
WHERE table_catalog = '<DB>' AND deleted_on IS NULL;
