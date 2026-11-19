---
doc_id: ENG-08
title: Observability and Runbook
persona: lead-data-engineer
status: draft
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
related: [DIR-04, ENG-01, ENG-03]
---

# {{project_name}}: Observability and Runbook

## 1. What we capture
| Signal | Source | Stored in | Retention |
|---|---|---|---|
| Pipeline run status and duration | | | |
| Row counts per load | | | |
| Test results | | | |
| Freshness per data product | | | |
| Capacity / credit usage | | | |
| Cost per pipeline | | | |
| Lineage | | | |

## 2. Alerts
| Alert | Condition | Severity | Channel | Who responds | Runbook |
|---|---|---|---|---|---|

## 3. Dashboards
<!-- Platform health, DQ scorecard, cost. Who looks at them and when. -->

## 4. On-call
<!-- Hours, rotation, escalation path, consumer comms template. -->

## 5. Runbook
Each entry: symptom, likely causes, diagnose, fix, verify, communicate.

### RB-01: Source unavailable
- **Symptom**:
- **Diagnose**:
- **Fix**:
- **Verify**:
- **Communicate**:

### RB-02: Error-severity test failed, publish blocked
### RB-03: Schema change at source
### RB-04: Pipeline ran twice / duplicate data
### RB-05: Late-arriving data needs reprocessing
### RB-06: Capacity throttling / warehouse queueing
### RB-07: Expired credential or secret
### RB-08: Backfill a date range

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
