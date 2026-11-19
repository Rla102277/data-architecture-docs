# data-architecture-docs

A Cursor Agent Skill that turns a data engineering project into a full design
doc set: architecture overview, TDD, ADRs, physical model, pipeline specs, data
contracts, test strategy, CI/CD, security, observability, governance, delivery
plan and cost model. Written three ways, for the **CDO/CIO**, the **Data
Director** and the **Lead Data Engineer**, all driven from one facts file so the
numbers never drift between the exec brief and the TDD.

Works in Cursor and Claude Code (same SKILL.md format).

## Install

Project-level (recommended, the skill travels with the repo):

```bash
mkdir -p .cursor/skills
cp -R data-architecture-docs .cursor/skills/
```

Global (every project on this machine):

```bash
mkdir -p ~/.cursor/skills
cp -R data-architecture-docs ~/.cursor/skills/
```

Claude Code: same folder under `.claude/skills/` or `~/.claude/skills/`. Cursor
also reads `.claude/skills/`, so one copy there covers both.

## Use

In Cursor Agent, type `/data-architecture-docs` or just ask for "architecture
docs and a TDD for this project". For best results paste
[KICKOFF_PROMPT.md](KICKOFF_PROMPT.md) with the brief filled in.

## What you get

```
docs/architecture/
  00-project-facts.yaml      single source of truth
  README.md                  reading guide by persona
  executive/   EXE-01..04    brief, strategic overview, investment + roadmap, risk + governance
  director/    DIR-01..06    solution arch, operating model/RACI, governance, DQ/SLA, delivery, cost/FinOps
  engineer/    ENG-01..09    TDD, physical model, pipeline specs, contracts, tests, CI/CD, security, runbook, standards
               adr/          MADR-style decision records
  shared/                    glossary, traceability matrix, RAID log
```

## Validate

```bash
python3 .cursor/skills/data-architecture-docs/scripts/validate_docs.py docs/architecture
```

Checks for missing docs, front matter, leftover placeholders, undefined IDs,
untagged assumptions, broken mermaid fences, exec word ceilings, em dashes and
filler phrases. Exit code 1 on errors, so it can run in CI.

## Layout

```
SKILL.md                       orchestrator (workflow, rules, length targets)
KICKOFF_PROMPT.md              paste-ready prompt
references/personas.md         who each reader is, voice, format, translation table
references/doc-catalog.md      every doc, purpose, standard ADR list
references/discovery-questions.md  interview bank with defaults
references/stack-profiles.md   Fabric, Snowflake, Databricks, dbt, Airflow, Power BI, Data Vault 2.0
references/diagram-standards.md    Mermaid rules and skeletons
references/quality-gates.md    final checklist incl. persona consistency check
assets/project-facts.template.yaml
templates/{executive,director,engineer,shared}/
scripts/validate_docs.py
```

## Prior art worth knowing

- adr/madr: the ADR format the templates follow.
- fattain-naime/engineering-docs: 22 general software doc skills, installs into Cursor. Good for app projects, no data engineering or persona tiering.
- basvdberg/data-engineering-design-patterns and data-solution-2026: data engineering pattern catalog used with Cursor. Good reference for pattern vocabulary.
- alirezarezvani/claude-skills (senior-data-engineer): a build-focused data engineering skill, not a docs generator.
