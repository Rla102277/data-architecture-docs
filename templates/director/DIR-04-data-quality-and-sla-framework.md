---
doc_id: DIR-04
title: Data Quality and SLA Framework
persona: data-director
status: draft
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
related: [ENG-05, ENG-08]
---

# {{project_name}}: Data Quality and SLA Framework

## Summary

## Quality dimensions
| Dimension | Definition | Example check | Default severity |
|---|---|---|---|
| Completeness | | | |
| Validity | | | |
| Uniqueness | | | |
| Consistency / referential integrity | | | |
| Timeliness | | | |
| Accuracy (reconciliation to source) | | | |

## Severity levels
| Level | Meaning | Pipeline behavior | Notify | Response target |
|---|---|---|---|---|
| Error / Sev 1 | Data is wrong or missing for a certified product | Block publish | | |
| Warn / Sev 2 | Degraded, still usable | Publish, flag | | |
| Info / Sev 3 | Trend or anomaly | Log | | |

## SLA / SLO matrix
| DP | Consumer | Freshness SLO | Availability SLO | Quality SLO | Measured by | Owner |
|---|---|---|---|---|---|---|

## Incident process for data issues
<!-- Detect -> triage -> communicate -> fix -> backfill -> post-incident review. Who talks to consumers. -->

## Scorecards and reporting
<!-- What the DQ dashboard shows, who sees it, cadence. -->

## Reconciliation approach
<!-- Which numbers are reconciled to source, how, tolerance. Critical for financials. -->

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
