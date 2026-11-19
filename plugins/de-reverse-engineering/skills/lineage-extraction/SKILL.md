---
name: lineage-extraction
description: >-
  Use when you need to know what feeds what: table-level lineage from SQL
  files, stored procedures, views, dbt models or SQL pulled out of SSIS and
  ADF/Fabric pipelines, including procedure-to-procedure EXEC calls and temp
  tables. Runs a sqlglot-based extractor (T-SQL, Snowflake, Spark and more) and
  writes edges.csv, a Mermaid lineage diagram and a list of everything it could
  not parse.
---

# Lineage Extraction

Build table-level lineage from code, and be explicit about what the code could
not tell you.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "Where does `rpt.vSalesByCustomer` get its data?"
- "What breaks if we drop `stg.Orders`?"
- Step 4 of `reverse-engineer-data-system`.

Not for: dbt projects with a working `manifest.json` (read its `parent_map` and
`child_map` instead, it is exact), or runtime lineage from a catalog (Purview,
Unity Catalog, OpenLineage) when one already exists.

## Inspect first

1. Where is the code? Prefer files: `docs/reverse-engineering/code/` from
   `sql-object-inventory`, `etl/sql/` from `etl-package-analysis`, or a repo.
2. Which dialect? `tsql` for SQL Server, Azure SQL and Fabric Warehouse;
   `snowflake`; `spark` or `databricks` for lakehouse notebooks SQL.
3. Is `sqlglot` installed? `python3 -c "import sqlglot"`. If not:
   `pip install sqlglot` (in a virtual environment).

## Procedure

1. Run the extractor:
   ```bash
   python3 <skill-dir>/scripts/extract_lineage.py \
     docs/reverse-engineering/code docs/reverse-engineering/etl/sql \
     --dialect tsql --out docs/reverse-engineering/lineage
   ```
   It splits procedure bodies into statements (handling BEGIN/END, IF, TRY/CATCH,
   CASE...END, CTEs, MERGE, SELECT INTO, temp tables and UPDATE aliases) and writes:
   `edges.csv`, `calls.csv` (EXEC proc to proc), `objects.csv`, `lineage.md`,
   `unparsed.md`.
2. **Read `unparsed.md` first.** Every line is a hole in the lineage. Resolve the
   important ones by hand: dynamic SQL (`EXEC(@sql)`, `sp_executesql`), linked
   servers, synonyms (map them with `inventory/synonyms.csv`).
3. Add manual edges you confirmed to `lineage/manual-edges.csv` with the same
   columns plus `evidence`. Never mix them silently into `edges.csv`.
4. For each important report or target, write a trace in `lineage/traces.md`:
   target, then each hop back to a source system table, with the file and
   statement number for each hop.
5. Split the Mermaid diagram if it passes about 40 nodes: one diagram per
   subject area or per target, generated from `edges.csv`.

## Standards

- **MUST** keep `unparsed.md` and say how many statements were not analyzed.
  Lineage that hides its gaps is worse than none.
- **MUST** name temp tables with their file (`proc::#stage`) so flows through them
  stay visible and do not merge across procedures.
- **SHOULD** treat column-level lineage as a second pass, only for the columns
  a decision depends on. Table-level first.
- **SHOULD** cross-check edges against `inventory/dependencies.csv`
  (`sys.sql_expression_dependencies`). Edges in one and not the other are
  findings: dynamic SQL, deferred name resolution, or dead code.

## Failure modes

| Failure | Prevention |
|---|---|
| Dynamic SQL silently dropped | Files with `EXEC(` or `sp_executesql` are listed in `unparsed.md` |
| Proc body parsed as one opaque command | T-SQL splitter handles control flow; anything still opaque is listed |
| UPDATE alias recorded as a table (`f`) | Alias resolved to the FROM table |
| Two procs' `#stage` merged into one node | Temp tables prefixed with their file |
| Pipeline calls a proc but lineage stops | ETL SQL is written as `EXEC proc` so `calls.csv` links them |
| Synonyms point somewhere unexpected | Resolve with `synonyms.csv` before tracing |

## Verify

- Pick three targets and confirm one hop each by reading the cited statement.
- `objects.csv`: every table written but never read is either a final output
  (report, export) or dead. Every table read but never written is a source or
  is fed by something you have not inventoried yet (another database, a pipeline).
- Count of edges versus count of `sys.sql_expression_dependencies` rows: a large
  gap means missing code or heavy dynamic SQL.

## Output

`docs/reverse-engineering/lineage/`: `edges.csv`, `calls.csv`, `objects.csv`,
`lineage.md`, `unparsed.md`, `manual-edges.csv`, `traces.md`.
