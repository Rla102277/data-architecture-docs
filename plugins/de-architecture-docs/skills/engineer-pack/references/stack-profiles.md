# Stack Profiles

Read only the profiles that match the project. Each lists what the docs MUST
cover for that tool, so nothing platform-specific gets skipped. Verify current
SKU names, pricing and feature status against vendor docs before putting numbers
in the cost model; mark the price date.

## Microsoft Fabric
- **Topology**: workspaces per layer and/or per environment (example: `fdn-bronze-dev`, `fdn-silver-prod`). State capacity assignment per workspace and why.
- **Storage**: OneLake, Lakehouse vs Warehouse per layer, shortcuts (to ADLS, S3, other workspaces) and mirroring where used. All tables Delta.
- **Ingestion**: Data Factory pipelines, Copy job, Dataflow Gen2, mirroring, notebooks. Pick per source class in an ADR.
- **Transform**: Spark notebooks, T-SQL in Warehouse, dbt (dbt-fabric adapter) against the Warehouse or SQL endpoint. Be explicit about which engine runs which layer.
- **Consumption**: semantic models, Direct Lake vs Import vs DirectQuery (ADR), fallback behavior, refresh orchestration.
- **Capacity**: F-SKU sizing basis, smoothing/bursting and throttling behavior, pause/resume strategy, Capacity Metrics app monitoring.
- **CI/CD**: Git integration (Azure DevOps or GitHub), deployment pipelines, or fabric-cicd / REST APIs. Which items are source-controlled and which are not.
- **Security**: workspace roles, item permissions, OneLake data access roles, RLS/OLS in semantic models, Entra ID groups, private links if required.
- **Governance**: Purview integration, sensitivity labels, endorsement (promoted/certified), domains.
- **Watch-outs to document**: SQL analytics endpoint metadata sync lag, V-Order and table maintenance (OPTIMIZE/VACUUM), Spark session startup time in SLA math.

## Snowflake
- **Topology**: accounts, databases per layer or domain, schemas, environments (separate DBs or accounts). Zero-copy clones for dev/test.
- **Compute**: warehouses per workload (ingest, transform, BI, ad hoc), size, auto-suspend, multi-cluster policy, resource monitors.
- **Ingestion**: Snowpipe / Snowpipe Streaming, COPY INTO, external stages, connectors, partner tools (Fivetran etc.).
- **Transform**: dbt, Dynamic Tables, Streams + Tasks. State which and where.
- **Security**: role hierarchy (functional vs access roles), RBAC model diagram, masking policies, row access policies, network policies, key-pair auth for service users.
- **Ops**: Time Travel and Fail-safe retention per layer, ACCOUNT_USAGE monitoring, query tagging for cost attribution.
- **Sharing**: secure shares / listings if data leaves the account.

## Databricks
- **Topology**: workspaces, Unity Catalog metastore, catalogs per env or layer, schemas, external locations.
- **Compute**: job clusters vs all-purpose vs serverless, SQL warehouses for BI, cluster policies.
- **Pipelines**: Lakeflow Declarative Pipelines (formerly DLT) or Jobs with notebooks/dbt, Auto Loader for files, expectations for DQ.
- **Security**: Unity Catalog grants, row filters and column masks, service principals.
- **CI/CD**: Databricks Asset Bundles, repos/Git folders.
- **Ops**: system tables for billing and audit, OPTIMIZE / liquid clustering, predictive optimization.

## dbt
- **Project layout**: `models/staging`, `models/intermediate`, `models/marts` (or `raw_vault`/`business_vault`/`marts`). State the mapping to platform layers.
- **Materializations** per layer: view, table, incremental (strategy: merge, delete+insert, insert_overwrite, microbatch), snapshot. Justify incremental `unique_key` and `is_incremental()` filter.
- **Tests**: generic (unique, not_null, relationships, accepted_values), dbt-utils / dbt-expectations, unit tests, model contracts (`contract: enforced`), severity `error` vs `warn`.
- **Docs**: descriptions, exposures for dashboards, `meta` for owner and PII flags.
- **Run**: tags/selectors per schedule, `dbt build` order, state-based CI (`state:modified+`, `--defer`), slim CI.
- **Standards**: sqlfluff config, naming (`stg_<source>__<entity>`, `int_<entity>_<verb>`, `fct_`, `dim_`).

## Airflow (or Astronomer / MWAA / Fabric Apache Airflow job)
- DAG per schedule or per domain; naming; owner; `catchup` and `max_active_runs`.
- Idempotent tasks keyed on `data_interval_start`; backfill procedure.
- Retries, retry delay, SLAs / deadline alerts, failure callbacks to Teams/Slack/PagerDuty.
- Connections and secrets backend (Key Vault, Secrets Manager); no secrets in DAG code.
- How dbt runs (Cosmos, BashOperator, dbt Cloud operator).
- Dataset/asset-aware scheduling if used.

## Power BI
- Semantic model ownership: shared golden model vs per-domain; thin reports.
- Storage mode per model (ADR). Refresh schedule tied to upstream completion, not wall clock, where possible.
- RLS roles mapped to Entra groups; OLS for sensitive columns.
- Source control as PBIP/TMDL; deployment pipelines; naming of measures; measure documentation.
- Certified vs promoted content; workspace app distribution.

## Data Vault 2.0
- Raw vault: hubs (business keys), links (relationships), satellites (descriptive history, split by rate of change and source). Hash key and hashdiff algorithm and casing/trim rules stated exactly.
- Business vault: PIT and bridge tables, computed satellites, effectivity satellites.
- Loading: insert-only, parallel loads, record source and load date standards, ghost records.
- Information marts: Kimball star on top of the vault; virtualized vs materialized.
- Tooling: AutomateDV / datavault4dbt macros if dbt; state the package and version.
- Document why Data Vault (auditability, many sources, changing business rules) and what it costs (more objects, more joins), in an ADR.

## Medallion (generic)
- Bronze: as-landed, append or history, metadata columns (`_load_ts`, `_source_file`, `_batch_id`), schema-on-read tolerance.
- Silver: typed, deduplicated, conformed keys, SCD where needed, DQ applied.
- Gold: business-ready, modeled for consumption (star, aggregates, data products).
- State retention, reprocessing approach, and which layer is the "system of record" for history.
