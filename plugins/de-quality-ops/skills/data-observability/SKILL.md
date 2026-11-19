---
name: data-observability
description: >-
  Use when you need to know a pipeline or data product is broken before users
  do: freshness, volume, schema change and distribution monitors, pipeline run
  and duration monitoring, alert routing and severity, SLA tracking, lineage
  for impact, and dashboards, using what the platform already has (dbt
  artifacts, Fabric monitoring hub, Snowflake ACCOUNT_USAGE, Airflow) before
  buying a tool.
---

# Data Observability

Watch the few signals that mean "the numbers are wrong or late", route each to
an owner, and stay quiet otherwise.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Users find broken data before the data team does.
- Too many alerts and nobody reads them.

Not for: designing the checks themselves (use `data-quality-checks`), or
handling an active incident (use `pipeline-incident-response`).

## Inspect first

1. The data products with promises (SLAs): what, for whom, ready by when.
2. What signals already exist: dbt `run_results.json` and source freshness,
   orchestrator run history, Fabric monitoring hub and Capacity Metrics,
   Snowflake `QUERY_HISTORY` and `TASK_HISTORY`, the batch audit table.
3. Where alerts go today and who answers them.

## Procedure

1. **Pick monitors per data product** (not per table):
   - freshness: newest data timestamp vs SLA
   - volume: rows per load vs history for the same weekday
   - schema: columns added, removed or retyped since last run
   - run health: failures, retries, duration vs history
   - distribution (only for key measures): null rate, sum, distinct count drift
2. **Severity and routing** ([assets/alert-routing.md](assets/alert-routing.md)):
   P1 (published number wrong or SLA missed for an executive product) pages the
   on-call; P2 goes to the team channel; P3 to a daily digest. Every alert names
   the data product, the owner, the impact, and a runbook link.
3. **Collect results in one place**: a monitoring table or schema fed by dbt
   artifacts, the audit table and platform history; a dashboard on it.
4. **Use lineage for impact**: when a source fails, list the downstream data
   products and consumers affected (from dbt or `lineage-extraction`).
5. **Tune monthly**: remove or fix alerts nobody acted on; add monitors for any
   incident that was found by a user.

## Standards

- **MUST** monitor freshness on every data product with an SLA.
- **MUST** route every alert to a named owner with a runbook link.
- **MUST** alert on a pipeline that reports success but loads zero rows when
  zero is abnormal.
- **SHOULD** compare against history (same weekday) rather than fixed numbers.
- **SHOULD** start with platform signals and dbt artifacts; buy a tool when the
  count of data products or teams outgrows them.

## Failure modes

| Failure | Prevention |
|---|---|
| Success status hides a failed step (masked failure) | Monitor row counts and audit status, not only job status |
| Alert storm, everyone mutes the channel | Severity tiers, digest for low priority, monthly tuning |
| Alert says "job failed" with no context | Data product, owner, impact and runbook in every alert |
| Users discover stale data first | Freshness monitors on every SLA product |
| Root cause found, impact unknown | Lineage-based impact list |

## Verify

Simulate each failure type in test (stop a load, drop a column, load half the
rows) and confirm the right alert reaches the right person within the target time.

## Output

Monitor list per data product, alert routing table, monitoring tables and
dashboard, and runbook links.
