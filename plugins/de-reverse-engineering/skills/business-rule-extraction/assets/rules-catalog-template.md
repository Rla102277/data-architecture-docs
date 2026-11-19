# Business rules catalog

| Status key | Meaning |
|---|---|
| unconfirmed | Extracted from code, not yet confirmed by an owner |
| confirmed | Owner agrees the rule is right and current |
| corrected | Owner says the rule should be different (see Correction) |
| retire | Owner says the rule should not carry forward |

## Summary

| ID | Rule (plain words) | Applies to | Confidence | Owner | Status |
|---|---|---|---|---|---|

---

## BR-001: <short name>

- **Rule:** <plain business statement>
- **Code:**
  ```sql
  <exact code>
  ```
- **Where:** `<file>` lines a-b (also implemented in: ...)
- **Applies to:** <tables, data products, reports>
- **Confidence:** high / medium / low, because ...
- **Test:** `rules/tests/BR-001.sql` -> <result and date>
- **Owner to confirm:** <role or name>
- **Status:** unconfirmed
- **Correction / notes:**
