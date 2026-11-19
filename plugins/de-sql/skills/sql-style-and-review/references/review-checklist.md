# SQL review checklist

Mark each item: OK, finding (blocker / should-fix / nit), or not applicable.

## Correctness
- [ ] Output grain stated, and the query produces exactly that grain
- [ ] Every join: which side is unique, proven by a key or a check
- [ ] No fan-out before an aggregate (join then SUM double counts)
- [ ] LEFT JOIN filters: conditions on the right table are in `ON`, not `WHERE` (or the join silently becomes INNER)
- [ ] `NOT IN` replaced by `NOT EXISTS` where the subquery can return NULL
- [ ] Null handling explicit: `COALESCE` defaults have a business reason
- [ ] Date ranges half-open; time zones explicit; no `BETWEEN` on timestamps
- [ ] Dedupe `ROW_NUMBER()` has a deterministic `ORDER BY` with a tiebreaker
- [ ] Division guarded against zero and integer division
- [ ] `DISTINCT` is not hiding a join bug
- [ ] `UNION` vs `UNION ALL` chosen on purpose
- [ ] Hard-coded values explained or moved to config / seeds

## Change safety
- [ ] Output columns, names and types unchanged, or consumers checked
- [ ] Incremental logic still correct on rerun (idempotent)
- [ ] Deletes, truncates and drops are intended and scoped

## Readability
- [ ] CTEs with one job each, named for what they hold
- [ ] Columns qualified; no `SELECT *` past staging
- [ ] Names follow project conventions
- [ ] Comments explain why, not what

## Security
- [ ] No credentials or secrets in code
- [ ] Dynamic SQL uses parameters (`sp_executesql` with params), never string-concatenated user input
- [ ] Sensitive columns not exposed to a wider audience than the source
- [ ] No `NOLOCK` on trusted numbers

## Performance (flag, then use sql-performance-tuning)
- [ ] Filters sargable (no functions on filtered columns)
- [ ] No row-by-row cursors or scalar UDFs in big queries
- [ ] Partition or cluster columns used in filters on big tables
