# de-dbt (plugin)

Opinionated dbt for Fabric, Snowflake and SQL Server: project setup, model development and incremental strategies, tests and contracts, snapshots, and CI/CD with slim CI and environments.

Install in Claude Code:

```
/plugin install de-dbt --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [dbt-ci-and-deployment](skills/dbt-ci-and-deployment/SKILL.md) | setting up or fixing how dbt changes are tested and shipped: slim CI with state:modified+ and --defer against production artifacts, per-PR schemas, production runs from Airflow, Fabric pipelines, GitHub Actions, Azure DevOps or dbt Cloud, artifact storage, blue/green or staged deploys, and rollback |
| [dbt-model-development](skills/dbt-model-development/SKILL.md) | writing or changing dbt models: staging, intermediate and mart models, choosing materializations, building incremental models (merge, delete+insert, append, insert_overwrite, microbatch) with correct unique_key, lookback for late data and on_schema_change, snapshots for SCD Type 2, ref and source usage, macros, and documentation |
| [dbt-project-setup](skills/dbt-project-setup/SKILL.md) | starting a dbt project or straightening out a messy one: adapter choice (dbt-fabric, dbt-fabricspark, dbt-snowflake, dbt-sqlserver, dbt-databricks), folder layout mapped to platform layers (staging, intermediate, marts or raw vault, business vault, marts), profiles and environments, packages, naming, sources and freshness, sqlfluff, and the first CI run |
| [dbt-testing-and-contracts](skills/dbt-testing-and-contracts/SKILL.md) | adding or reviewing tests in a dbt project: generic tests (unique, not_null, relationships, accepted_values), dbt-utils and dbt-expectations tests, singular tests, unit tests on fixed inputs (dbt 1.8+), model contracts with enforced data types and constraints, severity and warn/error thresholds, store_failures, and source freshness |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
