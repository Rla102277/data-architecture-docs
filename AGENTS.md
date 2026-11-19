# AGENTS.md

Role: Rōnin

Entry point for any coding agent working on this repo.

## What this repo is

A plugin marketplace. `plugins/data-architecture-docs/` is first-party.
`plugins/data-warrior/` and `plugins/gordonmurray-data-engineering/` are
vendored from upstream. See README.md for the layout and docs/HOW-IT-WORKS.md
for the flow.

## Rules

- **Never hand-edit vendored plugins.** Change upstream, then
  `python3 scripts/sync_upstream.py <plugin>`.
- **Never hand-edit generated files**: both `marketplace.json`, both first-party
  `plugin.json`, and every `references/conventions.md`. Edit the source
  (`marketplace.meta.json`, `plugin.meta.json`, `shared/conventions.md`) and run
  `python3 scripts/build.py`.
- No symlinks anywhere. Hosts skip or mishandle them.
- Each skill is self-contained: its own `references/` and `assets/`, links one
  level deep, SKILL.md under 500 lines, description says when to use it.
- Reviewer agents stay read-only (`tools: Read, Grep, Glob`) and return text.
- No em dashes in first-party files. Plain, direct voice.
- Keep workplace and client specifics out. Examples are fictional.
- Roles (Deshi / Rōnin / Kensei) change collaboration style, never permissions.

## Before committing

```bash
python3 scripts/build.py --check
python3 scripts/verify_repo.py
python3 -m unittest discover -s tests
claude plugin validate .        # if the Claude Code CLI is installed
```

Bump `version` in `plugin.meta.json` and add a CHANGELOG entry for any change
to the first-party plugin.
