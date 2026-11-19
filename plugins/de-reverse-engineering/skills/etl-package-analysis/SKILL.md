---
name: etl-package-analysis
description: >-
  Use when you must understand existing ETL packages or pipelines without
  running them: SSIS .dtsx packages, Azure Data Factory, Synapse or Microsoft
  Fabric Data Factory pipeline JSON. Extracts connections, steps, dependencies,
  data flow sources and destinations, every SQL statement and stored procedure
  call, and flags SQL built at run time, writing one summary per package.
---

# ETL Package Analysis

Read SSIS packages and ADF / Fabric pipelines as files and turn each into a
plain summary plus extracted SQL.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "We have 150 SSIS packages and nobody knows the order they run in."
- "What does this Fabric pipeline actually execute?"
- Step 3 of `reverse-engineer-data-system`.

Not for: debugging a failing run (use `pipeline-incident-response`).

## Inspect first

1. Get the files, not the running service:
   - SSIS: the `.dtsx` files from the project folder or SSISDB export
     (`.ispac` is a zip; unzip it). Note the deployment model (project or package).
   - ADF / Synapse: the Git-integrated repo (`pipeline/`, `dataset/`,
     `linkedService/`, `trigger/` folders) or an ARM export.
   - Fabric: workspace Git integration (each pipeline item has a
     `pipeline-content.json`) or the REST "Get Item Definition" output.
2. Get the schedules: SQL Agent job steps that call `dtexec` or the SSIS catalog
   (`inventory/jobs.csv`), ADF/Fabric triggers and schedules.
3. Never run a package or pipeline to learn what it does.

## Procedure

1. Run the analyzer:
   ```bash
   python3 <skill-dir>/scripts/analyze_etl_package.py <folder-of-dtsx-and-json> \
     --out docs/reverse-engineering/etl
   ```
   Writes `<package>.md` (connections with passwords masked, steps, dependencies,
   data movement, SQL found, dynamic items), `sql/<package>__<n>.sql` and
   `summary.csv`. Stored procedure activities are written as `EXEC <proc>`.
2. Feed the SQL to lineage:
   ```bash
   python3 <lineage-skill-dir>/scripts/extract_lineage.py docs/reverse-engineering/etl/sql \
     --dialect tsql --out docs/reverse-engineering/lineage
   ```
   (Run it together with the database code folder so edges join up.)
3. For each package, read the **Dynamic** section. Variables built by
   expression, parameters and `@concat(...)` SQL are not in the file. Find their
   values: SSIS environment and parameter values in SSISDB
   (`catalog.object_parameters`, `catalog.environment_variables`), ADF/Fabric
   pipeline parameters, triggers, and global parameters. Record what you find.
4. Build the run order: `schedule-and-order.md` with each trigger or job, the
   packages it runs in order, and dependencies between them.
5. Note the transforms that hold business logic (SSIS Derived Column,
   Conditional Split, Lookup with no-match handling, Script Tasks; ADF Data
   Flows) and hand them to `business-rule-extraction`.

## Standards

- **MUST** mask credentials in every output. The analyzer masks `Password=` and
  `PWD=`; check for others (keys, SAS tokens) before committing.
- **MUST** list Script Tasks and Script Components separately. Their C# or VB
  code lives in the package; extract and read it, it is often where the real rules are.
- **SHOULD** treat SSIS Lookup "ignore failure" and "redirect rows" settings as
  business rules: they decide what happens to rows that do not match.
- **SHOULD** record each package's error handling: OnError event handlers,
  `FailPackageOnFailure`, ADF `dependencyConditions` of Failed or Skipped.

## Failure modes

| Failure | Prevention |
|---|---|
| Connection strings with passwords committed to Git | Masking plus a manual check |
| SQL built from variables taken as missing | Listed under Dynamic, resolved from SSISDB or parameters |
| Run order guessed from names | Built from precedence constraints, dependsOn, triggers and jobs |
| Logic in Script Tasks ignored | Script code extracted and read |
| Nested pipeline calls lost | ExecutePipeline / InvokePipeline recorded as `calls` dependencies |

## Verify

- Every package in `summary.csv` has a run trigger in `schedule-and-order.md`
  or is marked "no trigger found" (candidate for retirement).
- Spot-check one package: open the `.dtsx` or JSON and confirm the step count
  and the first SQL statement match the summary.

## Output

`docs/reverse-engineering/etl/`: one `<package>.md` each, `sql/`, `summary.csv`,
`schedule-and-order.md`.
