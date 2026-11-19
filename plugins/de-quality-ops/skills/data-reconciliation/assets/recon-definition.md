# Reconciliation: <name>

| Field | Value |
|---|---|
| Measure | e.g. net revenue |
| System of record | e.g. ERP general ledger |
| Grain | period x legal entity x GL account |
| Tolerance | absolute: $ ; percent: % |
| Severity | block publish / flag |
| Owner | e.g. Controller |
| Runs | after every load / daily / at close |

## Source query (system of record)

```sql
-- period, entity, account, amount
```

## Target query (platform)

```sql
-- same grain, same period definition, same currency and sign
```

## Known differences

| Type | Description | Reference | Expected amount |
|---|---|---|---|
| Timing | | | |
| Adjustment | | | |

## Sign-off

| Period | Result | Unexplained difference | Signed by | Date |
|---|---|---|---|---|
