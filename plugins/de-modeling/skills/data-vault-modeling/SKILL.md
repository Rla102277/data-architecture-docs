---
name: data-vault-modeling
description: >-
  Use when designing, building or reviewing a Data Vault 2.0 layer: hubs,
  links, satellites, hash keys and hashdiffs, multi-source and multi-active
  satellites, effectivity satellites, PIT and bridge tables, the business vault,
  and information marts on top, built with dbt packages such as AutomateDV or
  datavault4dbt on Fabric, Snowflake or SQL Server.
---

# Data Vault Modeling

Integrate many sources with full history and audit, then serve stars from it.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Many sources describe the same business entities and change over time.
- Audit and restatement matter (finance, regulated data), and rules keep changing.
- Reviewing a vault that has become a pile of satellites nobody queries.

Not for: a single source with stable rules and one team (a well-built
dimensional model is simpler; make that call in an ADR with `architecture-decision`).

## Inspect first

1. Business keys per entity, per source. Profile them: uniqueness, format, nulls,
   overlap across sources (the same customer in ERP and CRM?).
2. Relationships between entities as they occur in source transactions.
3. Change rates of attributes (to split satellites).
4. The dbt package and its support for your platform. AutomateDV and
   datavault4dbt support different adapters; check Fabric support for the exact
   version before committing, and pin it.

## Procedure

1. **Hubs**: one per business concept with a stable business key
   (`hub_customer` on `customer_id`). Columns: hash key, business key(s),
   `load_datetime`, `record_source`. Insert-only.
2. **Links**: one per relationship or transaction between hubs
   (`link_customer_order`). Hash key of the combined business keys plus the hub
   hash keys. Insert-only.
3. **Satellites**: descriptive attributes with history, per hub or link,
   **split by source and by rate of change** (`sat_customer_erp_details`,
   `sat_customer_crm_contact`). Columns: parent hash key, `load_datetime`,
   `hashdiff`, attributes, `record_source`. A new row only when the hashdiff changes.
4. **Hashing standard** ([references/hashing.md](references/hashing.md)): one
   algorithm, one delimiter, one null token, trim and upper-case rules,
   documented once and implemented once (package config or a macro).
5. **Staging for the vault**: typed, hashed staging models per source table
   (package `stage` macros) with `record_source` and `load_datetime`.
6. **Business vault**: computed satellites for derived rules, effectivity
   satellites for relationships that start and end, **PIT** tables for fast
   point-in-time joins across satellites, **bridges** for paths across links.
7. **Information marts**: Kimball facts and dimensions built from hubs, links,
   PITs and bridges. Users query marts, never the raw vault.

## Standards

- **MUST** keep the raw vault insert-only and source-faithful. Business rules
  go in the business vault or marts, so they can change without reloading history.
- **MUST** use one hashing standard everywhere. A mismatch in trim or case
  splits one customer into two hubs.
- **MUST** carry `record_source` and `load_datetime` on every vault row.
- **SHOULD** split satellites by source and change rate; one giant satellite per
  hub rewrites every attribute on every change.
- **SHOULD** build PITs for any mart that joins three or more satellites.
- **SHOULD** use ghost records (zero-key rows) so PIT joins never drop rows.
- **SHOULD NOT** model every source table as a hub. Hubs are business concepts,
  not tables.

## Failure modes

| Failure | Prevention |
|---|---|
| Same entity in two hubs because of key formatting | Hashing standard with trim and case rules |
| Hub per source table, not per business concept | Business key analysis first |
| Users query the raw vault and get wrong answers | Marts are the only consumer interface |
| Satellites explode with unchanged rows | Hashdiff compare before insert |
| Point-in-time queries too slow | PIT tables |
| Package on an unsupported adapter | Support checked and version pinned |

## Verify

- Hub uniqueness: one row per business key hash.
- For a sample of business keys, the satellite history matches source change history.
- Mart totals match source totals for a period.
- Reloading the same batch inserts zero new rows (idempotent).

## Output

A vault model spec (hubs, links, satellites with keys and sources), the hashing
standard, and the dbt models with tests.
