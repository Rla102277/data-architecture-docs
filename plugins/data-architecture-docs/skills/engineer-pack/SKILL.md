---
name: engineer-pack
description: >-
  Use when writing or revising the Lead Data Engineer documents for a data
  platform: Technical Design Document (TDD), physical data model, pipeline
  specifications, test strategy, environments and CI/CD, security
  implementation, observability and runbook, and engineering standards
  (ENG-01..09). Build-ready detail: grain, keys, idempotency, failure modes.
---

# Engineer Pack (Lead Data Engineer)

Write `docs/architecture/engineer/ENG-01..09` from
[assets/templates/](assets/templates/). Read the facts file and the ADRs first.
Data contracts (ENG-04) come from the `data-contracts` skill. Follow
[references/conventions.md](references/conventions.md).

## The reader

Builds it, sets standards, reviews every PR, gets paged. Needs enough detail to
build without a meeting: physical architecture, models (grain, keys, SCD,
partitioning), pipeline behavior (incremental logic, idempotency, retries,
backfill, late data, deletes, schema drift), tests, environments and promotion,
security in code, observability and runbooks, standards.

## Voice

Precise and imperative. RFC 2119 words for standards: "PL-004 MUST be
idempotent on `load_date`; re-running a day overwrites that partition."

## Rules per doc

| Doc | Must hold |
|---|---|
| ENG-01 TDD | Single action; requirements traced to design; physical diagram; layers with technical columns; ingestion and transform design; orchestration with a sequence diagram; NFR design; failure modes table; build order |
| ENG-02 Physical model | Grain and primary key for every gold model; SCD policy; surrogate key method; partitioning and maintenance; schema evolution policy |
| ENG-03 Pipeline specs | Per pipeline: pattern, schedule, incremental key, watermark storage, idempotency, late data, deletes, schema drift, retries, partial failure, backfill command, DQ gates, contract, alerts, owner. Backfills use [assets/plans/backfill-plan.yaml](assets/plans/backfill-plan.yaml); schema changes use [assets/plans/schema-change-plan.yaml](assets/plans/schema-change-plan.yaml) |
| ENG-05 Test strategy | Test pyramid; catalog of TST-### traced to NFRs; reconciliation design; UAT plan |
| ENG-06 Environments and CI/CD | Exact promotion steps, not just a diagram; secrets; rollback for code and data. Release gates use [assets/plans/release-gate-evidence.yaml](assets/plans/release-gate-evidence.yaml) |
| ENG-07 Security | Principals, groups, RLS/CLS rules with tests, sensitive column handling, audit |
| ENG-08 Observability and runbook | Every ENG-01 failure mode has a runbook entry (symptom, diagnose, fix, verify, communicate) |
| ENG-09 Standards | Naming, folder layout, SQL and Python style, PR checklist, definition of done |

Stack-specific must-cover lists (Fabric, Snowflake, Databricks, dbt, Airflow,
Power BI, Data Vault 2.0, medallion) are in
[references/stack-profiles.md](references/stack-profiles.md). Read only the ones
that match. For Iceberg, Paimon, Fluss, Flink, Iggy, Lance or Firn, also load the
matching gordonmurray skill and recheck its dated version facts before citing them.

Test: could a new senior engineer start building from this pack without a meeting?
