---
name: data-contracts
description: >-
  Use when defining or changing data contracts at a pipeline or product
  boundary: source contracts (what we extract), dataset contracts (what we
  publish) and metric contracts (how a KPI is defined). Covers semantics,
  keys, deletes, late data, quality rules, freshness SLA, ownership and
  compatibility, written as YAML in docs/architecture/engineer/ENG-04-data-contracts/.
---

# Data Contracts

Write one YAML file per boundary in
`docs/architecture/engineer/ENG-04-data-contracts/`, plus a `README.md` index
(contract, producer, consumers, version, status). Follow
[references/conventions.md](references/conventions.md).

| Boundary | Template |
|---|---|
| Source system into the platform | [assets/source-contract.yaml](assets/source-contract.yaml) |
| Published dataset or data product | [assets/dataset-contract.yaml](assets/dataset-contract.yaml) |
| Business metric or KPI definition | [assets/metric-contract.yaml](assets/metric-contract.yaml) |

Templates are from vaquarkhan/data-engineering-agent-skills (MIT). Replace every
example value. Link each contract to its `SRC-`, `DP-`, `KPI-` or `NFR-` id.

## Decisions every contract makes

- Producer, consumers, purpose, owner, classification, freshness SLO, escalation.
- Business and technical keys, uniqueness scope, types, nullability, meaning,
  timezone, units, allowed values, sensitive fields.
- Operational guarantees: cadence, ordering, late arrival, dedupe, **delete
  semantics**, historical corrections, retention.
- Compatibility: what is additive, what is breaking (renames, type narrowing,
  key changes, new required fields), consumer migration window. Never call a
  change safe without checking consumers.
- Where validation runs (source, landing, transform, serving), severity,
  quarantine and who fixes.

## Failure modes

A contract that checks only field names misses semantics. Nullable does not mean
unknown is acceptable. Row counts do not prove referential integrity. Never guess
an upstream delete policy: ask, or log a `Q-###`.

Use a representation the team's tools can enforce (dbt model contracts and
tests, Great Expectations, Soda, platform constraints). Do not invent a
contract system. Mark any validation that has not run.
