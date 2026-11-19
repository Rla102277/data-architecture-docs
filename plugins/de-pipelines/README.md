# de-pipelines (plugin)

Pipeline engineering: incremental ingestion (CDC, change tracking, watermarks, snapshots, deletes, late data, schema drift), safe backfill and replay, and Airflow orchestration with dbt.

Install in Claude Code:

```
/plugin install de-pipelines --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [airflow-orchestration](skills/airflow-orchestration/SKILL.md) | building or reviewing Apache Airflow DAGs for data pipelines, including Astronomer, MWAA, Cloud Composer and Fabric's Apache Airflow job: DAG design, idempotent tasks keyed on the data interval, retries and timeouts, backfills and catchup, sensors and dataset (asset) scheduling, secrets, alerting, and running dbt from Airflow with Cosmos or bash |
| [backfill-and-replay](skills/backfill-and-replay/SKILL.md) | historical data must be loaded, reloaded or reprocessed: initial history loads, rebuilding after a logic fix, replaying from raw after a bad run, or recovering a missed window |
| [incremental-ingestion](skills/incremental-ingestion/SKILL.md) | designing or fixing how data is pulled from a source into the platform: choosing CDC, SQL Server change tracking, timestamp watermarks, full snapshots, file drops or API pagination; making loads idempotent; handling deletes, late and corrected rows, schema drift, retries and partial failures; and recording watermarks safely |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
