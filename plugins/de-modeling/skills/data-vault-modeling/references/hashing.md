# Hashing standard

Decide once, document here, implement once (package config or one macro).

| Rule | Recommended default | Why |
|---|---|---|
| Algorithm | MD5 for keys on most platforms, SHA-256 when policy requires; same everywhere | Consistency beats strength for keys; collisions on MD5 at warehouse scale are vanishingly rare but policy may differ |
| Output type | Binary where the platform supports it well, otherwise uppercase hex string; one choice everywhere | Joins between binary and string hashes silently fail |
| Input casting | Cast every part to string first | Different types hash differently |
| Trim | Trim leading and trailing spaces | `'ABC '` and `'ABC'` are the same customer |
| Case | Upper-case business keys (not descriptive attributes in hashdiffs unless agreed) | Case differences across sources |
| Null token | Replace null with a fixed token, e.g. `'^^'` | Null concatenation returns null on many platforms |
| Delimiter | A character not found in keys, e.g. `'||'` | `A+BC` vs `AB+C` must not collide |
| Composite keys | Order of columns fixed and documented | Order changes the hash |
| Hashdiff | Same rules over the descriptive columns in a fixed order | Detects real changes only |

Example (T-SQL style), key of `customer_id` and `company_code`:

```sql
CONVERT(char(32), HASHBYTES('MD5',
  CONCAT(
    UPPER(TRIM(COALESCE(CAST(customer_id AS nvarchar(100)), '^^'))), '||',
    UPPER(TRIM(COALESCE(CAST(company_code AS nvarchar(100)), '^^')))
  )), 2) AS hk_customer
```

Snowflake: `UPPER(MD5(...))` over the same concatenation. Spark:
`upper(md5(concat_ws('||', ...)))` (note `concat_ws` skips nulls, so coalesce first).
Prove equivalence across platforms with a test row set if more than one engine
computes hashes.
