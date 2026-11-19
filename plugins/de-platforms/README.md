# de-platforms (plugin)

Platform-deep skills for Microsoft Fabric, Snowflake, Power BI semantic models and SQL Server as a source: topology, security, capacity and cost, deployment, and the traps each platform has.

Install in Claude Code:

```
/plugin install de-platforms --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [microsoft-fabric-engineering](skills/microsoft-fabric-engineering/SKILL.md) | building, reviewing or troubleshooting a Microsoft Fabric data platform: workspace and capacity topology (F SKUs), Lakehouse vs Warehouse per layer, OneLake shortcuts and mirroring, Data Factory pipelines, Dataflow Gen2, Copy job and notebooks, dbt-fabric, Git integration and deployment (deployment pipelines, fabric-cicd), security (workspace roles, OneLake data access, RLS), capacity throttling and cost, and table maintenance |
| [power-bi-semantic-models](skills/power-bi-semantic-models/SKILL.md) | designing, reviewing or deploying Power BI semantic models (datasets) on Fabric or Power BI: star schema shape, storage mode (Direct Lake, Import, DirectQuery, composite), DAX measure standards, calculation groups, RLS and OLS with Entra groups, incremental refresh, PBIP and TMDL in Git, deployment pipelines, performance with DAX query view and Best Practice Analyzer, and working from a Mac |
| [snowflake-engineering](skills/snowflake-engineering/SKILL.md) | building, reviewing or cost-tuning a Snowflake platform: database and schema layout per environment, role hierarchy (functional and access roles), warehouses per workload with auto-suspend and resource monitors, Snowpipe, streams and tasks, dynamic tables, dbt-snowflake, zero-copy clones, time travel, masking and row access policies, service user authentication, query tagging and cost attribution |
| [sql-server-source-extraction](skills/sql-server-source-extraction/SKILL.md) | extracting data from an operational SQL Server or Azure SQL database into a warehouse or lakehouse (Fabric, Snowflake, Databricks) without hurting the application: readable secondaries, snapshot isolation, rowversion and datetime watermarks, change tracking, CDC setup and retention, Fabric mirroring, on-premises data gateways, least-privilege logins and safe query patterns |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
