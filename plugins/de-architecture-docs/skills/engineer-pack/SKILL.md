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

Write the docs a senior engineer can build from without a meeting.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- Phase 3 of `architecture-docs`.
- "Write the TDD", "spec the pipelines", "write the runbook".

Not for: the code itself (use the dbt, pipeline and platform skills).

## Inspect first

1. The facts file and ADRs.
2. The repo: real names of workspaces, schemas, models and pipelines.
3. Stack must-cover lists in [references/stack-profiles.md](references/stack-profiles.md)
   (Fabric, Snowflake, Databricks, dbt, Airflow, Power BI, Data Vault, medallion);
   read only the ones that match. For Iceberg, Paimon, Fluss, Flink, Iggy, Lance or
   Firn, also load the matching gordonmurray skill and recheck its dated facts.

## Procedure

Write `engineer/ENG-01..09` from [assets/templates/](assets/templates/); data
contracts (ENG-04) come from `data-contracts`.

| Doc | Must hold |
|---|---|
| ENG-01 TDD | Single action; requirements traced to design; physical diagram; layers and technical columns; ingestion and transform design; orchestration sequence diagram; NFR design; failure modes table; build order |
| ENG-02 Physical model | Grain and primary key per gold model; SCD policy; surrogate keys; partitioning and maintenance; schema evolution |
| ENG-03 Pipeline specs | Per pipeline: pattern, schedule, incremental key, watermark storage, idempotency, late data, deletes, schema drift, retries, partial failure, backfill command ([assets/plans/backfill-plan.yaml](assets/plans/backfill-plan.yaml)), DQ gates, contract, alerts, owner |
| ENG-05 Test strategy | Test pyramid; TST-### catalog traced to NFRs; reconciliation; UAT |
| ENG-06 Environments and CI/CD | Exact promotion steps; secrets; rollback for code and data; release gates ([assets/plans/release-gate-evidence.yaml](assets/plans/release-gate-evidence.yaml)) |
| ENG-07 Security | Principals, groups, RLS/CLS with tests, sensitive columns, audit |
| ENG-08 Observability and runbook | A runbook entry for every ENG-01 failure mode |
| ENG-09 Standards | Naming, layout, SQL and Python style, PR checklist, definition of done |

Schema changes use [assets/plans/schema-change-plan.yaml](assets/plans/schema-change-plan.yaml).

## Standards

- **MUST** use RFC 2119 words (MUST, SHOULD, MAY) for standards.
- **MUST** give every pipeline its idempotency, late data, delete and backfill behavior.
- **MUST** map every failure mode to a runbook entry.
- **SHOULD** use real object names, not placeholders.

## Failure modes

| Failure | Prevention |
|---|---|
| Happy-path design only | Failure modes table plus runbook mapping |
| Gold model with unclear grain | Grain and key required per model |
| Diagram-only deployment docs | Exact promotion steps required |

## Verify

The `lead-engineer-reader` review passes: a new senior engineer could build from it.

## Output

`docs/architecture/engineer/ENG-01..09` and `engineer/adr/` (from `architecture-decision`).
