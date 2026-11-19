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

Write down, per boundary, what producers promise and consumers can rely on.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- ENG-04 in the engineer pack.
- A new source, a new published dataset, or a KPI whose definition is disputed.
- Before any breaking schema change.

Not for: test implementation (use `dbt-testing-and-contracts` or `data-quality-checks`).

## Inspect first

1. Producer, consumers and their use; the facts file IDs (`SRC-`, `DP-`, `KPI-`, `NFR-`).
2. Profiles of the data (keys, nulls, deletes, late arrivals) from `data-profiling`.
3. Tools the team can enforce with: dbt contracts and tests, Great Expectations,
   Soda, platform constraints.

## Procedure

1. Pick the template (from vaquarkhan/data-engineering-agent-skills, MIT):
   source ([assets/source-contract.yaml](assets/source-contract.yaml)), dataset
   ([assets/dataset-contract.yaml](assets/dataset-contract.yaml)) or metric
   ([assets/metric-contract.yaml](assets/metric-contract.yaml)).
2. Fill every field; replace all example values; link the facts-file ID.
3. Decide: keys and uniqueness scope, types, nullability and meaning, timezone,
   units, allowed values, sensitive fields; cadence, ordering, late arrival,
   dedupe, **delete semantics**, corrections, retention; compatibility (additive
   vs breaking, migration window); where validation runs, severity, quarantine, owner.
4. Write `ENG-04-data-contracts/README.md`: contract, producer, consumers, version, status.

## Standards

- **MUST** define delete semantics; never guess an upstream delete policy (ask, or log a `Q-###`).
- **MUST** check consumers before calling a change safe.
- **MUST** mark validations that have not run.
- **SHOULD** use a representation the team's tools can enforce.

## Failure modes

| Failure | Prevention |
|---|---|
| Contract checks names, misses meaning | Semantics, units and timezone required |
| "Nullable" read as "unknown is fine" | Meaning of null stated |
| Breaking change shipped as minor | Compatibility rules and consumer check |

## Verify

Each contract has an owner, a delete policy, compatibility rules and a linked ID.

## Output

`docs/architecture/engineer/ENG-04-data-contracts/*.yaml` and its README.
