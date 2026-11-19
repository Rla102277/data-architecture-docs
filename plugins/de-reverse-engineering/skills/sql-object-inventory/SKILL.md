---
name: sql-object-inventory
description: >-
  Use when you need a complete catalog of a database before changing,
  migrating or documenting it: tables, views, stored procedures, functions,
  triggers, synonyms, columns, keys, row counts, dependencies, SQL Agent jobs,
  schedules, CDC and change tracking, linked servers, and usage signals. Read-only
  catalog queries for SQL Server, Azure SQL, Snowflake and Microsoft Fabric
  Warehouse, with results saved as CSV evidence.
---

# SQL Object Inventory

Catalog everything in a database with read-only queries and save the results as
evidence.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- First step of any reverse engineering, migration sizing or cleanup.
- "How many procs do we have, which ones run, and what do they touch?"

Not for: understanding what one procedure does (use `stored-procedure-analysis`).

## Inspect first

1. Which platform and edition? The query file differs: SQL Server / Azure SQL,
   Snowflake, or Fabric Warehouse / SQL analytics endpoint.
2. Permissions: SQL Server needs `VIEW DEFINITION` and `VIEW SERVER STATE` for
   code and usage DMVs, plus `msdb` read for jobs. Snowflake needs access to
   `SNOWFLAKE.ACCOUNT_USAGE` for dependencies and history. If missing, run what
   you can and list the gaps as open questions.
3. One database at a time. Note server, database and time for every run.

## Procedure

1. Open the query file for the platform:
   - SQL Server / Azure SQL: [assets/sqlserver-inventory.sql](assets/sqlserver-inventory.sql)
   - Snowflake: [assets/snowflake-inventory.sql](assets/snowflake-inventory.sql)
   - Fabric Warehouse / SQL endpoint / Lakehouse: [assets/fabric-inventory.sql](assets/fabric-inventory.sql)
2. Run each numbered query. Save each result as CSV in
   `docs/reverse-engineering/inventory/` using the file name in the query header
   (`objects.csv`, `columns.csv`, `keys.csv`, `dependencies.csv`, `rowcounts.csv`,
   `jobs.csv`, `usage.csv`, `proc-stats.csv`, `cdc.csv`, `linked-servers.csv`).
3. Export code: run the code-extraction query and write one file per object to
   `docs/reverse-engineering/code/<schema>.<object>.<type>.sql`. Keep the exact
   text; do not reformat it (line numbers become evidence).
4. Write `inventory/README.md`: platform, server, database, time, who ran it,
   which queries failed and why, and the counts by object type.
5. Flag landmines with a grep over `code/` (see Standards) and add a
   `landmines.csv` (object, pattern, line).
6. Rank objects for triage: dependents count, row count, last execution or
   access, referenced by jobs. Write `inventory/triage.csv`.

## Standards

- **MUST** run only catalog and `SELECT` queries. No `EXEC` of user procedures.
- **MUST** save the query text with each result (a header comment in the CSV
  folder README is enough) so anyone can re-run it.
- **MUST** grep extracted code for these landmines and record them:
  `EXEC(`, `sp_executesql` (dynamic SQL), four-part names or `OPENQUERY`
  (linked servers), `NOLOCK`, `CURSOR`, `TRUNCATE`, `DROP`, `CREATE TRIGGER`,
  `@@ROWCOUNT` checks with silent `RETURN`, `BEGIN CATCH` without `THROW` or
  `RAISERROR`, hard-coded dates (`'20` followed by digits), `GETDATE()` in filters.
- **SHOULD** treat usage DMVs as weak evidence. `sys.dm_db_index_usage_stats` and
  `sys.dm_exec_procedure_stats` reset on restart and plan eviction. Record the
  server start time (`sys.dm_os_sys_info.sqlserver_start_time`) next to them.
- **SHOULD** prefer `ACCOUNT_USAGE` over `INFORMATION_SCHEMA` in Snowflake for
  history and dependencies, and note its latency (up to a few hours).

## Failure modes

| Failure | Prevention |
|---|---|
| Missing cross-database references | `dependencies.csv` keeps `referenced_database_name`; inventory every referenced database too |
| Object "unused" after a recent restart | Server start time recorded next to usage evidence |
| Code reformatted on export, line refs lost | Export exact `definition` text |
| Encrypted procs (`WITH ENCRYPTION`) silently skipped | Code query returns NULL definition; list them as open questions |
| Permissions errors swallowed | README lists every query that failed |

## Verify

- Object counts by type in the README match `SELECT type_desc, COUNT(*) FROM sys.objects WHERE is_ms_shipped = 0 GROUP BY type_desc` (or the platform equivalent).
- Every procedure and view in `objects.csv` has a file in `code/` or is listed as encrypted / no access.
- Spot-check three row counts against `SELECT COUNT(*)`.

## Output

`docs/reverse-engineering/inventory/*.csv`, `inventory/README.md`,
`inventory/triage.csv`, `inventory/landmines.csv`, and `code/*.sql`.
