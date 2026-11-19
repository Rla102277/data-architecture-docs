# CLAUDE.md

Role: Rōnin

Read AGENTS.md. Same rules apply.

Try a plugin from this checkout without installing:

```bash
claude --plugin-dir plugins/de-reverse-engineering --plugin-dir plugins/data-warrior
```

Before committing: `python3 scripts/build.py --check`,
`python3 scripts/verify_repo.py`, `python3 -m unittest discover -s tests`,
and `claude plugin validate .`.
