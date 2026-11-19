# Data quality plan: <dataset>

| Field | Value |
|---|---|
| Dataset | |
| Grain | |
| Consumers and decision | |
| Freshness need | |
| Owner (data) | |
| Owner (pipeline) | |

| # | Failure mode | Check | Layer | Severity (block / warn) | On failure | Owner | Tool |
|---|---|---|---|---|---|---|---|
| 1 | Duplicate rows | unique on grain key | marts | block | stop publish | | dbt |
| 2 | Missing day of data | volume vs same weekday history | landing | block | stop, alert | | |
| 3 | Unknown product codes | accepted values / relationships | staging | warn | quarantine rows, alert | | |
| 4 | Stale data | freshness under 26h | marts | block | stop refresh, alert | | dbt source freshness |
