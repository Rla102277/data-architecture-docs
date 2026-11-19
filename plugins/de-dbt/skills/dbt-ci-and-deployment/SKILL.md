---
name: dbt-ci-and-deployment
description: >-
  Use when setting up or fixing how dbt changes are tested and shipped: slim CI
  with state:modified+ and --defer against production artifacts, per-PR
  schemas, production runs from Airflow, Fabric pipelines, GitHub Actions,
  Azure DevOps or dbt Cloud, artifact storage, blue/green or staged deploys,
  and rollback.
---

# dbt CI and Deployment

Test only what changed, against real production context, and deploy in a way you
can roll back.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- No CI yet, or CI that rebuilds the whole project on every PR.
- Moving dbt runs to production scheduling.

Not for: orchestrating non-dbt work (use `airflow-orchestration`).

## Inspect first

1. Where code lives (GitHub, Azure DevOps) and where prod runs (Airflow, Fabric
   pipeline or notebook, dbt Cloud, a container job).
2. Where production `manifest.json` and `run_results.json` are stored after each
   prod run. Slim CI needs the latest prod manifest.
3. Warehouse cost model: CI that builds everything is often the biggest waste.

## Procedure

1. **Store prod artifacts**: after every prod run, upload `target/manifest.json`
   (and `run_results.json`) to a stable location (blob storage, an artifact
   store, dbt Cloud does this for you).
2. **PR CI** ([assets/github-actions-dbt-ci.yml](assets/github-actions-dbt-ci.yml)):
   - fetch the prod manifest into `prod-artifacts/`
   - `dbt deps`
   - `dbt build --select state:modified+ --defer --state prod-artifacts --target ci`
   - target a per-PR schema (`dbt_ci_pr_<number>`) and drop it when the PR closes
   - add `sqlfluff lint` on changed files
3. **Prod run**: `dbt source freshness`, then `dbt build --target prod` by tag
   or selector per schedule, from the orchestrator. Fail loudly; alert the owner.
4. **Deploy pattern**: merge to `main` deploys. For high-risk marts, build into a
   staging schema and swap (blue/green) only after tests pass, where the
   platform supports cheap swaps (Snowflake `ALTER ... SWAP WITH`, views pointing
   at versioned tables elsewhere).
5. **Rollback**: revert the commit and rerun the affected models; for data,
   use time travel or rebuild from staging. Write the steps in the runbook.

## Standards

- **MUST** run tests in CI (`dbt build`, not `dbt run`).
- **MUST** use separate CI credentials with no write access to prod schemas.
- **MUST** fail the prod job on test errors and alert a named owner.
- **SHOULD** use slim CI (`state:modified+ --defer`) once the project has more
  than a handful of models.
- **SHOULD** add `--empty` (dbt 1.8+) schema-only builds for fast compile checks
  when full CI is costly.
- **SHOULD** clean up CI schemas automatically.

## Failure modes

| Failure | Prevention |
|---|---|
| CI rebuilds everything and costs a fortune | Slim CI with deferral |
| Stale prod manifest makes CI skip changed models | Artifact upload after every prod run, checked for age |
| CI writes into prod by accident | Separate credentials and targets |
| A failed test still lets bad data reach BI | `dbt build` order: tests gate downstream models |
| Orphan CI schemas pile up | Drop on PR close |

## Verify

- Open a PR that changes one model: CI builds that model and its children only,
  and the log shows deferral to prod for parents.
- A deliberately failing test fails the PR.

## Output

CI workflow file, prod job definition, artifact storage step, CI cleanup, and
a runbook entry for rollback.
