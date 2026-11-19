# Skill Standard

Every first-party skill in this factory meets this standard. `scripts/verify_repo.py`
enforces the parts a machine can check. A copy ships inside the skill-factory
skills as `references/skill-standard.md` (built by `scripts/build.py`).

## Why a standard

A thin skill ("follow best practices for pipelines") does not change what an
agent does. A good skill changes behavior on the task it names: it inspects
before acting, applies opinionated defaults a senior engineer would apply,
refuses the known failure modes, and proves its output. The test of a skill is
an eval where the agent with the skill beats the agent without it.

## Folder

```
<skill-name>/
+-- SKILL.md          # Required. Under 500 lines.
+-- references/       # Detail loaded on demand (one level deep from SKILL.md)
+-- assets/           # Templates, query files, YAML the skill fills in
`-- scripts/          # Deterministic helpers (standard library Python first)
```

Nothing else in the folder. `references/doctrine.md` is generated: do not edit it.

## Front matter

```yaml
---
name: kebab-case-name          # equals the folder name, unique across all plugins
description: >-
  Use when <the situation, in the user's words>. <What it produces>.
  <Key terms a user might type: tools, patterns, file types>.
---
```

- `description` starts with **"Use when"** and says when to trigger, not what
  the skill "is". Under 1024 characters. Name the tools and terms people type.

## Required sections, in order

| Section | Holds |
|---|---|
| `# Title` | One line on the job this skill does |
| `## When to use` | Triggers, and when NOT to use (point to the better skill) |
| `## Inspect first` | What to read or query before acting. Never act on an unread system |
| `## Procedure` | Numbered steps. Commands, queries and file paths, not adjectives |
| `## Standards` | Opinionated defaults with the reason for each. MUST / SHOULD / MAY |
| `## Failure modes` | The specific ways this goes wrong, and how the procedure prevents each |
| `## Verify` | How to prove the output is right: queries, tests, parity checks, exit codes |
| `## Output` | Exactly what files or artifacts the skill leaves behind |

Optional after Output: `## Platform notes`, `## Resources`.

## Writing

- Specific beats general. "Merge on `order_line_id`; filter `updated_at >
  max(updated_at) - interval '3 days'` to catch late rows" beats "handle late data".
- Every default has a reason. Every rule a senior engineer would break has the
  exception named.
- Show code: SQL, YAML, Python, CLI. Mark the dialect.
- Version-sensitive facts carry a date and "recheck before citing".
- No em dashes, no vendor-brochure words, no filler.
- Distinguish observed (cite the file or query), assumed, and decided.

## Evals

Every skill has at least one scenario in `evals/scenarios/<plugin>/<skill>.json`:
a realistic prompt, and the behaviors that prove the skill fired (must include,
must not include). `scripts/run_evals.py` runs it with and without the plugin.
A skill that does not beat the baseline gets rewritten, not shipped.

## Doctrine

Every skill inherits The Data Warrior doctrine (`references/doctrine.md`):
ground the decision before the build, smallest reversible change, prove with
real tests, never invent evidence, stop for a human on irreversible steps.
