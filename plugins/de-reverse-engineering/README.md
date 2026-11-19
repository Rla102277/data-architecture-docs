# de-reverse-engineering (plugin)

Reverse engineer legacy data systems without running them: SQL Server, Snowflake and Fabric catalog inventory, stored procedure specs, SSIS and ADF/Fabric pipeline analysis, sqlglot table lineage, business rules catalog, profiling, and legacy-to-dbt migration with parity testing.

Install in Claude Code:

```
/plugin install de-reverse-engineering --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [business-rule-extraction](skills/business-rule-extraction/SKILL.md) | you need the business logic hidden inside existing SQL, stored procedures, views, ETL transforms, dbt models or report measures written down as rules a business person can confirm: filters, CASE logic, hard-coded IDs and dates, exclusions, allocations, currency and unit conversions, deduplication and late-data rules |
| [data-profiling](skills/data-profiling/SKILL.md) | you need to know what is actually in a table before trusting, modeling or migrating it: row counts, nulls, distinct values, ranges, lengths, top values, candidate keys and duplicate checks, and hints of PII |
| [etl-package-analysis](skills/etl-package-analysis/SKILL.md) | you must understand existing ETL packages or pipelines without running them: SSIS .dtsx packages, Azure Data Factory, Synapse or Microsoft Fabric Data Factory pipeline JSON |
| [legacy-to-dbt-migration](skills/legacy-to-dbt-migration/SKILL.md) | moving legacy SQL logic (stored procedures, views, SSIS or ADF transforms, SQL Agent jobs) into dbt on Fabric, Snowflake, SQL Server or a lakehouse |
| [lineage-extraction](skills/lineage-extraction/SKILL.md) | you need to know what feeds what: table-level lineage from SQL files, stored procedures, views, dbt models or SQL pulled out of SSIS and ADF/Fabric pipelines, including procedure-to-procedure EXEC calls and temp tables |
| [reverse-engineer-data-system](skills/reverse-engineer-data-system/SKILL.md) | you inherit or must replace a data system nobody fully understands: a legacy SQL Server warehouse, stored procedures, SSIS packages, ADF or Fabric pipelines, a Snowflake account, an undocumented dbt project |
| [sql-object-inventory](skills/sql-object-inventory/SKILL.md) | you need a complete catalog of a database before changing, migrating or documenting it: tables, views, stored procedures, functions, triggers, synonyms, columns, keys, row counts, dependencies, SQL Agent jobs, schedules, CDC and change tracking, linked servers, and usage signals |
| [stored-procedure-analysis](skills/stored-procedure-analysis/SKILL.md) | you must understand, document or rewrite a stored procedure: T-SQL (SQL Server, Azure SQL, Fabric Warehouse) or Snowflake procedures |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
