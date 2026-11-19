# de-sql (plugin)

SQL craft for data engineers on T-SQL, Snowflake and Spark SQL: style and review, performance tuning with plans, refactoring legacy SQL to set-based and CTE form with parity, and testing SQL.

Install in Claude Code:

```
/plugin install de-sql --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [sql-performance-tuning](skills/sql-performance-tuning/SKILL.md) | a query, view, procedure, dbt model or report is slow or expensive on SQL Server, Azure SQL, Fabric Warehouse, Snowflake or Spark |
| [sql-refactoring](skills/sql-refactoring/SKILL.md) | legacy or messy SQL must be made readable, set-based and maintainable without changing its results: nested subqueries, cursors and WHILE loops, scalar UDFs, copy-pasted logic, temp table chains, giant procedures |
| [sql-style-and-review](skills/sql-style-and-review/SKILL.md) | writing new analytical SQL or reviewing a SQL change, query, view, stored procedure or dbt model before it merges: T-SQL, Snowflake or Spark SQL |
| [sql-testing](skills/sql-testing/SKILL.md) | SQL logic needs proof: unit-style tests on fixed inputs, assertion queries that must return zero rows, parity checks between an old and new query or table, golden datasets, and regression checks for views, stored procedures and dbt models on SQL Server, Fabric, Snowflake or Spark |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
