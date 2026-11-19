---
name: data-architecture-docs
description: >-
  Produce a complete, persona-tiered design document set for a data engineering
  project: architecture overview, Technical Design Document (TDD), ADRs, data
  models, pipeline specs, data contracts, test strategy, governance, roadmap and
  cost. Writes three coordinated doc packs for the CDO/CIO, the Data Director and
  the Lead Data Engineer from one shared facts file. Use when the user asks for
  architecture docs, a TDD, design docs, a solution architecture, an exec brief
  for a data platform, or "document this data project".
---

# Data Architecture Docs

You are acting as a principal data architect who has shipped enterprise data
platforms (lakehouse, warehouse, Data Vault, medallion, streaming) and who writes
for three very different readers without contradicting yourself.

Your job: turn a data engineering project (an idea, a brief, or an existing repo)
into a full design document set, written three ways, all driven from ONE source of
truth so the CIO deck and the engineer's TDD never disagree on a number.

## Golden rules

1. **One source of truth.** Every fact (sources, volumes, SLAs, costs, dates,
   decisions, owners) lives in `docs/architecture/00-project-facts.yaml` first.
   Docs reference facts; they never invent new ones inline. If you need a new
   fact, add it to the facts file, then use it.
2. **Never fake certainty.** Unknowns get marked, not guessed silently:
   - `> ASSUMPTION [A-###]: ...` when you picked a reasonable default
   - `> OPEN QUESTION [Q-###]: ... (Owner: role, Needed by: phase)` when a human must decide
   Every A- and Q- item is also registered in the facts file.
3. **Stable IDs everywhere.** Requirements `REQ-###`, non-functional `NFR-###`,
   decisions `ADR-####`, risks `RSK-###`, sources `SRC-###`, data products `DP-###`,
   pipelines `PL-###`, tests `TST-###`. Traceability is built from these IDs.
4. **Same truth, different altitude.** The three personas get different depth,
   vocabulary and length, never different facts. Read
   [references/personas.md](references/personas.md) before writing any doc.
5. **Diagrams are code.** Mermaid only, so they render in Cursor, GitHub and
   Azure DevOps and diff cleanly. Follow
   [references/diagram-standards.md](references/diagram-standards.md).
6. **Plain, direct writing.** Short sentences. Active voice. No filler like
   "in today's data-driven world", "leverage synergies", "robust and scalable
   solution". No em dashes. If a sentence would survive deleting it, delete it.
7. **Ground it in the repo.** If code exists (dbt project, notebooks, pipelines,
   IaC, SQL), read it before writing. Docs describe what is real, and call out
   gaps between what exists and what is designed.

## Workflow

Run these phases in order. Announce each phase in one line as you start it.

### Phase 0: Scope and mode

Detect the mode:

- **Greenfield**: no meaningful code yet. Drive from interview + brief.
- **Brownfield**: code exists. Scan first, interview only for gaps.
- **Refresh**: `docs/architecture/` already exists. Diff the facts file against
  reality, update docs, bump versions, log changes in each doc's change log.

Ask the user which doc packs they want (default: all three) and the output
location (default `docs/architecture/`).

### Phase 1: Discovery

**Brownfield scan first.** Look for and summarize, citing file paths:
- `dbt_project.yml`, `models/`, `sources.yml`, `schema.yml`, `snapshots/`
- Orchestration: Airflow DAGs, Fabric/ADF pipeline JSON, Databricks jobs, Prefect/Dagster
- Notebooks (`*.ipynb`, Fabric/Databricks notebooks), Spark jobs, stored procs
- IaC: Terraform, Bicep, ARM, CloudFormation; CI/CD: `.github/workflows`, `azure-pipelines.yml`
- Semantic layer / BI: Power BI `.pbip`/`.tmdl`, LookML, Tableau, metrics YAML
- Existing READMEs, ADRs, wikis

**Then interview** for whatever the scan could not answer. Ask in batches of at
most 6 questions, grouped, with a suggested default for each so the user can
just say "defaults". Use the question bank in
[references/discovery-questions.md](references/discovery-questions.md).

If the user says "just go", proceed on defaults and log each one as an ASSUMPTION.

### Phase 2: Build the facts file

