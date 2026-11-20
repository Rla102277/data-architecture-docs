# Data Engineering Factory

**Technical completion is not strategic success.**

A skill factory for data engineers, for Claude Code and Cursor. It ships deep,
opinionated skills for the work data engineers actually do (reverse engineering
legacy systems, SQL, dbt, modeling, pipelines, Fabric, Snowflake, Power BI,
quality and ops, architecture docs) and the machinery to make more of them to
one standard and prove they work. The Data Warrior is the doctrine every skill follows.

```
87 skills in 13 plugins and a job line. 47 first-party, every one built to the same
standard with its own eval scenario. 40 vendored from The Data Warrior and gordonmurray.
```

Browse them all in the [skill catalog](catalog/SKILLS.md).

## Install

**Claude Code**: add the marketplace once, then install the plugins you want:

```bash
claude plugin marketplace add Rla102277/data-architecture-docs
claude plugin install de-reverse-engineering@data-engineering-factory
claude plugin install de-dbt@data-engineering-factory
# ...or any plugin below
```

**Cursor** (local plugin copy; Cursor skips symlinks):

```bash
git clone https://github.com/Rla102277/data-architecture-docs.git ~/Documents/projects/code/data-engineering-factory
cd ~/Documents/projects/code/data-engineering-factory
python3 scripts/install.py cursor                       # everything
python3 scripts/install.py cursor --plugins de-dbt,de-sql
```

Then **Developer: Reload Window**. Skills-only installs for one project or for
Codex: [docs/INSTALL.md](docs/INSTALL.md).

## Plugins

