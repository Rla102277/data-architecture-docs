-- SQL Server / Azure SQL Database inventory. Read-only catalog queries.
-- Run in the target database. Save each result to the CSV named in its header.
-- Requires VIEW DEFINITION; usage DMVs need VIEW SERVER STATE (or VIEW DATABASE STATE on Azure SQL);
-- job queries need read access to msdb (not available on Azure SQL Database).

-- 0) context.csv : where and when this ran
SELECT @@SERVERNAME AS server_name, DB_NAME() AS database_name, SYSUTCDATETIME() AS run_at_utc,
       (SELECT sqlserver_start_time FROM sys.dm_os_sys_info) AS sqlserver_start_time,
       SERVERPROPERTY('ProductVersion') AS product_version, SERVERPROPERTY('Edition') AS edition;

-- 1) objects.csv : every user object
SELECT s.name AS schema_name, o.name AS object_name, o.type, o.type_desc,
       o.create_date, o.modify_date
FROM sys.objects AS o
JOIN sys.schemas AS s ON s.schema_id = o.schema_id
WHERE o.is_ms_shipped = 0
  AND o.type IN ('U','V','P','FN','IF','TF','TR','SN','SO','X')
ORDER BY s.name, o.type_desc, o.name;

-- 2) columns.csv
SELECT c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION, c.COLUMN_NAME, c.DATA_TYPE,
       c.CHARACTER_MAXIMUM_LENGTH, c.NUMERIC_PRECISION, c.NUMERIC_SCALE, c.IS_NULLABLE, c.COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS AS c
ORDER BY c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION;

-- 3) keys.csv : primary keys and unique constraints
SELECT tc.TABLE_SCHEMA, tc.TABLE_NAME, tc.CONSTRAINT_TYPE, tc.CONSTRAINT_NAME,
       kcu.COLUMN_NAME, kcu.ORDINAL_POSITION
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu
  ON kcu.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA AND kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
WHERE tc.CONSTRAINT_TYPE IN ('PRIMARY KEY','UNIQUE')
ORDER BY tc.TABLE_SCHEMA, tc.TABLE_NAME, tc.CONSTRAINT_NAME, kcu.ORDINAL_POSITION;

-- 4) foreign-keys.csv
SELECT OBJECT_SCHEMA_NAME(fk.parent_object_id) AS child_schema, OBJECT_NAME(fk.parent_object_id) AS child_table,
       COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS child_column,
       OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS parent_schema, OBJECT_NAME(fk.referenced_object_id) AS parent_table,
       COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS parent_column,
       fk.name AS fk_name, fk.is_disabled, fk.is_not_trusted
FROM sys.foreign_keys AS fk
JOIN sys.foreign_key_columns AS fkc ON fkc.constraint_object_id = fk.object_id
ORDER BY child_schema, child_table, fk.name;

-- 5) rowcounts.csv : rows and size per table
SELECT s.name AS schema_name, t.name AS table_name,
       SUM(CASE WHEN p.index_id IN (0,1) THEN p.rows ELSE 0 END) AS row_count,
       CAST(SUM(a.total_pages) * 8 / 1024.0 AS DECIMAL(18,1)) AS total_mb
FROM sys.tables AS t
JOIN sys.schemas AS s ON s.schema_id = t.schema_id
JOIN sys.partitions AS p ON p.object_id = t.object_id
JOIN sys.allocation_units AS a ON a.container_id = p.partition_id
GROUP BY s.name, t.name
ORDER BY row_count DESC;

-- 6) dependencies.csv : what each module references (incl. cross-database)
SELECT OBJECT_SCHEMA_NAME(d.referencing_id) AS referencing_schema, OBJECT_NAME(d.referencing_id) AS referencing_object,
       o.type_desc AS referencing_type,
       d.referenced_server_name, d.referenced_database_name, d.referenced_schema_name, d.referenced_entity_name,
       d.is_ambiguous, d.is_caller_dependent
FROM sys.sql_expression_dependencies AS d
JOIN sys.objects AS o ON o.object_id = d.referencing_id
ORDER BY referencing_schema, referencing_object, d.referenced_entity_name;

-- 7) code : one row per module. Write each definition to code/<schema>.<object>.<type>.sql
--    NULL definition = encrypted or no permission: list as an open question.
SELECT OBJECT_SCHEMA_NAME(m.object_id) AS schema_name, OBJECT_NAME(m.object_id) AS object_name,
       o.type_desc, m.uses_ansi_nulls, m.uses_quoted_identifier, m.definition
