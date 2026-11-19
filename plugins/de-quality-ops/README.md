# de-quality-ops (plugin)

Keep data trustworthy in production: data quality checks with severity and quarantine, source-to-target reconciliation and financial controls, observability (freshness, volume, schema) and pipeline incident response.

Install in Claude Code:

```
/plugin install de-quality-ops --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [data-observability](skills/data-observability/SKILL.md) | you need to know a pipeline or data product is broken before users do: freshness, volume, schema change and distribution monitors, pipeline run and duration monitoring, alert routing and severity, SLA tracking, lineage for impact, and dashboards, using what the platform already has (dbt artifacts, Fabric monitoring hub, Snowflake ACCOUNT_USAGE, Airflow) before buying a tool |
| [data-quality-checks](skills/data-quality-checks/SKILL.md) | deciding what data quality checks a pipeline or data product needs and wiring them in: completeness, uniqueness, validity, referential integrity, freshness and volume checks, severity (block vs warn), where each check runs (landing, staging, marts), quarantine of bad rows, ownership, and tooling (dbt tests, Great Expectations, Soda, platform constraints) |
| [data-reconciliation](skills/data-reconciliation/SKILL.md) | warehouse or lakehouse numbers must tie to a system of record: source-to-target row and amount reconciliation, GL tie-outs for revenue, COGS and margin, tolerance rules, timing differences, reconciliation evidence for SOX and audit, and automated reconciliation reports that run with every load |
| [pipeline-incident-response](skills/pipeline-incident-response/SKILL.md) | a data pipeline or data product is broken now: failed or silently wrong loads, stale dashboards, duplicate or missing data, a bad deploy, a source outage |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
