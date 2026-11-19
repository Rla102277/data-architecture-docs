# Data Architecture Docs

**Technical completion is not strategic success.**

A skills toolkit for data engineering architecture work in Cursor, Claude Code
and Codex. The core skill, `data-architecture-docs`, turns a data project into a
full design doc set (architecture overview, TDD, ADRs, data model, pipeline
specs, contracts, test strategy, CI/CD, security, runbook, governance, delivery
plan, cost model) written three ways:

| Persona | Gets | Reads it for |
|---|---|---|
| **CDO / CIO** | 4 short docs, brief first | Fund it, sequence it, accept the risk, or stop |
| **Data Director** | 6 docs, tables over prose | Scope, team, governance, SLAs, cost |
| **Lead Data Engineer** | 9 docs plus ADRs | Build it without a meeting |

All three packs come from one facts file, so the CIO brief and the TDD never
disagree on a number. Nothing gets written until the **ground gate** (from The
Data Warrior) is filled: the decision, the outcome, the owner, what would prove
us wrong, and the single action in one sentence.

## Repository layout

```
data-architecture-docs/
+-- skills/                     # Everything an agent loads
|   +-- data-architecture-docs/ # Core skill: persona-tiered doc set from one facts file
|   |   +-- SKILL.md            # Orchestrator: ground gate, phases, rules, length targets
|   |   +-- KICKOFF_PROMPT.md   # Paste-ready prompt with project brief
|   |   +-- references/         # Personas, doc catalog, discovery, stack profiles, diagrams, gates
|   |   +-- templates/          # Doc templates by pack (executive, director, engineer, shared)
|   |   +-- assets/             # project-facts.template.yaml
|   |   +-- reviewers -> ../../agents
|   |   `-- scripts/            # validate_docs.py (docs linter, CI-ready)
|   +-- data-warrior/           # The Data Warrior: 31 skills by ring (vendored, synced)
|   `-- gordonmurray/           # Iceberg, Paimon, Fluss, Flink, Iggy, Lance, Firn, Compose (vendored)
+-- agents/                     # Review personas: CIO / Director / Lead DE readers, Council, specialists
+-- templates/                  # Shared YAML templates
|   +-- contracts/              # Source, dataset, metric contracts
|   `-- plans/                  # Backfill, schema change, release gate evidence
+-- examples/                   # Fictional worked example (brief, facts, exec brief, review)
+-- scripts/                    # install.sh, sync-upstream.sh, verify_repo.py
+-- tests/                      # Validator unit tests
+-- .claude/skills -> ../skills # Opening this repo loads every skill (Claude Code + Cursor)
+-- .cursor/rules/              # Rule that routes docs/architecture/ work to the skill
+-- .github/workflows/          # Verify, test, install smoke test
+-- AGENTS.md                   # Entry point for any agent working in this repo
+-- CLAUDE.md                   # Claude Code entry point
`-- THIRD_PARTY_NOTICES.md      # Upstream sources and licenses
```

## What the skill produces

```
docs/architecture/
+-- 00-project-facts.yaml   # Single source of truth, ground gate first
+-- README.md               # Single action, reading guide by persona, index, open questions
+-- executive/              # EXE-01..04: brief, strategic overview, investment + roadmap, risk
+-- director/               # DIR-01..06: solution arch, RACI, governance, DQ/SLA, delivery, cost
+-- engineer/               # ENG-01..09: TDD, data model, pipelines, tests, CI/CD, security, runbook
|   +-- adr/                # Decision records: options, status quo, steelman, validation test
|   `-- ENG-04-data-contracts/  # Source / dataset / metric contract YAML
+-- reviews/                # Reader, specialist and Council verdicts
`-- shared/                 # Glossary, traceability matrix, RAID log (with void risks)
```

## Install

Clone once, then install into a project or your user profile.

```bash
git clone https://github.com/Rla102277/data-architecture-docs.git
cd data-architecture-docs

# One project (works in Claude Code AND Cursor):
scripts/install.sh --target ~/Documents/projects/code/my-data-project

# Everywhere on this machine, linked so `git pull` keeps it current:
scripts/install.sh --global --symlink

# Cursor-only folder, just the docs skill:
scripts/install.sh --tool cursor --target <project> --skills docs
```

`--skills` takes `all` (default) or any of `docs,warrior,gordonmurray`.
`--tool` takes `claude` (default, `.claude/skills`, read by Claude Code and
Cursor), `cursor` (`.cursor/skills`) or `codex` (`.agents/skills`). Install for
one of claude or cursor, not both, or Cursor lists every skill twice.

## Use

In Cursor Agent or Claude Code, type `/data-architecture-docs` or ask for
"architecture docs and a TDD for this project". For best results paste
[KICKOFF_PROMPT.md](skills/data-architecture-docs/KICKOFF_PROMPT.md) with the
brief filled in. The skill runs:

1. **Ground gate**, one question per turn: decision, outcome, terrain, falsifiers, owner, single action
2. **Discovery**: survey the repo, then batched questions with defaults
3. **Facts file** checkpoint: you correct it before any doc is written
4. **ADRs first**, study-the-wind style
5. **Packs bottom-up**: engineer, director, executive, shared
6. **Validate**: linter, persona consistency check, wind patterns
7. **Review**: reader personas, specialists, Council lenses, honest about independence
8. **Hand-off**: single action, open questions, top risks

If the target repo has `Role: Deshi | Rōnin | Kensei` in its `AGENTS.md`, the
skill teaches, acts or anticipates accordingly. Roles never grant permissions.

## Companion skills

| Set | Use it for |
|---|---|
| **The Data Warrior** (`skills/data-warrior/`) | Grounding before building (`know-the-ground`), architecture trade-offs (`study-the-wind`), decision asks (`win-the-room`), politics and incentives (`void-sight`), contracts, pipelines, testing, failure patterns. The Forge CLI lives upstream. |
| **gordonmurray** (`skills/gordonmurray/`) | Deep, dated guidance for Iceberg, Paimon, Fluss, Flink, Flink Agents, Iggy, Lance, Firn and Docker Compose |
| **Review personas** (`agents/`) | CIO, Director and Lead DE readers; the Council's six lenses; vaquarkhan's architect, analytics engineer, reliability, infrastructure and security reviewers |

Vendored sets stay canonical upstream. To update:

```bash
scripts/sync-upstream.sh               # all
scripts/sync-upstream.sh data-warrior  # one
```

Add another upstream by adding a line to `scripts/upstreams.conf`.

## Validate

```bash
python3 skills/data-architecture-docs/scripts/validate_docs.py docs/architecture  # a doc set
python3 scripts/verify_repo.py                                                     # this repo
python3 -m unittest discover -s tests                                              # validator tests
```

The doc validator fails on missing docs, an empty ground gate, missing front
matter, leftover placeholders, undefined IDs, untagged assumptions, broken
Mermaid fences, exec docs over their word ceiling and reviews without a verdict.
It warns on em dashes, filler phrases, missing reviews and self-set approvals.

## Credits

Built on ideas and files from
[The Data Warrior](https://github.com/Rla102277/The-data-warrior-agent),
[gordonmurray/data-engineering-skills](https://github.com/gordonmurray/data-engineering-skills),
[vaquarkhan/data-engineering-agent-skills](https://github.com/vaquarkhan/data-engineering-agent-skills)
and [MADR](https://github.com/adr/madr). Licenses in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
