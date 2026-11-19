---
doc_id: ENG-01
title: Technical Design Document
persona: lead-data-engineer
status: draft
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
related: [DIR-01, ENG-02, ENG-03, ENG-05, ENG-06, ENG-07, ENG-08]
---

# {{project_name}}: Technical Design Document

## 1. Overview
### 1.1 Purpose of this document
### 1.2 Summary of the design
<!-- 5-8 sentences. Platform, layers, transform engine, orchestration, consumption. -->
### 1.3 Goals and non-goals
| Goals | Non-goals |
|---|---|

## 2. Requirements traced to design
| ID | Requirement / NFR | Design section | Verified by |
|---|---|---|---|

## 3. Physical architecture
```mermaid
flowchart LR
  %% workspaces/accounts, storage, compute, network boundaries, identity
```
### 3.1 Component inventory
| Component | Technology / SKU | Purpose | Environment(s) | Owner |
|---|---|---|---|---|
### 3.2 Network and connectivity
<!-- Gateways, private endpoints, firewall rules, source connectivity per SRC. -->
### 3.3 Compute sizing
<!-- Sizing basis, concurrency, scaling rules. Link DIR-06. -->

## 4. Data architecture
### 4.1 Layers
| Layer | Physical location | Format | Load style | Retention | Who can read |
|---|---|---|---|---|---|
### 4.2 Standard technical columns
| Column | Type | Layer(s) | Meaning |
|---|---|---|---|
| `_load_ts` | timestamp | all | When the row was written by the platform |
| `_source_system` | string | bronze+ | SRC id |
| `_batch_id` | string | all | Orchestrator run id |
| `_record_hash` | string | silver+ | Hash of business columns for change detection |
### 4.3 Modeling approach
<!-- Summary, details in ENG-02. Grain and key strategy, SCD policy, surrogate key method. -->

## 5. Ingestion design
<!-- Pattern per source class. Details per pipeline in ENG-03. -->
| Source class | Pattern | Tool | Incremental key | Schema drift handling |
|---|---|---|---|---|

## 6. Transformation design
### 6.1 Engine and project layout
### 6.2 Incremental strategy per layer
### 6.3 Dependency and run order
```mermaid
flowchart TB
  %% DAG of model groups / pipeline groups
```

## 7. Orchestration
### 7.1 Schedules and triggers
| Schedule | Trigger | Pipelines | Must finish by |
|---|---|---|---|
### 7.2 Key flow
```mermaid
sequenceDiagram
  %% ingest -> transform -> test -> publish -> alert
```
### 7.3 Retries, timeouts, concurrency

## 8. Consumption layer
<!-- Semantic models, storage mode, refresh trigger, RLS hookup, endorsement. -->

## 9. Non-functional design
| NFR | How the design meets it | Monitor / test |
|---|---|---|
### 9.1 Performance
### 9.2 Reliability and recovery (RPO/RTO, backups, reprocessing from bronze)
### 9.3 Scalability
### 9.4 Cost controls

## 10. Failure modes
| Failure | Detection | Blast radius | Automatic response | Runbook |
|---|---|---|---|---|
| Source unavailable | | | | ENG-08 |
| Schema change at source | | | | |
| Duplicate / replayed batch | | | | |
| Late-arriving data | | | | |
| Error-severity test failure | | | | |
| Capacity / warehouse throttling | | | | |
| Credential expiry | | | | |

## 11. Security summary
<!-- Identity, secrets, RBAC, RLS/CLS, encryption, audit. Details in ENG-07. -->

## 12. Migration and cutover (if replacing something)
<!-- Parallel run, reconciliation, cutover steps, rollback. -->

## 13. Build order
<!-- Sprint-level sequence of what to build first and why. -->
| Order | Item | Depends on | Done when |
|---|---|---|---|

## 14. Open items
<!-- Q-### and A-### that affect this design. -->

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
