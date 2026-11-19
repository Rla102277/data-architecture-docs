---
name: project-facts
description: >-
  Use when starting, grounding or refreshing a data architecture doc set, or
  when a fact (cost, date, SLA, source, owner, decision) changes. Runs the
  Data Warrior ground gate, surveys the repo, interviews for gaps and builds or
  updates docs/architecture/00-project-facts.yaml, the single source of truth.
---

# Project Facts

Build and maintain `docs/architecture/00-project-facts.yaml`, the one place
every fact lives.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- Phase 1 of `architecture-docs`.
- "Our budget changed" or "we moved go-live": update the fact, then every doc using it.

Not for: writing the docs themselves (the pack skills do that).

## Inspect first

1. An existing facts file, `SCROLL.md` or brief: start from them and cite the source.
2. The repo (brownfield), citing paths: dbt (`dbt_project.yml`, `models/`,
   `sources.yml`), orchestration (Airflow DAGs, Fabric/ADF pipeline JSON,
   Databricks jobs), notebooks and procs, IaC and CI/CD, semantic models
   (`.pbip`, `.tmdl`), READMEs, ADRs, `docs/reverse-engineering/`.

## Procedure

1. **Ground gate first**, one question per turn, each with a suggested answer:
   decision (and for whom), outcome (KPI), terrain (non-negotiable constraints),
   falsifiers (what would prove the approach wrong early), owner (a person or
   role), single action (one sentence). If the single action will not fit in one
   sentence, stop and tell the user. Deshi: explain why each matters; Rōnin:
   crisp question plus default; Kensei: add the second-order risk of each answer.
2. **Survey** the repo (Inspect first) and record observed vs assumed.
3. **Interview for gaps** with [references/discovery-questions.md](references/discovery-questions.md):
   batches of at most 6, each with a default. "Just go" means defaults, each logged as `A-###`.
4. **Write the file** from [assets/project-facts.template.yaml](assets/project-facts.template.yaml):
   unknowns `null` with a `Q-###`; costs with unit x volume x frequency and
   `price_date`; risks with a `type` (technical, delivery, security, compliance, void).
5. **Checkpoint**: show the single action, sources, key NFRs, top decisions and
   top open questions; ask for corrections.
6. **Refresh mode**: change the fact, bump `facts_version`, list every doc that
   cites it so packs get updated.

## Standards

- **MUST** fill the ground gate before anything else.
- **MUST** cite where each observed fact came from.
- **MUST NOT** invent volumes, prices, owners or dates.
- **SHOULD** keep IDs stable across refreshes; retire, never reuse.

## Failure modes

| Failure | Prevention |
|---|---|
| Docs start before anyone agrees what the project is for | Ground gate and checkpoint |
| A number changed in one doc only | Refresh lists every citing doc |
| Defaults mistaken for decisions | Logged as `A-###` assumptions |

## Verify

- `ground.single_action` is one sentence and not null (the docs linter fails otherwise).
- Every ID referenced by any doc is defined in the facts file or a doc heading.

## Output

`docs/architecture/00-project-facts.yaml` and a short checkpoint summary for the user.
