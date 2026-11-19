---
name: sql-server-source-extraction
description: >-
  Use when extracting data from an operational SQL Server or Azure SQL
  database into a warehouse or lakehouse (Fabric, Snowflake, Databricks)
  without hurting the application: readable secondaries, snapshot isolation,
  rowversion and datetime watermarks, change tracking, CDC setup and retention,
  Fabric mirroring, on-premises data gateways, least-privilege logins and safe
  query patterns.
---

# SQL Server Source Extraction

Pull from production SQL Server safely, consistently and incrementally.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Onboarding an ERP or app database on SQL Server as a source.
- Extracts that block users, miss rows or read inconsistent data.

Not for: the general pattern decision (start with `incremental-ingestion`).

## Inspect first

1. Version and edition (`SELECT @@VERSION`), hosting (on-premises, VM, Azure SQL,
   Managed Instance), and whether a readable secondary (Availability Group) exists.
2. What is already enabled: CDC (`sys.databases.is_cdc_enabled`), change
   tracking (`sys.change_tracking_databases`), `rowversion` columns on the tables.
3. The DBA's rules: allowed windows, max query duration, who approves enabling
   CDC or change tracking. Enabling either changes the source; never do it
   without the owner's approval.
4. Network path: direct, gateway, private endpoint.

## Procedure

1. **Connect to a readable secondary** when one exists
   (`ApplicationIntent=ReadOnly`), so extracts do not compete with the app.
2. **Consistency**: ask the DBA to enable `READ_COMMITTED_SNAPSHOT` or
   `ALLOW_SNAPSHOT_ISOLATION` and extract under snapshot isolation, so a multi-table
   extract sees one point in time without blocking writers. Never use `NOLOCK`.
3. **Pick the change signal per table** (see [references/change-signals.sql](references/change-signals.sql)):
   - `rowversion` column: best watermark (monotonic, set on every update by the engine).
   - Change tracking: net changes plus deletes, light overhead, with
     `CHANGE_TRACKING_MIN_VALID_VERSION` checks so you know when you must resync.
   - CDC: every change with before/after values; monitor capture job lag and the
     cleanup retention (default 3 days) against your longest possible outage.
   - `datetime` updated column: only after verifying it is maintained on every update.
4. **Or mirror**: Fabric mirroring for supported SQL Server versions replicates
   tables into OneLake in near real time; check supported versions, table limits
   and what it does not replicate before choosing it.
5. **Least privilege**: a dedicated login with `SELECT` on the needed schemas
   (plus change tracking or CDC function permissions), no `db_owner`.
6. **Query shape**: select explicit columns, filter on indexed change columns,
   page large tables by key ranges, set a query timeout.
7. **Record** the version or LSN or watermark per table per batch in the control table.

## Standards

- **MUST** get owner approval before enabling CDC or change tracking or
  changing isolation settings on a source.
- **MUST NOT** use `NOLOCK` for extracts.
- **MUST** check `CHANGE_TRACKING_MIN_VALID_VERSION` (or CDC min LSN) before each
  incremental pull and trigger a full resync when your stored version is older.
- **SHOULD** prefer `rowversion` over `datetime` columns as a watermark.
- **SHOULD** extract from a readable secondary when available.

## Failure modes

| Failure | Prevention |
|---|---|
| Extract blocks order entry | Readable secondary, snapshot isolation, off-peak, timeouts |
| Inconsistent extract across related tables | Snapshot isolation for the whole extract |
| Change tracking version expired after a long outage, changes lost | Min valid version check, automatic resync |
| CDC cleanup removed changes before they were read | Retention sized above max outage; lag alerting |
| App updates skip the `ModifiedDate` column | Prefer rowversion or change tracking |
| Over-privileged extract login | Dedicated least-privilege login |

## Verify

- Insert, update and delete a test row in a non-production copy: all three arrive.
- Simulate an expired version (or test the resync path) in non-production.
- Extract duration and blocking observed on the source during a real run.

## Output

Per-table extraction spec (signal, columns, version handling), the login and
permission script for the DBA, and the control table entries.
