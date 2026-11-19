# Doc Catalog

Output root: `docs/architecture/` (configurable). Template for each doc lives in
`templates/<pack>/`. Required sections are the template headers.

```
docs/architecture/
├── README.md                          # reading guide by persona, index, open questions
├── 00-project-facts.yaml              # single source of truth
├── executive/                         # CDO / CIO
│   ├── EXE-01-executive-brief.md
│   ├── EXE-02-strategic-architecture-overview.md
│   ├── EXE-03-investment-and-roadmap.md
│   └── EXE-04-risk-and-governance-summary.md
├── director/                          # Data Director
│   ├── DIR-01-solution-architecture.md
│   ├── DIR-02-operating-model-and-raci.md
│   ├── DIR-03-data-governance-and-security.md
│   ├── DIR-04-data-quality-and-sla-framework.md
│   ├── DIR-05-delivery-plan.md
│   └── DIR-06-cost-model-and-finops.md
├── engineer/                          # Lead Data Engineer
│   ├── ENG-01-technical-design-document.md
│   ├── ENG-02-physical-data-model.md
│   ├── ENG-03-pipeline-specifications.md
│   ├── ENG-04-data-contracts/          # one YAML per contract + README
│   ├── ENG-05-test-strategy.md
│   ├── ENG-06-environments-and-cicd.md
│   ├── ENG-07-security-implementation.md
│   ├── ENG-08-observability-and-runbook.md
│   ├── ENG-09-engineering-standards.md
│   └── adr/
│       ├── ADR-0001-<slug>.md
│       └── ...
└── shared/
    ├── glossary.md
    ├── traceability-matrix.md
    └── raid-log.md                    # risks, assumptions, issues, dependencies
```

## Executive pack (CDO / CIO)

| Doc | Purpose | Must answer |
|---|---|---|
| EXE-01 Executive Brief | The 2-page "should we" | Problem, outcome, cost, timeline, risk, decisions needed |
| EXE-02 Strategic Architecture Overview | One picture of what we are building | Capabilities, what changes for the business, what we retire |
| EXE-03 Investment & Roadmap | Money and time | One-time + run cost by year, phases by quarter, value milestones, KPIs |
| EXE-04 Risk & Governance Summary | What could hurt us | Top risks, compliance posture, vendor lock-in, key-person risk, controls |

## Director pack (Data Director)

| Doc | Purpose | Must answer |
|---|---|---|
| DIR-01 Solution Architecture | Logical design | Domains, layers, data products, integration patterns, NFRs, key decisions |
| DIR-02 Operating Model & RACI | Who does what | Team topology, roles, RACI, intake, support model, hiring |
| DIR-03 Data Governance & Security | Control model | Ownership, classification, access model, retention, compliance mapping |
| DIR-04 Data Quality & SLA Framework | Trust | DQ dimensions, SLOs, severity levels, incident process, scorecards |
| DIR-05 Delivery Plan | Execution | Phases, milestones, dependencies, capacity, exit criteria per phase |
| DIR-06 Cost Model & FinOps | Spend control | Cost by component, sizing basis, scaling curve, levers, chargeback |

## Engineer pack (Lead Data Engineer)

| Doc | Purpose | Must answer |
|---|---|---|
| ENG-01 Technical Design Document (TDD) | The master build doc | Physical arch, components, flows, NFR implementation, failure modes |
| ENG-02 Physical Data Model | Exact structures | Layers, entities, grain, keys, SCD, partitioning, DDL, naming |
| ENG-03 Pipeline Specifications | One spec per pipeline | Source, pattern, schedule, incremental logic, idempotency, retries, backfill |
| ENG-04 Data Contracts | Producer/consumer agreements | Schema, semantics, quality rules, SLA, owner, versioning |
| ENG-05 Test Strategy | What proves it works | Test pyramid, dbt tests, DQ checks, reconciliation, perf, UAT |
| ENG-06 Environments & CI/CD | Path to prod | Env topology, branching, deployment, secrets, promotion gates |
| ENG-07 Security Implementation | Controls in code | Identity, RBAC, RLS/CLS, encryption, network, audit |
| ENG-08 Observability & Runbook | Run it at 2am | Logging, metrics, alerts, lineage, on-call, runbook per failure |
| ENG-09 Engineering Standards | How we write code | Naming, folder layout, SQL/Python style, PR checklist, definition of done |
| ADRs | Why we chose | One decision per file, MADR format |

## Shared

| Doc | Purpose |
|---|---|
| glossary.md | Business and technical terms, one definition each, used by all packs |
| traceability-matrix.md | REQ/NFR -> ADR -> design section -> PL/DP -> TST |
| raid-log.md | Risks, assumptions, issues, dependencies with IDs, owners, status |

## Standard ADRs

Only write the ones that are real decisions for this project. Common candidates:

- ADR: Platform choice (Fabric vs Snowflake vs Databricks vs hybrid)
- ADR: Storage format and table format (Delta, Iceberg, native)
- ADR: Layering pattern (medallion, Data Vault 2.0, hybrid raw vault + medallion)
- ADR: Modeling approach for consumption (Kimball star, OBT, semantic model)
- ADR: Ingestion pattern per source class (CDC, incremental watermark, full snapshot, API, files, streaming)
- ADR: Transformation tool (dbt, Spark notebooks, stored procedures, warehouse SQL)
- ADR: Orchestration (Airflow, Fabric Data Factory, ADF, Dagster, dbt Cloud)
- ADR: Workspace / account / environment topology
- ADR: Identity and access model (RBAC groups, RLS strategy)
- ADR: Data quality tooling (dbt tests, Great Expectations, Soda, native DQ)
- ADR: Semantic layer / BI connection mode (Direct Lake, Import, DirectQuery)
- ADR: Source control and CI/CD (Git integration, deployment pipelines, Terraform)
- ADR: Historization (SCD2 where, snapshot retention)
- ADR: Naming conventions
- ADR: Build vs buy for ingestion (native connectors vs Fivetran/Airbyte vs custom)
