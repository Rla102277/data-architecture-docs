# de-architecture-docs (plugin)

Persona-tiered design docs for data platforms, written from one facts file.

Install in Claude Code:

```
/plugin install de-architecture-docs --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: see `docs/INSTALL.md` at the repo root.

```
de-architecture-docs/
+-- .claude-plugin/plugin.json     # Claude Code manifest (generated)
+-- .cursor-plugin/plugin.json     # Cursor manifest (generated)
+-- plugin.meta.json               # Source for both manifests
+-- skills/
|   +-- architecture-docs/         # Orchestrator: scope, flow, shared docs, hand-off
|   +-- project-facts/             # Ground gate, survey, interview, facts file
|   +-- architecture-decision/     # ADRs: options, status quo, steelman, validation test
|   +-- engineer-pack/             # ENG-01..09 for the Lead Data Engineer
|   +-- director-pack/             # DIR-01..06 for the Data Director
|   +-- executive-pack/            # EXE-01..04 for the CDO / CIO
|   +-- data-contracts/            # Source, dataset and metric contracts
|   +-- validate-architecture-docs/ # Docs linter and quality gates
|   `-- review-architecture-docs/  # Runs the reviewer subagents
+-- agents/                        # Read-only reviewer subagents
+-- rules/                         # Cursor rule for docs/architecture/**
+-- assets/icon.png                # Plugin icon
`-- shared/conventions.md          # Canonical conventions, built into every skill
```

## Reviewer subagents

| Agent | Reads | Source |
|---|---|---|
| cio-reader | Executive pack | This repo |
| data-director-reader | Director pack | This repo |
| lead-engineer-reader | Engineer pack and ADRs | This repo |
| council | Whole set, six Data Warrior lenses | This repo, from The Data Warrior |
| data-architect | DIR-01, ENG-01/02, ADRs | vaquarkhan (MIT), front matter added |
| analytics-engineer-reviewer | ENG-02, ENG-05 | vaquarkhan (MIT), front matter added |
| data-platform-reliability-reviewer | DIR-04, ENG-03, ENG-08 | vaquarkhan (MIT), front matter added |
| data-platform-infrastructure-reviewer | ENG-01, ENG-06 | vaquarkhan (MIT), front matter added |
| data-security-and-compliance-auditor | DIR-03, ENG-07 | vaquarkhan (MIT), front matter added |

All reviewers have `tools: Read, Grep, Glob` and return text. The calling skill
writes the review files. Cursor does not currently enforce `readonly: true` on
plugin-shipped agents, so the read-only behavior there relies on the agent's
instructions.

## Editing this plugin

- Change conventions in `shared/conventions.md`, manifests in
  `plugin.meta.json`, then run `python3 scripts/build.py` from the repo root.
- Keep each SKILL.md under 500 lines; push detail into `references/` or `assets/`.