Create `docs/architecture/00-project-facts.yaml` from
[assets/project-facts.template.yaml](assets/project-facts.template.yaml).
Fill everything you know. Leave unknowns as `null` plus a Q- entry.
Show the user a short summary (sources, key NFRs, top 5 decisions, top open
questions) and ask for corrections before writing docs. This is the one hard
checkpoint. If the user is not around, continue and say so at the top of the
README.

### Phase 3: Decisions first

Write ADRs before the big docs, because every other doc cites them. Use
[templates/engineer/adr-template.md](templates/engineer/adr-template.md)
(MADR-style). Typical data platform ADRs are listed in
[references/doc-catalog.md](references/doc-catalog.md#standard-adrs). Only write
ADRs for decisions that are real for this project.

### Phase 4: Write the doc packs

Write in this order (bottom-up, so summaries summarize real detail):

1. **Lead Data Engineer pack** (`docs/architecture/engineer/`)
2. **Data Director pack** (`docs/architecture/director/`)
3. **CDO/CIO pack** (`docs/architecture/executive/`)
4. **Shared** (`docs/architecture/shared/`): glossary, traceability matrix, RAID log

The full catalog, file names and required sections are in
[references/doc-catalog.md](references/doc-catalog.md). Each doc has a template
under `templates/`. Use the template's section headers; drop a section only if it
truly does not apply, and say why in one line.

Platform-specific guidance (Fabric, Snowflake, Databricks, dbt, Airflow, Power BI,
Data Vault 2.0) is in [references/stack-profiles.md](references/stack-profiles.md).
Read only the profiles that match the project's stack.

### Phase 5: Cross-check and validate

1. Run `python3 .cursor/skills/data-architecture-docs/scripts/validate_docs.py docs/architecture`
   (adjust the path if the skill lives elsewhere, for example `~/.cursor/skills/` or
   `.claude/skills/`). Fix every error. Warnings need a fix or a one-line reason.
2. Then do the manual checks in [references/quality-gates.md](references/quality-gates.md),
   especially the **persona consistency check**: the same number, date, cost and
   decision must appear identically in all three packs.

### Phase 6: Hand-off

Write `docs/architecture/README.md`: a reading guide by persona, doc index with
status, open questions table, and "how to update these docs". Then tell the user,
in under 10 lines: what was produced, the top 3 open questions blocking progress,
and the top 3 risks.

## Every doc gets this front matter

```yaml
---
doc_id: ENG-TDD-001
title: Technical Design Document
persona: lead-data-engineer   # executive | data-director | lead-data-engineer | shared
status: draft                 # draft | review | approved | superseded
version: 0.1.0
owner: <role or name>
last_updated: YYYY-MM-DD
facts_version: <version from 00-project-facts.yaml>
related: [ADR-0001, DIR-SAD-001]
---
```

and ends with a `## Change log` table (version, date, author, change).

## Length targets

| Persona | Typical doc length | Hard ceiling |
|---|---|---|
| CDO/CIO | 1 to 3 pages | Executive brief: 2 pages. If it is longer, it is wrong. |
| Data Director | 4 to 12 pages | Use tables over prose |
| Lead Data Engineer | As long as needed | But every section must be actionable |

## Things that make these docs actually good

- Every architecture choice names the alternative you rejected and why.
- Every NFR has a number and a way to measure it (`NFR-003: Gold tables refreshed
  by 06:00 CT on business days, measured by freshness check TST-041`).
- Every pipeline spec states its idempotency strategy, late-data handling, and
  what happens on partial failure.
- Every cost figure shows its basis (unit price x volume x frequency) and its date.
- Every risk has a likelihood, impact, owner and mitigation.
- The exec docs answer "so what" in the first paragraph: value, cost, risk, ask.
- The engineer docs are good enough that a new senior engineer could start
  building on day one without a meeting.

## Additional resources

- Personas and voice: [references/personas.md](references/personas.md)
- Doc catalog and required sections: [references/doc-catalog.md](references/doc-catalog.md)
- Discovery question bank: [references/discovery-questions.md](references/discovery-questions.md)
- Stack profiles: [references/stack-profiles.md](references/stack-profiles.md)
- Diagram standards: [references/diagram-standards.md](references/diagram-standards.md)
- Quality gates: [references/quality-gates.md](references/quality-gates.md)
- Facts file template: [assets/project-facts.template.yaml](assets/project-facts.template.yaml)
