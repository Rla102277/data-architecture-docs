---
name: sql-refactoring
description: >-
  Use when legacy or messy SQL must be made readable, set-based and
  maintainable without changing its results: nested subqueries, cursors and
  WHILE loops, scalar UDFs, copy-pasted logic, temp table chains, giant
  procedures. Refactors in small steps into CTEs, window functions and
  set-based logic, proving identical output with parity queries after each step.
---

# SQL Refactoring

Change the shape, never the answer, and prove it after every step.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "Clean up this 800-line proc before we migrate it."
- "Replace this cursor."
- Preparing legacy SQL for `legacy-to-dbt-migration`.

Not for: changing business logic (that is a rule change; get owner approval and
treat it as a feature), or tuning (use `sql-performance-tuning`).

## Inspect first

1. The current code and its spec (`stored-procedure-analysis` output if it exists).
2. A reproducible test input: a copy of the inputs at a fixed point in time, or
   a non-production database. Refactoring without a frozen input cannot be proven.
3. The current output for that input, saved as the golden result.

## Procedure

1. **Freeze** inputs and capture the golden output (table or CSV) with a row count
   and per-column checksums.
2. **Refactor in small, separate steps**, re-running parity after each:
   - Extract nested subqueries into named CTEs.
   - Replace cursors and `WHILE` loops with set-based statements
     ([references/patterns.md](references/patterns.md)).
   - Replace correlated subqueries with joins or window functions.
   - Replace scalar UDFs called per row with inline expressions or joins.
   - Collapse temp table chains whose only purpose is ordering steps into CTEs,
     but keep a temp table when it is reused or materially speeds things up.
   - Remove dead code: branches that cannot run, columns never used downstream
     (check consumers first).
   - Deduplicate copy-pasted logic into one CTE or view.
3. **Compare** with the golden output after each step (see `sql-testing`). Any
   difference stops the work until explained.
4. **Commit per step** with a message saying what changed and that parity held.

## Standards

- **MUST** keep results identical, including row order only when the consumer
  depends on order (and then make the `ORDER BY` explicit).
- **MUST** run parity after every step, not only at the end.
- **MUST** preserve null semantics. `NOT IN` to `NOT EXISTS`, `ISNULL` vs
  `COALESCE` type precedence and `CONCAT` vs `+` with nulls can all change results.
- **SHOULD** preserve column names and types of outputs unless consumers are changed too.
- **SHOULD** keep each step small enough to review in five minutes.

## Failure modes

| Failure | Prevention |
|---|---|
| Cursor replacement changes results for ties or ordering | Window `ORDER BY` with a unique tiebreaker; parity proves it |
| `ISNULL` to `COALESCE` changes data type and truncation | Type check in parity (compare types, not only values) |
| Silent behavior change from a "harmless" cleanup | Parity after every step |
| Big-bang rewrite nobody can review | One pattern per commit |
| Refactoring code that is dead anyway | Check callers and usage first |

## Verify

Parity query result for each step: zero rows missing, zero extra, zero
mismatched values per column, and identical column types.

## Output

The refactored SQL, a step log (step, change, parity result), and the golden
output kept for the next change.
