---
name: snowflake-engineering
description: >-
  Use when building, reviewing or cost-tuning a Snowflake platform: database
  and schema layout per environment, role hierarchy (functional and access
  roles), warehouses per workload with auto-suspend and resource monitors,
  Snowpipe, streams and tasks, dynamic tables, dbt-snowflake, zero-copy clones,
  time travel, masking and row access policies, service user authentication,
  query tagging and cost attribution.
---

# Snowflake Engineering

Keep Snowflake simple, secure and cheap: few roles done right, warehouses that
sleep, and costs you can attribute.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New Snowflake account or a sprawling one to clean up.
- "Our bill went up." "Who can see salary data?" "Streams and tasks or dbt?"

Not for: query-level tuning (use `sql-performance-tuning`).

## Inspect first

1. Edition (features like masking policies and ACCESS_HISTORY need Enterprise+).
2. `SNOWFLAKE.ACCOUNT_USAGE`: `WAREHOUSE_METERING_HISTORY`, `QUERY_HISTORY`,
   `GRANTS_TO_ROLES`, `GRANTS_TO_USERS`, `LOGIN_HISTORY` for the last 30 to 90 days.
3. Current roles, warehouses (size, auto-suspend, min/max clusters), resource
   monitors, network policies, and how service users authenticate.

## Procedure

1. **Layout**: database per environment and layer (`RAW_PROD`, `ANALYTICS_PROD`,
   `ANALYTICS_DEV`) or per domain; schemas per source or subject area.
2. **Roles** ([references/rbac.md](references/rbac.md)): access roles own
   privileges on objects (`AR_ANALYTICS_PROD_READ`), functional roles get access
   roles (`FR_ANALYST`, `FR_TRANSFORMER`, `FR_LOADER`), users get functional
   roles. Future grants on schemas so new tables inherit access.
3. **Warehouses per workload**: `WH_LOAD`, `WH_TRANSFORM`, `WH_BI`, `WH_ADHOC`,
   each with `AUTO_SUSPEND = 60` (seconds), `AUTO_RESUME = TRUE`, the smallest size
   that meets its SLA, multi-cluster only for BI concurrency. Resource monitors
   with notify and suspend thresholds.
4. **Loading**: Snowpipe or Snowpipe Streaming for continuous files and events,
   `COPY INTO` for batch, connectors where they fit.
5. **Transforming**: dbt-snowflake for modeled layers; dynamic tables for simple
   declarative refresh with a target lag; streams and tasks for change-driven
   procedural logic. Pick one primary approach per layer in an ADR.
6. **Data protection**: masking policies for sensitive columns, row access
   policies for row-level rules, tags for classification. Time travel retention
   set on purpose per database (cost vs recovery).
7. **Service users**: key-pair or OAuth authentication, not passwords; network
   policies for service users. Recheck Snowflake's current authentication
   requirements, which have tightened against password-only sign-in.
8. **Cost attribution**: `ALTER SESSION SET QUERY_TAG` from dbt and tools,
   warehouse per team or workload, monthly review of metering by warehouse and tag.

## Standards

- **MUST** grant privileges to roles, never to users directly.
- **MUST** auto-suspend every warehouse.
- **MUST** use resource monitors on every warehouse that can run unattended.
- **MUST** use key-pair or OAuth for service users.
- **SHOULD** use zero-copy clones for dev and CI data instead of copies.
- **SHOULD** scale up for slow single queries (spill), out for queueing.
- **SHOULD** keep `ACCOUNTADMIN` to a few named humans with MFA, never a service.

## Failure modes

| Failure | Prevention |
|---|---|
| Runaway warehouse cost | Auto-suspend, resource monitors, monthly metering review |
| New tables invisible to analysts | Future grants on schemas |
| Role spaghetti nobody can audit | Access roles vs functional roles pattern |
| Sensitive columns readable by everyone with SELECT | Masking policies with tags |
| Service password leaked or blocked by policy | Key-pair auth |
| Time travel storage cost surprise | Retention set per database on purpose |

## Verify

- `SHOW WAREHOUSES`: every warehouse has auto-suspend and a monitor.
- Sample a sensitive column as an analyst role: masked.
- Metering by warehouse for the last month matches expectations.

## Output

Account layout, role design with grants script, warehouse and monitor config,
protection policies, and a cost review query set.
