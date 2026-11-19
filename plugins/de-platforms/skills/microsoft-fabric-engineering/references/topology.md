# Fabric topology patterns

## Capacities

| Capacity | Hosts | Why |
|---|---|---|
| Production (larger F SKU) | prod workspaces only | Prod reports and loads are never throttled by dev |
| Non-production (smaller F SKU) | dev, test workspaces | Can pause when idle; experiments stay isolated |

## Workspaces (layer x environment)

```
<code>-landing-dev     <code>-landing-test     <code>-landing-prod
<code>-core-dev        <code>-core-test        <code>-core-prod        (raw vault / silver)
<code>-marts-dev       <code>-marts-test       <code>-marts-prod       (gold, warehouse)
<code>-reporting-dev   <code>-reporting-test   <code>-reporting-prod   (semantic models, reports)
```

Fewer workspaces is fine for small teams (one per environment). Split when
access, capacity or ownership differ between layers.

## Data flow

```mermaid
flowchart LR
  src[(Sources)] -->|pipelines, mirroring, gateway| land[Landing lakehouse]
  land -->|notebooks or dbt| core[Core: raw vault / silver]
  core -->|dbt-fabric| marts[Marts warehouse]
  marts -->|Direct Lake or Import| sem[Semantic models]
  sem --> rpt[Reports and apps]
```

## Promotion

Git branch per environment or a single main branch with deployment pipelines
stages (dev, test, prod). Parameterize: connections, lakehouse and warehouse
IDs, capacity assignment. Record which item types are not supported by Git or
deployment pipelines in the deploy runbook as manual steps.
