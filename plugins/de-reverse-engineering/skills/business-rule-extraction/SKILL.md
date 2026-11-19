---
name: business-rule-extraction
description: >-
  Use when you need the business logic hidden inside existing SQL, stored
  procedures, views, ETL transforms, dbt models or report measures written down
  as rules a business person can confirm: filters, CASE logic, hard-coded IDs
  and dates, exclusions, allocations, currency and unit conversions,
  deduplication and late-data rules. Produces a rules catalog with evidence,
  confidence and an owner to confirm each rule.
---

# Business Rule Extraction

Turn code into a list of decisions the business can confirm, correct or retire.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Before a migration: the new system must reproduce or deliberately change each rule.
- "Why is revenue different in the new report?"
- Step 6 of `reverse-engineer-data-system`.

Not for: designing new rules (that is a modeling or metric decision; use
`dimensional-modeling` or `data-contracts`).

## Inspect first

1. The code that produces the numbers people care about: trace back from the
   report or mart using `lineage/traces.md`.
2. Proc specs (`procs/*.md`) already list rule candidates as `BR-<proc>-##`.
3. Report-level logic too: Power BI measures (DAX), SSRS dataset queries,
   Excel calculations. Rules often live in the last mile.

## Procedure

1. **Harvest candidates.** Search the in-scope code for:
   - `WHERE`, `HAVING` and join conditions with literals: `status <> 'X'`, `type IN (3, 7)`
   - `CASE` expressions that assign categories, flags or amounts
   - hard-coded IDs, codes, dates, thresholds, percentages
   - `ISNULL`/`COALESCE` defaults that change meaning (`ISNULL(discount, 0.1)`)
   - dedupe logic (`ROW_NUMBER() ... = 1` and its `ORDER BY`)
   - date logic: fiscal calendars, cutoffs, "as of" rules, time zones
   - conversions: currency, units, sign flips for credits and returns
   - exclusions: test accounts, internal customers, cancelled orders
2. **Write each rule** in [assets/rules-catalog-template.md](assets/rules-catalog-template.md)
   format: plain-language statement, the exact code, file and lines, where it
   applies (which outputs), confidence, and who can confirm.
3. **Group duplicates.** The same rule implemented twice, differently, is the
   most valuable finding: list both versions and the outputs that differ.
4. **Test rules against data** where possible: e.g. "excludes internal
   customers" means zero internal customers in the output. Write the query and
   the result.
5. **Send for confirmation.** Each rule gets an owner (finance, sales ops) and a
   status: confirmed, corrected, retire, unknown.

## Standards

- **MUST** write the rule in business words first, code second.
  "Orders cancelled within 24 hours are not counted as sales" not `DATEDIFF(hh,...) > 24`.
- **MUST** cite file and lines for every rule.
- **MUST** set confidence: high (one clear implementation, data agrees), medium
  (clear code, untested), low (inferred, dynamic, or contradicted by data).
- **SHOULD** flag magic numbers with no explanation as open questions, never guess
  their meaning.
- **SHOULD** note the rule's blast radius: which reports and data products depend on it.

## Failure modes

| Failure | Prevention |
|---|---|
| Rule paraphrased wrong, so the rebuild is wrong | Exact code stored next to the plain words |
| A rule implemented twice, differently, missed | Explicit duplicate-grouping step |
| Meaning invented for a magic number | Unknown meaning becomes an open question |
| Rules found only in SQL, report logic missed | Inspect DAX, SSRS and Excel too |
| Catalog never confirmed, so it stays a guess | Owner and status per rule |

## Verify

- Each high-confidence rule has a test query and its result.
- Rebuild one key number using only the catalog's rules (on paper or in SQL) and
  compare to the legacy output. A gap means a missing rule.

## Output

`docs/reverse-engineering/rules/rules-catalog.md`, plus `rules/tests/*.sql` for
rule tests.
