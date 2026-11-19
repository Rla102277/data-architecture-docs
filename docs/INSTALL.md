# Install

Pick one path per host. Do not install the same skills for Claude Code and
Cursor in the same project: Cursor also reads `.claude/`, so it would list
everything twice.

## Claude Code

From GitHub, one step (Claude Code 2.1.275 or later):

```
/plugin install data-architecture-docs --marketplace Rla102277/data-architecture-docs
```

Or add the marketplace once and pick plugins:

```bash
claude plugin marketplace add Rla102277/data-architecture-docs
claude plugin install data-architecture-docs@data-architecture-docs
claude plugin install data-warrior@data-architecture-docs                    # optional
claude plugin install gordonmurray-data-engineering@data-architecture-docs   # optional
```

From a local clone: `python3 scripts/install.py claude` (runs the same commands
against your checkout, or prints them if the `claude` CLI is not on your PATH).

The repo is private, so Claude Code needs your GitHub access (`gh auth login`)
to add it from GitHub.

## Cursor

Cursor loads local plugins from `~/.cursor/plugins/local/` and skips symlinks
that point outside it, so the installer copies:

```bash
python3 scripts/install.py cursor                                   # all plugins
python3 scripts/install.py cursor --plugins data-architecture-docs  # just one
```

Then **Developer: Reload Window** and check **Customize** for the plugins.
After `git pull`, run it again to update.

Known Cursor limit: `readonly: true` is not enforced on plugin-shipped agents
today. The reviewers are instructed to be read-only and return text, and the
calling skill writes the files.

## Skills only (one project, Codex, or hosts without plugins)

```bash
python3 scripts/install.py skills --target ~/Documents/projects/code/my-project --tool claude
python3 scripts/install.py skills --target <project> --tool cursor
python3 scripts/install.py skills --global --tool codex
```

Copies every skill into `.claude/skills`, `.cursor/skills` or `.agents/skills`
(flattening the Data Warrior's ring folders), and reviewer agents into
`.claude/agents` or `.cursor/agents`. Codex has no subagent folder, so reviews
there run as one agent applying each persona, and say so.
