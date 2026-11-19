# Data Architecture Docs

**Technical completion is not strategic success.**

A plugin marketplace for data engineering architecture work in Claude Code and
Cursor. The core plugin turns a data project into a full design doc set,
written three ways from one facts file, so the CIO brief and the engineer's TDD
never disagree on a number:

| Reader | Gets | Reads it to |
|---|---|---|
| **CDO / CIO** | 4 short docs, a 2-page brief first | Fund it, sequence it, accept the risk, or stop |
| **Data Director** | 6 docs, tables over prose | Own scope, team, governance, SLAs and cost |
| **Lead Data Engineer** | 9 docs plus ADRs and contracts | Build it without a meeting |

Nothing gets written until the **ground gate** is filled: the decision, the
outcome, the owner, what would prove us wrong, and the single action in one
sentence. Then read-only reviewer subagents check each pack the way its real
reader will.

## Install

**Claude Code** (one step):

```
/plugin install data-architecture-docs --marketplace Rla102277/data-architecture-docs
```

**Cursor** (local plugin copy; Cursor skips symlinks):

```bash
git clone https://github.com/Rla102277/data-architecture-docs.git ~/Documents/projects/code/data-architecture-docs
cd ~/Documents/projects/code/data-architecture-docs
python3 scripts/install.py cursor
```

Then **Developer: Reload Window**. Other options (one project, Codex, picking
plugins) are in [docs/INSTALL.md](docs/INSTALL.md).

## Use

Type `/architecture-docs`, or ask for "architecture docs and a TDD for this
project". For the best first run, paste the
[kickoff prompt](plugins/data-architecture-docs/skills/architecture-docs/KICKOFF_PROMPT.md)
with the brief filled in. How the flow works: [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md).

## Plugins

| Plugin | What it gives you | Source |
|---|---|---|
| [data-architecture-docs](plugins/data-architecture-docs/) | 9 skills and 9 reviewer subagents for the persona-tiered doc set | This repo |
| [data-warrior](plugins/data-warrior/) | 31 Data Warrior skills: ground the decision, study trade-offs, win the room, read the void | [The-data-warrior-agent](https://github.com/Rla102277/The-data-warrior-agent), synced |
| [gordonmurray-data-engineering](plugins/gordonmurray-data-engineering/) | Dated expert skills for Iceberg, Paimon, Fluss, Flink, Flink Agents, Iggy, Lance, Firn, Docker Compose | [gordonmurray/data-engineering-skills](https://github.com/gordonmurray/data-engineering-skills), synced |

Each installs on its own. The core plugin uses the others when they are present
and never requires them.

## Repository layout

```
data-architecture-docs/
+-- .claude-plugin/marketplace.json   # Claude Code marketplace (generated)
+-- .cursor-plugin/marketplace.json   # Cursor marketplace (generated)
+-- marketplace.meta.json             # Source for both marketplace files
+-- plugins/
|   +-- data-architecture-docs/       # First-party plugin
|   |   +-- skills/                   # architecture-docs (orchestrator), project-facts,
|   |   |                             #   architecture-decision, engineer-pack, director-pack,
|   |   |                             #   executive-pack, data-contracts, validate-, review-
|   |   +-- agents/                   # 9 read-only reviewer subagents
|   |   +-- rules/                    # Cursor rule for docs/architecture/**
|   |   +-- shared/conventions.md     # Canonical conventions, built into every skill
|   |   `-- plugin.meta.json          # Source for both plugin manifests
|   +-- data-warrior/                 # Vendored from upstream, do not edit
|   `-- gordonmurray-data-engineering/ # Vendored from upstream, do not edit
+-- examples/                         # Fictional worked example
+-- docs/                             # INSTALL, HOW-IT-WORKS
+-- scripts/
|   +-- install.py                    # Cursor, Claude Code or skills-only install
|   +-- build.py                      # Generate manifests and conventions copies
|   +-- sync_upstream.py              # Re-vendor upstream plugins (upstreams.json)
|   `-- verify_repo.py                # Structural checks, run in CI
+-- tests/                            # Docs linter tests
+-- .github/workflows/validate.yml    # Build check, verify, tests, install smoke tests
+-- AGENTS.md / CLAUDE.md             # Rules for agents working on this repo
+-- CHANGELOG.md
`-- THIRD_PARTY_NOTICES.md
```

## Develop

```bash
python3 scripts/build.py            # after editing conventions or *.meta.json
python3 scripts/verify_repo.py      # structure, names, links, manifests
python3 -m unittest discover -s tests
python3 scripts/sync_upstream.py    # pull upstream plugin changes
claude plugin validate .            # Claude Code's own validator
claude --plugin-dir plugins/data-architecture-docs   # try the plugin locally
```

## Credits

Built on ideas and files from
[The Data Warrior](https://github.com/Rla102277/The-data-warrior-agent),
[gordonmurray/data-engineering-skills](https://github.com/gordonmurray/data-engineering-skills),
[vaquarkhan/data-engineering-agent-skills](https://github.com/vaquarkhan/data-engineering-agent-skills)
and [MADR](https://github.com/adr/madr). Licenses in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
