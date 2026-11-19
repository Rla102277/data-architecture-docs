# AGENTS.md

Role: Rōnin

Entry point for any coding agent (Cursor, Claude Code, Codex) working in this repo.

## What this repo is
A skills toolkit for data engineering architecture work. The first-party skill is
`skills/data-architecture-docs/`: it produces a persona-tiered design doc set
(CDO/CIO, Data Director, Lead Data Engineer) from one facts file. It ships with
vendored companion skills from The Data Warrior and gordonmurray, and review
personas in `agents/`.

## Rules for working here
- First-party code: `skills/data-architecture-docs/`, `agents/` (except the five
  vaquarkhan files), `scripts/`, `tests/`, `examples/`, root docs.
- **Never hand-edit vendored folders** (`skills/data-warrior/`, `skills/gordonmurray/`)
  or the vaquarkhan files in `agents/` and `templates/`. Change upstream, then run
  `scripts/sync-upstream.sh`.
- Keep `skills/data-architecture-docs/SKILL.md` under 500 lines. Put detail in
  `references/` and link one level deep.
- No em dashes in first-party files. Plain, direct voice.
- Keep workplace or client specifics out of this repo. Examples are fictional.
- Before committing: `python3 scripts/verify_repo.py` and
  `python3 -m unittest discover -s tests` must pass.
- Roles (Deshi / Rōnin / Kensei) change collaboration style, never permissions.

## Layout
See README.md.
