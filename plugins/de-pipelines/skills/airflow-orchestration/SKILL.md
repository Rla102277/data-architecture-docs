---
name: airflow-orchestration
description: >-
  Use when building or reviewing Apache Airflow DAGs for data pipelines,
  including Astronomer, MWAA, Cloud Composer and Fabric's Apache Airflow job:
  DAG design, idempotent tasks keyed on the data interval, retries and
  timeouts, backfills and catchup, sensors and dataset (asset) scheduling,
  secrets, alerting, and running dbt from Airflow with Cosmos or bash.
---

# Airflow Orchestration

Airflow schedules and watches work; it should not do the heavy lifting itself.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New DAGs, or DAGs that fail mysteriously, double-load, or cannot backfill.
- Running dbt on a schedule from Airflow.

Not for: orchestration inside Fabric Data Factory pipelines alone (use
`microsoft-fabric-engineering`), or the ingestion logic itself (`incremental-ingestion`).

## Inspect first

1. Airflow version (2.x vs 3.x changes scheduling terms: datasets became assets,
   `schedule_interval` became `schedule`, execution date became logical date).
   Recheck the API for your version.
2. Where it runs (Astronomer, MWAA, Composer, Fabric Apache Airflow job,
   self-hosted) and the executor (Celery, Kubernetes).
3. Existing DAG conventions, connections and secrets backend.

## Procedure

1. **One DAG per pipeline or schedule**, named `<domain>__<pipeline>__<cadence>`,
   with `owner`, `tags`, `doc_md`.
2. **Tasks keyed on the data interval**: every task processes
   `data_interval_start` to `data_interval_end`, never "now". That makes reruns
   and backfills correct.
3. **Push work down**: tasks call the warehouse, Spark, dbt or an API; they do not
   pull data through the Airflow worker.
4. **Defaults**: `retries=2` with exponential backoff for transient errors,
   `execution_timeout` on every task, `max_active_runs=1` for pipelines that must
   run in order, `catchup=False` unless backfilling by design.
5. **dbt**: either Cosmos (`astronomer-cosmos`) to render dbt models as Airflow
   tasks with per-model retries, or one `dbt build --select tag:<schedule>` task
   for small projects. Run `dbt source freshness` first.
6. **Dependencies across DAGs**: dataset/asset-based scheduling or explicit
   sensors with timeouts and `mode="reschedule"`, not long-poking sensors that
   hold worker slots.
7. **Failure visibility**: `on_failure_callback` to Teams, Slack or PagerDuty
   with DAG, task, logical date and log link. SLA or deadline alerts on DAGs with
   delivery promises.
8. **Secrets**: connections from a secrets backend (Key Vault, Secrets Manager),
   never in code or Airflow Variables in plain text.

## Standards

- **MUST** make tasks idempotent for their data interval.
- **MUST** set `execution_timeout` on every task.
- **MUST NOT** do top-level heavy work in DAG files (queries, API calls at import);
  the scheduler parses DAG files constantly.
- **MUST NOT** swallow errors in task code; a failed step must fail the task.
- **SHOULD** keep DAGs thin: business logic in dbt or code packages, not in the DAG.
- **SHOULD** test DAG imports in CI (`python -c "import dag_file"` or `airflow dags test`).

## Failure modes

| Failure | Prevention |
|---|---|
| Rerun of yesterday processes today's data | Data-interval keyed tasks |
| Accidental backfill of a year on deploy | `catchup=False` by default |
| Sensors exhaust worker slots | Reschedule mode, timeouts, or asset scheduling |
| Slow scheduler from heavy DAG files | No top-level work |
| Task "succeeds" but the load failed | Exceptions propagate; audit status checked |
| Silent failures overnight | Failure callbacks to a channel with an owner |

## Verify

- `airflow dags test <dag_id> <date>` runs end to end in a non-production environment.
- Clear and rerun one task for a past interval: target data unchanged.
- A forced failure produces an alert with a working log link.

## Output

DAG files, a test in CI that imports every DAG, and a runbook entry per DAG
(owner, schedule, what to do on failure).
