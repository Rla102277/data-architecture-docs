---
name: project-facts
description: >-
  Use when starting, grounding or refreshing a data architecture doc set, or
  when a fact (cost, date, SLA, source, owner, decision) changes. Runs the
  Data Warrior ground gate, surveys the repo, interviews for gaps and builds or
  updates docs/architecture/00-project-facts.yaml, the single source of truth.
---

# Project Facts

Build and maintain `docs/architecture/00-project-facts.yaml`. Every other doc
reads from it. Follow [references/conventions.md](references/conventions.md).

## 1. Ground gate (first, always)

Fill the `ground:` block before anything else. Ask **one question per turn**,
with a suggested answer the user can accept. Skip any that a `SCROLL.md`, brief
or prior facts file already answers, and cite the source.

1. **Decision**: what decision will this make clearer, and for whom?
2. **Outcome**: what changes in the business if it works? (ties to a KPI)
3. **Terrain**: which constraints are not negotiable? (team, budget, deadline, compliance, existing platform)
4. **Falsifiers**: what evidence would prove this approach wrong, early?
5. **Owner**: who owns the outcome? A person or role, not a team.
6. **Single action**: in one sentence, what must someone do right now?

If the single action will not fit in one sentence, stop and tell the user. The
work is not ready to document.

Role behavior: **Deshi** explain why each question matters and give an example;
**Rōnin** crisp question plus default; **Kensei** add the second-order risk each
answer creates. All roles ask all six.

## 2. Survey (brownfield)

Summarize what exists, citing file paths:
- dbt (`dbt_project.yml`, `models/`, `sources.yml`, `schema.yml`, `snapshots/`)
- Orchestration (Airflow DAGs, Fabric/ADF pipeline JSON, Databricks jobs, Dagster, Prefect)
- Notebooks, Spark jobs, stored procedures
- IaC (Terraform, Bicep, ARM, CloudFormation) and CI/CD (`.github/workflows`, `azure-pipelines.yml`)
- Semantic layer and BI (`.pbip`, `.tmdl`, LookML, Tableau, metrics YAML)
- Existing READMEs, ADRs, wikis, `SCROLL.md`, `BATTLE_MAP.md`

Record what you observed versus what you assume.

## 3. Interview for gaps

Use [references/discovery-questions.md](references/discovery-questions.md).
Batches of at most 6, grouped, each with a default. If the user says "just go",
proceed on defaults and log each as `A-###`.

## 4. Write the facts file

Start from [assets/project-facts.template.yaml](assets/project-facts.template.yaml).
Fill what you know; leave unknowns `null` with a `Q-###`. Every cost carries
unit x volume x frequency and a `price_date`. Every risk has a `type`
(technical, delivery, security, compliance, void).

## 5. Checkpoint

Show the user: the single action, sources, key NFRs, top decisions, top open
questions. Ask for corrections. Do not let packs be written on an unconfirmed
ground gate unless the user said to proceed.

## Refresh mode

When `docs/architecture/` exists: compare the facts file to the repo and to what
the user says changed. Update the fact, bump `facts_version`, then list every
doc that cites the changed fact so the packs can be updated. Never silently
change a number in one pack only.