| Plugin | Skills | What it does |
|---|---|---|
| [de-reverse-engineering](plugins/de-reverse-engineering/) | 8 | Understand legacy systems without running them: catalog inventory (SQL Server, Snowflake, Fabric), stored procedure specs, SSIS and ADF/Fabric package analysis, sqlglot lineage, business rules catalog, profiling, legacy-to-dbt migration with parity |
| [de-modernization](plugins/de-modernization/) | 4 | Look at a system and design a whole new way: evidence-based assessment, clean-sheet target options from the decisions the data serves, and a wave-by-wave migration that turns the old system off |
| [de-sql](plugins/de-sql/) | 4 | Style and review, performance tuning from plans, refactoring with parity, testing |
| [de-dbt](plugins/de-dbt/) | 4 | Project setup, models and incrementals, tests and contracts, slim CI and deployment |
| [de-modeling](plugins/de-modeling/) | 2 | Kimball dimensional modeling, Data Vault 2.0 with a hashing standard |
| [de-pipelines](plugins/de-pipelines/) | 3 | Incremental ingestion (CDC, change tracking, watermarks, deletes), backfill and replay, Airflow |
| [de-platforms](plugins/de-platforms/) | 4 | Microsoft Fabric, Snowflake, Power BI semantic models, SQL Server as a source |
| [de-quality-ops](plugins/de-quality-ops/) | 5 | Data quality checks, GL reconciliation, observability, incident response, daily cost and value report |
| [de-architecture-docs](plugins/de-architecture-docs/) | 9 | Persona-tiered design docs (CDO/CIO, Data Director, Lead DE) from one facts file, reviewed by read-only subagents |
| [de-factory-line](plugins/de-factory-line/) | 1 + CLI | Push jobs (reimagine, reverse-engineer, build, migrate, docs, incident) through gated stages: each stage names its skill, artifacts are hashed, tests record real exit codes, reviews go stale when files change, a human approves |
| [de-skill-factory](plugins/de-skill-factory/) | 3 | Create a new skill, upgrade a thin one, eval any skill against a baseline |
| [data-warrior](plugins/data-warrior/) | 31 | The doctrine: ground the decision, study trade-offs, win the room, read the void (vendored from [The-data-warrior-agent](https://github.com/Rla102277/The-data-warrior-agent)) |
| [gordonmurray-data-engineering](plugins/gordonmurray-data-engineering/) | 9 | Iceberg, Paimon, Fluss, Flink, Flink Agents, Iggy, Lance, Firn, Docker Compose (vendored from [gordonmurray/data-engineering-skills](https://github.com/gordonmurray/data-engineering-skills)) |

## Push jobs through the line

Skills say how to do the work; the line makes sure it got done, with proof.

```bash
alias job='python3 ~/.cursor/plugins/local/de-factory-line/skills/run-factory-job/scripts/job.py'
cd ~/Code/<your-repo>
job init
job new reimagine "Replace the SSIS sales warehouse"
job next JOB-0001        # stage, skill to use, files to leave, gate
```

Or in Cursor: "push the reimagine of this system through the factory as a job".
The agent runs each stage with its skill, records tests and reviews, pushes, and
stops at every human gate. `job board` writes `.factory/BOARD.md`.

| Job type | Stages |
|---|---|
| reimagine | ground, understand, assess, options, **choose**, decide, roadmap, docs (test), review, **approve** |
| reverse-engineer | ground, inventory, etl?, lineage, procs?, rules, profile?, map, review, **approve** |
| build | spec, steps?, build, test, review, **approve**, **deploy** |
| migrate | ground, map, build, parity (test), parallel-run (test), review, **approve**, **cutover**, **decommission** |
| docs | ground, decide, packs, validate (test), review, **approve** |
| incident | contain, fix, test, **repair**, postmortem (review), **close** |

Bold = human gate. `?` = optional.

## What makes a skill here

Every first-party skill meets the [skill standard](factory/SKILL_STANDARD.md),
and CI enforces it:

- a description that starts "Use when" in the words engineers type
- **When to use, Inspect first, Procedure, Standards, Failure modes, Verify, Output**, in that order
- real commands, queries and code, with the dialect marked; defaults with reasons
- the Data Warrior doctrine built in: inspect before acting, observed vs assumed,
  smallest reversible change, prove it, never invent, stop for a human on irreversible steps
- an eval scenario that has to beat a no-skill baseline

Tools that ship inside skills are tested in CI: the T-SQL-aware lineage
extractor, the SSIS / ADF / Fabric package analyzer, the profiling SQL
generator and the architecture docs linter.

## Repository layout

```
data-engineering-factory/
+-- .claude-plugin/marketplace.json   # Claude Code marketplace (generated)
+-- .cursor-plugin/marketplace.json   # Cursor marketplace (generated)
+-- marketplace.meta.json             # Source for both marketplace files
+-- plugins/                          # One folder per plugin
|   +-- de-*/                         # First-party: plugin.meta.json, skills/, assets/icon.png
|   +-- de-factory-line/              # The job line: job.py CLI and job types
|   +-- data-warrior/                 # Vendored doctrine, do not edit
|   `-- gordonmurray-data-engineering/ # Vendored, do not edit
+-- factory/
|   +-- SKILL_STANDARD.md             # The bar every skill meets
|   +-- doctrine.md                   # Built into every skill as references/doctrine.md
|   `-- templates/                    # SKILL.md and eval templates
+-- catalog/                          # SKILLS.md and skills.json (generated)
+-- evals/
|   +-- scenarios/<plugin>/<skill>.json
|   +-- fixtures/                     # Sample legacy SQL, SSIS, ADF, bad SQL
|   `-- results/                      # Local eval runs (git-ignored)
+-- scripts/
|   +-- new_skill.py                  # Scaffold a skill and its eval
|   +-- build.py                      # Generate manifests, doctrine copies, catalog
|   +-- verify_repo.py                # Enforce the standard (CI)
|   +-- run_evals.py                  # Run evals with and without plugins
|   +-- sync_upstream.py              # Re-vendor upstream plugins (upstreams.json)
|   `-- install.py                    # Cursor, Claude Code or skills-only install
+-- tests/                            # Tool and linter tests
+-- examples/                         # Fictional worked example
+-- docs/                             # INSTALL, HOW-IT-WORKS
`-- AGENTS.md / CLAUDE.md             # Rules for agents working on this repo
```

## Make a new skill

```bash
python3 scripts/new_skill.py --plugin de-dbt --name dbt-snapshots \
  --trigger "tracking history of mutable source tables with dbt snapshots"
# fill in SKILL.md and evals/scenarios/de-dbt/dbt-snapshots.json, then:
python3 scripts/build.py && python3 scripts/verify_repo.py
python3 scripts/run_evals.py --plugin de-dbt --skill dbt-snapshots
```

Or ask your agent: "make a skill for ..." (the `create-data-skill` skill runs
the interview and does the same steps).

## Develop

```bash
python3 scripts/build.py --check     # generated files current
python3 scripts/verify_repo.py       # the standard, manifests, links, evals
python3 -m unittest discover -s tests
claude plugin validate .             # Claude Code's own validator
python3 scripts/run_evals.py --dry-run
```

## Credits

The Data Warrior doctrine and skills, gordonmurray/data-engineering-skills,
vaquarkhan/data-engineering-agent-skills (contract templates and reviewers) and
MADR. Licenses in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
