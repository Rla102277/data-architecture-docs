# Install

Pick one path per host. Do not install the same skills for Claude Code and
Cursor in the same project: Cursor also reads `.claude/`, so it would list
everything twice.

## Claude Code

```bash
claude plugin marketplace add Rla102277/data-architecture-docs
claude plugin install <plugin>@data-engineering-factory
```

Plugins: `de-reverse-engineering`, `de-sql`, `de-dbt`, `de-modeling`,
`de-pipelines`, `de-platforms`, `de-quality-ops`, `de-architecture-docs`,
`de-skill-factory`, `data-warrior`, `gordonmurray-data-engineering`.

One step, Claude Code 2.1.275 or later:

```
/plugin install de-reverse-engineering --marketplace Rla102277/data-architecture-docs
```

From a local clone: `python3 scripts/install.py claude [--plugins a,b]` runs the
same commands against your checkout, or prints them if `claude` is not on PATH.

The repo is private, so adding it from GitHub needs your GitHub access
(`gh auth login`).

## Cursor

Cursor loads local plugins from `~/.cursor/plugins/local/` and skips symlinks
that point outside it, so the installer copies:

```bash
python3 scripts/install.py cursor                          # all plugins
python3 scripts/install.py cursor --plugins de-dbt,de-sql  # some
```

Then **Developer: Reload Window** and check **Customize**. After `git pull`, run
it again to update.

Known Cursor limit: `readonly: true` is not enforced on plugin-shipped agents.
The reviewer agents are instructed to stay read-only and return text.

## Skills only (one project, Codex, or hosts without plugins)

```bash
python3 scripts/install.py skills --target ~/Documents/projects/code/my-project --tool claude
python3 scripts/install.py skills --target <project> --tool cursor --plugins de-reverse-engineering
python3 scripts/install.py skills --global --tool codex
```

Copies skills into `.claude/skills`, `.cursor/skills` or `.agents/skills`
(flattening the Data Warrior ring folders and giving each Warrior skill a copy of
THE_WAY.md), and reviewer agents into `.claude/agents` or `.cursor/agents`.

## Tool dependencies

- Python 3.10+ for every script (standard library only), except:
- `lineage-extraction` needs `pip install sqlglot`.
- `run_evals.py` needs the Claude Code CLI, signed in.