FROM sys.sql_modules AS m
JOIN sys.objects AS o ON o.object_id = m.object_id
WHERE o.is_ms_shipped = 0;

-- 8) synonyms.csv
SELECT s.name AS schema_name, sn.name AS synonym_name, sn.base_object_name
FROM sys.synonyms AS sn JOIN sys.schemas AS s ON s.schema_id = sn.schema_id;

-- 9) triggers.csv
SELECT OBJECT_SCHEMA_NAME(tr.parent_id) AS table_schema, OBJECT_NAME(tr.parent_id) AS table_name,
       tr.name AS trigger_name, tr.is_disabled, tr.is_instead_of_trigger
FROM sys.triggers AS tr WHERE tr.parent_class = 1;

-- 10) usage.csv : last access per table since last restart (weak evidence, resets)
SELECT OBJECT_SCHEMA_NAME(u.object_id) AS schema_name, OBJECT_NAME(u.object_id) AS object_name,
       MAX(u.last_user_seek) AS last_seek, MAX(u.last_user_scan) AS last_scan,
       MAX(u.last_user_lookup) AS last_lookup, MAX(u.last_user_update) AS last_update,
       SUM(u.user_seeks + u.user_scans + u.user_lookups) AS reads, SUM(u.user_updates) AS writes
FROM sys.dm_db_index_usage_stats AS u
WHERE u.database_id = DB_ID()
GROUP BY u.object_id;

-- 11) proc-stats.csv : procedure executions in plan cache (weak evidence, evicts)
SELECT OBJECT_SCHEMA_NAME(ps.object_id, ps.database_id) AS schema_name,
       OBJECT_NAME(ps.object_id, ps.database_id) AS proc_name,
       ps.execution_count, ps.last_execution_time, ps.cached_time,
       ps.total_elapsed_time / 1000 AS total_elapsed_ms, ps.max_elapsed_time / 1000 AS max_elapsed_ms
FROM sys.dm_exec_procedure_stats AS ps
WHERE ps.database_id = DB_ID()
ORDER BY ps.execution_count DESC;

-- 12) jobs.csv : SQL Agent jobs and steps (msdb; SQL Server and Managed Instance only)
SELECT j.name AS job_name, j.enabled, js.step_id, js.step_name, js.subsystem,
       js.database_name, js.command, js.on_success_action, js.on_fail_action
FROM msdb.dbo.sysjobs AS j
JOIN msdb.dbo.sysjobsteps AS js ON js.job_id = j.job_id
ORDER BY j.name, js.step_id;

-- 13) job-schedules.csv
SELECT j.name AS job_name, sc.name AS schedule_name, sc.enabled, sc.freq_type, sc.freq_interval,
       sc.freq_subday_type, sc.freq_subday_interval, sc.active_start_time
FROM msdb.dbo.sysjobs AS j
JOIN msdb.dbo.sysjobschedules AS jsch ON jsch.job_id = j.job_id
JOIN msdb.dbo.sysschedules AS sc ON sc.schedule_id = jsch.schedule_id;

-- 14) job-history.csv : last 30 days of outcomes
SELECT j.name AS job_name, h.step_id, h.run_status, msdb.dbo.agent_datetime(h.run_date, h.run_time) AS run_at,
       h.run_duration
FROM msdb.dbo.sysjobhistory AS h
JOIN msdb.dbo.sysjobs AS j ON j.job_id = h.job_id
WHERE msdb.dbo.agent_datetime(h.run_date, h.run_time) >= DATEADD(day, -30, GETDATE());

-- 15) cdc.csv : change data capture and change tracking
SELECT DB_NAME() AS database_name,
       (SELECT is_cdc_enabled FROM sys.databases WHERE database_id = DB_ID()) AS db_cdc_enabled,
       s.name AS schema_name, t.name AS table_name, t.is_tracked_by_cdc,
       CASE WHEN ct.object_id IS NULL THEN 0 ELSE 1 END AS change_tracking_enabled
FROM sys.tables AS t
JOIN sys.schemas AS s ON s.schema_id = t.schema_id
LEFT JOIN sys.change_tracking_tables AS ct ON ct.object_id = t.object_id;

-- 16) linked-servers.csv
SELECT name, product, provider, data_source, is_linked FROM sys.servers WHERE is_linked = 1;
