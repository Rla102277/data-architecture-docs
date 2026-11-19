# CLAUDE.md

Role: Rōnin

Read AGENTS.md. Same rules apply to Claude Code.

Skills for this repo are exposed through `.claude/skills -> ../skills`, which
Claude Code and Cursor both read, so opening this repo loads every skill here.

Before committing: `python3 scripts/verify_repo.py` and
`python3 -m unittest discover -s tests`.
