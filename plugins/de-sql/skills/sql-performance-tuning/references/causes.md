# Common causes and fixes

| Symptom in plan or profile | Likely cause | Fix to try first |
|---|---|---|
| Scan on a big table where few rows survive | Non-sargable predicate (`WHERE YEAR(d)=2026`, `ISNULL(col,'')='x'`, leading `%LIKE`) | Rewrite as a range or plain comparison |
| Implicit conversion warning (SQL Server), `CONVERT_IMPLICIT` | Comparing `varchar` to `nvarchar`, string to number or date | Match types; cast the literal or parameter, not the column |
| Estimated rows far from actual | Stale or missing statistics; skewed values | `UPDATE STATISTICS` (or create stats); filtered stats for skew |
| Plan fine for one parameter, terrible for another | Parameter sniffing | `OPTION (RECOMPILE)` on that statement, or `OPTIMIZE FOR`, or split the logic by case |
| Key lookup repeated millions of times | Index missing included columns | Covering index (add `INCLUDE` columns) |
| Sort or hash spills to tempdb / disk / remote storage | Memory grant too small, or far too many rows reach the operator | Filter or aggregate earlier; then more memory or a bigger warehouse |
| Snowflake `partitions_scanned` close to `partitions_total` | No pruning on the filter column | Filter on a well-clustered column; consider a clustering key on large, filtered tables |
| Spark: one task runs 10x longer than the rest | Skewed join key | Salt the key, AQE skew join, or broadcast the small side |
| Spark: thousands of tiny files | Small-file problem from frequent appends | `OPTIMIZE` (Delta), coalesce on write, target file size |
| Join output much larger than both inputs | Many-to-many fan-out | Fix the join keys or pre-aggregate one side |
| Row-by-row: cursor, `WHILE` loop, scalar UDF per row | Procedural logic | Set-based rewrite (see sql-refactoring) |
| Long queue time, short execution | Concurrency limit | Snowflake multi-cluster or separate warehouse; Fabric capacity smoothing review; schedule spreading |
| Same expensive query repeated by many reports | No reuse | Materialize an aggregate table or use the BI layer's aggregation |
