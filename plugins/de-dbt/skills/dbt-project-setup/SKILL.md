---
name: dbt-project-setup
description: >-
  Use when starting a dbt project or straightening out a messy one: adapter
  choice (dbt-fabric, dbt-fabricspark, dbt-snowflake, dbt-sqlserver,
  dbt-databricks), folder layout mapped to platform layers (staging,
  intermediate, marts or raw vault, business vault, marts), profiles and
  environments, packages, naming, sources and freshness, sqlfluff, and the
  first CI run.
---

# dbt Project Setup

Set up a dbt project that a team can grow for years without a rewrite.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New dbt project on Fabric, Snowflake, SQL Server or a lakehouse.
- An existing project with no structure, mixed naming, or no environments.

Not for: writing individual models (use `dbt-model-development`).

## Inspect first

1. Platform and target: Fabric Warehouse (`dbt-fabric`), Fabric Lakehouse via
   Spark (`dbt-fabricspark`), Snowflake (`dbt-snowflake`), SQL Server / Azure SQL
   (`dbt-sqlserver`), Databricks (`dbt-databricks`). Check the adapter's current
   supported dbt version and feature list (materializations, incremental
   strategies, contracts) before committing. Recheck at setup time; adapters move.
2. dbt Core or dbt Cloud / dbt platform, and where it will run (Airflow, Fabric
   pipeline or notebook, GitHub Actions, dbt Cloud jobs).
3. The layering decision (medallion, Data Vault plus marts). If it is not made,
   make it with `architecture-decision` first.
4. Existing sources: names, owners, load timestamps (for freshness).

## Procedure

1. **Scaffold**: `dbt init <project>`; pin dbt and adapter versions in
   `requirements.txt` (or the dbt Cloud version).
2. **Layout** (see [references/layout.md](references/layout.md)): one folder per
   layer, subfolders per source or domain, `_<folder>__models.yml` and
   `_<source>__sources.yml` files beside the SQL.
3. **dbt_project.yml**: default materialization and schema per folder, tags per
   schedule (`daily`, `hourly`), `+persist_docs`, `+on_schema_change` for
   incrementals, and `meta: {owner: ...}` per folder.
4. **Environments**: `dev` (personal schema per developer), `ci` (ephemeral
   schema per PR), `prod`. Secrets from environment variables
   (`{{ env_var('DBT_FABRIC_CLIENT_SECRET') }}`), never in `profiles.yml` in Git.
5. **Custom schema naming**: override `generate_schema_name` so prod uses the
   clean schema (`marts`) and dev and CI use a prefixed one (`dbt_rarchambault_marts`).
6. **Sources**: every raw table declared once with `loaded_at_field` and
   `freshness` (warn/error thresholds) and an owner in `meta`.
7. **Packages**: start with `dbt-utils`; add `dbt-expectations`,
   `dbt-audit-helper`, `codegen`, and a Data Vault package (AutomateDV or
   datavault4dbt) only when needed. Check each package supports your adapter.
8. **Linting**: `.sqlfluff` with the dbt templater and your dialect; pre-commit hook.
9. **First CI**: `dbt deps && dbt build --target ci` on every PR (see `dbt-ci-and-deployment`).

## Standards

- **MUST** pin dbt, adapter and package versions.
- **MUST** keep credentials out of Git: `profiles.yml` reads `env_var()`.
- **MUST** separate dev, CI and prod schemas so a developer cannot overwrite prod.
- **SHOULD** name models by layer: `stg_<source>__<entity>`, `int_<entity>__<verb>`,
  `fct_<process>`, `dim_<entity>`. Double underscore separates source from entity.
- **SHOULD** have exactly one staging model per source table, and only staging
  models select from `source()`.
- **SHOULD** declare an owner for every folder in `meta`.

## Failure modes

| Failure | Prevention |
|---|---|
| Adapter lacks a feature the design assumes | Feature check before setup; ADR records it |
| Developer runs against prod by default | `target: dev` default and separate credentials |
| Models select raw tables directly everywhere | Only staging touches `source()` |
| Packages break on upgrade | Pinned versions, upgrade in a branch with CI |
| Secrets leaked in `profiles.yml` | `env_var()` only, secret scanning in CI |

## Verify

- `dbt debug --target dev` and `--target ci` pass.
- `dbt build --target ci` passes on an empty PR.
- `dbt source freshness` runs and reports every source.

## Output

The project skeleton, `dbt_project.yml`, `profiles.yml.example`, packages,
`.sqlfluff`, a README with how to run locally, and the first CI workflow.
