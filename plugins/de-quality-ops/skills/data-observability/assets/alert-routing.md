# Alert routing

| Severity | Meaning | Channel | Response target | Example |
|---|---|---|---|---|
| P1 | A published number is wrong, or an executive SLA is missed | Page on-call + team channel | 30 minutes in business hours | Revenue mart stale at 6:30am |
| P2 | A data product is degraded or late, workaround exists | Team channel | Same business day | Inventory snapshot 2 hours late |
| P3 | Anomaly or warning to review | Daily digest | Weekly review | Null rate on optional column rose |

## Alert content (every alert)

- Data product and check that failed
- Owner (person or rotation)
- Impact: who is affected and what they will see
- Since when, and last good run
- Link to logs and to the runbook entry

## Monitors

| Data product | Monitor | Threshold | Severity | Owner | Runbook |
|---|---|---|---|---|---|
