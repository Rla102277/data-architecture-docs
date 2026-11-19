---
name: microsoft-fabric-engineering
description: >-
  Use when building, reviewing or troubleshooting a Microsoft Fabric data
  platform: workspace and capacity topology (F SKUs), Lakehouse vs Warehouse
  per layer, OneLake shortcuts and mirroring, Data Factory pipelines, Dataflow
  Gen2, Copy job and notebooks, dbt-fabric, Git integration and deployment
  (deployment pipelines, fabric-cicd), security (workspace roles, OneLake
  data access, RLS), capacity throttling and cost, and table maintenance.
---

# Microsoft Fabric Engineering

Build on Fabric with clear workspace boundaries, capacity you understand, and
deployments you can repeat.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Designing or reviewing a Fabric platform, workspace layout or capacity plan.
- "Why is Fabric throttling?" "Lakehouse or Warehouse?" "How do we deploy?"

Not for: Power BI semantic model design (use `power-bi-semantic-models`).

## Inspect first

Fabric changes monthly. Recheck current docs for any feature you rely on,
especially anything in preview. Facts below were checked 2026-11.

1. Capacities: SKU per capacity, which workspaces sit on which, and the
   Capacity Metrics app (utilization, throttling, overages) for the last 14 days.
2. Workspaces: names, environment, layer, roles, Git connection, deployment pipeline.
3. Items: lakehouses, warehouses, pipelines, notebooks, dataflows, semantic models,
   and which are source-controlled.
4. How data arrives: pipelines, mirroring, shortcuts, notebooks, gateways.

## Procedure

1. **Topology** (see [references/topology.md](references/topology.md)): separate
   production and non-production capacities so dev work cannot throttle prod;
   workspaces per environment and per layer or domain; consistent names
   (`<code>-<layer>-<env>`).
2. **Pick the engine per layer** in an ADR:
   - Lakehouse (Spark, Delta) for landing and heavy transformation in Python/Spark.
   - Warehouse (T-SQL, Delta underneath) for SQL-first teams, dbt-fabric, and
     multi-table transactions.
   - Both read each other through OneLake shortcuts or cross-database queries.
3. **Ingestion**: pipelines with Copy activity or Copy job for batch, mirroring
   for supported databases (near real time, check source limits), shortcuts to
   avoid copying data already in ADLS, S3 or other workspaces, gateways for
   on-premises sources.
4. **Transformation**: dbt-fabric on the Warehouse, or notebooks on the
   Lakehouse; orchestrate with pipelines (or Airflow), passing parameters, with
   failures surfacing as pipeline failures.
5. **Source control and deployment**: connect every workspace to Git (Azure DevOps
   or GitHub). Promote with deployment pipelines or `fabric-cicd` from CI,
   parameterizing connections and workspace IDs per environment. Know which item
   types support Git and which do not; document the manual steps for the rest.
6. **Security**: Entra ID groups only, workspace roles minimal (Viewer for
   consumers, Contributor for engineers, Admin for few), OneLake data access roles
   or SQL permissions for layer-level access, RLS and OLS in semantic models.
7. **Capacity and cost**: watch Capacity Metrics weekly; understand smoothing
   (background jobs are spread over 24 hours, interactive over minutes) and the
   throttling stages; schedule heavy jobs away from business hours; pause
   non-production capacities when idle if your agreement allows.
8. **Table maintenance**: V-Order and optimized writes on; scheduled `OPTIMIZE`
   and `VACUUM` (respecting time travel needs) on Lakehouse Delta tables with
   frequent small writes.

## Standards

- **MUST** separate production from development capacity.
- **MUST** put every workspace that holds production logic under Git.
- **MUST** grant access through Entra groups, never individuals.
- **MUST** surface failures: a notebook or proc that catches an error must
  re-raise it so the pipeline run fails and alerts.
- **SHOULD** account for the SQL analytics endpoint's metadata sync delay after
  Lakehouse writes before downstream SQL reads (trigger a refresh or wait).
- **SHOULD** keep secrets in Azure Key Vault (or Fabric's supported secret
  mechanism), referenced, never pasted into notebooks or pipeline JSON.

## Failure modes

| Failure | Prevention |
|---|---|
| Dev experiment throttles prod reports | Separate capacities |
| Pipeline shows success while a notebook step failed silently | Re-raise errors; check activity output, not only status |
| Downstream SQL reads stale Lakehouse data | Endpoint sync handled before reads |
| Deployments by hand drift between environments | Git plus deployment pipelines or fabric-cicd |
| Capacity overage surprise | Weekly Capacity Metrics review, heavy jobs off-peak |
| Preview feature changes behavior | Preview use recorded in ADRs and rechecked |

## Verify

- Capacity Metrics: no throttling in prod over the last 14 days, or a plan for it.
- A full deploy from Git to test reproduces the workspace without manual steps
  (or the manual steps are listed).
- A forced failure in each pipeline produces a failed run and an alert.

## Output

Topology diagram and naming standard, capacity plan, ADRs for engine and
deployment choices, and a deploy runbook.
