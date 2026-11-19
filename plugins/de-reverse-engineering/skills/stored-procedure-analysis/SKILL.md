---
name: stored-procedure-analysis
description: >-
  Use when you must understand, document or rewrite a stored procedure:
  T-SQL (SQL Server, Azure SQL, Fabric Warehouse) or Snowflake procedures.
  Produces a spec per procedure: purpose, parameters, inputs, outputs, side
  effects, control flow, temp tables, business rules, error handling,
  transaction behavior, dynamic SQL and risks, with line references.
---

# Stored Procedure Analysis

Read a procedure the way a reviewer reads a contract: what it promises, what it
actually does, and where those differ.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "What does `usp_LoadSales` do?" "Can we retire this proc?"
- Before rewriting a proc in dbt, Spark or a new procedure.
- Step 5 of `reverse-engineer-data-system`, for the procedures that matter.

Not for: performance tuning of a known proc (use `sql-performance-tuning`).

## Inspect first

1. The exact code with line numbers (`code/<schema>.<proc>.PROCEDURE.sql`).
2. Who calls it: `lineage/calls.csv`, `inventory/jobs.csv`, `etl/` summaries,
   and a code search for its name (apps and reports call procs too).
3. How often and how long it runs: `inventory/proc-stats.csv`.
4. The tables it touches: `lineage/edges.csv` rows for this file.

## Procedure

Fill [assets/proc-spec-template.md](assets/proc-spec-template.md) for each proc.

1. **Signature.** Parameters, types, defaults, OUTPUT parameters, return codes.
2. **Control flow.** Read top to bottom and write the steps as a numbered list
   in plain words, with line ranges. Note each branch (`IF`, `WHILE`, `GOTO`).
3. **Data in and out.** Tables read, tables written (INSERT, UPDATE, DELETE,
   MERGE, TRUNCATE), temp tables and table variables, result sets returned.
4. **Side effects.** Calls to other procs, linked servers, `xp_cmdshell`,
   `sp_send_dbmail`, file writes, Agent jobs started.
5. **Business rules.** Every filter, CASE, hard-coded value and join condition
   that encodes a decision. Number them `BR-<proc>-##` and hand them to
   `business-rule-extraction`.
6. **Transactions and errors.** `BEGIN TRAN` and where it commits; `XACT_ABORT`;
   `TRY/CATCH` blocks and whether they re-throw; what state is left on failure.
7. **Idempotency.** Can it be run twice for the same input safely? Why or why not.
8. **Risks.** Dynamic SQL (and what builds it), `NOLOCK`, cursors, `SELECT *`,
   implicit conversions, `GETDATE()` in logic, missing `SET NOCOUNT ON`,
   swallowed errors.
9. **Diagram** (optional, for long procs): a Mermaid flowchart of steps and branches.

## Standards

- **MUST** cite line numbers for every step, rule and risk.
- **MUST** separate what the code does from what its comments or name claim.
  Stale comments are common; the code wins, the mismatch is a finding.
- **MUST** say "unknown" for dynamic SQL whose text depends on run-time values,
  and list the variables that build it.
- **SHOULD** describe each step at the level a business analyst could confirm:
  "Removes refunded orders from the fact table" not "DELETE with JOIN".
- **SHOULD** check for a sibling proc with a similar name (`_v2`, `_old`, `_new`):
  find which one is actually called.

## Failure modes

| Failure | Prevention |
|---|---|
| Spec written from the proc name or comments | Code-first reading with line refs |
| Missing a write hidden in a called proc | Side effects step follows every EXEC one level |
| "Safe to rerun" claimed without checking | Explicit idempotency step |
| Error handling that hides failures missed | TRY/CATCH re-throw check is mandatory |
| Rewriting a proc nobody calls | Callers checked first |

## Verify

- Every table in the spec's Data in/out matches `lineage/edges.csv` for this file.
- If a non-production copy exists and the user approves, run the proc on a
  known input and compare the outputs the spec predicts. Never in production.

## Output

`docs/reverse-engineering/procs/<schema>.<proc>.md` per procedure, and the
rules handed to `rules/rules-catalog.md`.
