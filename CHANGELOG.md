# Changelog

## 1.0.0 (2026-11-19)

Restructured into a plugin marketplace.

- Repo is a Claude Code and Cursor marketplace with three plugins:
  `data-architecture-docs`, `data-warrior`, `gordonmurray-data-engineering`.
- The single skill is split into nine focused skills: `architecture-docs`
  (orchestrator), `project-facts`, `architecture-decision`, `engineer-pack`,
  `director-pack`, `executive-pack`, `data-contracts`,
  `validate-architecture-docs`, `review-architecture-docs`. Each carries its own
  templates; no symlinks.
- Reviewers are read-only subagents: CIO, Director and Lead DE readers, the
  Council lenses, and five specialists from vaquarkhan.
- Shared conventions live in one file and are built into every skill.
- `scripts/install.py` installs for Cursor (local plugin copy), Claude Code
  (marketplace) or skills only (any project, Codex).
- `scripts/build.py --check`, `verify_repo.py`, validator tests and
  `claude plugin validate` run in CI.

## 0.2.0 (2026-11-19)

- Added The Data Warrior ground gate, study-the-wind ADRs, win-the-room brief,
  void risks and roles. Vendored Data Warrior and gordonmurray skills. Added
  vaquarkhan contracts and reviewers.

## 0.1.0 (2026-11-19)

- First version: one skill, persona-tiered templates, facts file, validator.
