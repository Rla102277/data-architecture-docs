# AGENTS.md

Role: Rōnin

Entry point for any coding agent working on this repo.

## What this repo is

The Data Engineering Factory: a Claude Code and Cursor plugin marketplace of
data engineering skills, plus the tooling that builds, verifies and evals them.
First-party plugins are `plugins/de-*` (they have `plugin.meta.json`).
`plugins/data-warrior` and `plugins/gordonmurray-data-engineering` are vendored.
Read README.md, `factory/SKILL_STANDARD.md` and `docs/HOW-IT-WORKS.md`.

## Rules

- **Every first-party skill meets `factory/SKILL_STANDARD.md`**: "Use when"
  description; sections When to use, Inspect first, Procedure, Standards,
  Failure modes, Verify, Output in order; doctrine link; under 500 lines; an
  eval scenario in `evals/scenarios/<plugin>/<skill>.json`.
- **New skills** start from `python3 scripts/new_skill.py`.
- **Job types** live in `plugins/de-factory-line/skills/run-factory-job/assets/job-types.json`;
  every stage's skill must exist (tests enforce it). Never weaken a gate to make a job pass.
- **Never hand-edit vendored plugins.** Change upstream, then
  `python3 scripts/sync_upstream.py <plugin>`.
- **Never hand-edit generated files**: marketplace and plugin manifests,
  `references/doctrine.md`, `references/conventions.md`, `references/skill-standard.md`,
  the skill-factory `assets/*.tmpl`, and `catalog/`. Edit the source and run
  `python3 scripts/build.py`.
- **Scripts** are standard-library Python unless there is no reasonable way
  (sqlglot for lineage). Every script has a test in `tests/`.
- No symlinks. No em dashes in first-party files. Plain, direct voice.
- Keep workplace and client specifics out. Examples and fixtures are fictional.
- Version-sensitive platform facts carry a date and "recheck before citing".
- Roles (Deshi / Rōnin / Kensei) change collaboration style, never permissions.

## Before committing

```bash
python3 scripts/build.py --check
python3 scripts/verify_repo.py
python3 -m unittest discover -s tests
claude plugin validate .
```

Bump `version` in the plugin's `plugin.meta.json` and add a CHANGELOG entry for
any change to a first-party plugin.
