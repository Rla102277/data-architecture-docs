---
name: create-data-skill
description: >-
  Use when someone wants a new agent skill for a data engineering task: "make a
  skill for X", "turn how we do Y into a skill", "we keep explaining Z to the
  agent". Interviews for the real procedure and failure modes, writes a
  SKILL.md to the factory standard with references, assets or scripts, adds an
  eval scenario, and validates it, in the factory repo or in any project.
---

# Create a Data Skill

Capture how a senior data engineer does a task, so the agent does it that way
every time.

Follow [references/doctrine.md](references/doctrine.md) and
[references/skill-standard.md](references/skill-standard.md).

## When to use

- A repeated data engineering task the agent does generically or wrong.
- A team practice that lives in one person's head.

Not for: deepening an existing thin skill (use `upgrade-data-skill`), or a one-off
task (just do the task).

## Inspect first

1. **Does a skill already exist?** Search the installed skills and the factory
   catalog (`catalog/SKILLS.md` in the factory repo). Extending beats duplicating.
2. **Where will it live?**
   - In the factory repo (`plugins/<plugin>/skills/<name>/`): use the scaffolder.
   - In one project: `.claude/skills/<name>/` (Claude Code and Cursor both read it)
     or `.cursor/skills/<name>/`.
3. **Real material**: an example of the task done well, a past failure, team docs,
   code. A skill written from nothing is generic.

## Procedure

1. **Interview** (one question at a time; offer a draft answer each time):
   1. What is the task, in the user's words? When does it come up?
   2. What does a senior engineer look at before acting?
   3. What are the steps, with the actual commands, queries or files?
   4. What defaults do you always apply, and why?
   5. How does this go wrong? (Ask for the last two times it did.)
   6. How do you prove it worked?
   7. What should be left behind (files, PR, ticket)?
2. **Name it**: kebab-case, verb-noun or noun of the task (`snowflake-cost-review`,
   `ssis-package-retirement`). Unique across installed skills.
3. **Scaffold**:
   - In the factory repo:
     `python3 scripts/new_skill.py --plugin <plugin> --name <name> --trigger "<when>"`
   - Elsewhere: copy [assets/SKILL.md.tmpl](assets/SKILL.md.tmpl) into the skill folder.
4. **Write the SKILL.md** to the standard: description starting with "Use when"
   and naming the terms users type; sections When to use, Inspect first,
   Procedure, Standards, Failure modes, Verify, Output. Real commands and code.
   Detail beyond about 300 lines goes to `references/`; templates to `assets/`;
   deterministic helpers to `scripts/` (standard library Python first, tested).
5. **Write the eval**: from [assets/eval.json.tmpl](assets/eval.json.tmpl), at least
   one realistic prompt with `must_include` behaviors that only appear if the skill
   fired, and `must_not_include` for its failure modes. Factory path:
   `evals/scenarios/<plugin>/<name>.json`.
6. **Validate**: in the factory repo run `python3 scripts/build.py` then
   `python3 scripts/verify_repo.py`. Elsewhere, check front matter, links and line count by hand.
7. **Eval it** with `eval-data-skill`. Ship only if it beats the no-skill baseline.

## Standards

- **MUST** come from real practice: at least one real example or failure.
- **MUST** meet the skill standard's required sections and front matter.
- **MUST** have an eval scenario.
- **SHOULD** stay under 300 lines in SKILL.md; push detail into references.
- **SHOULD** name the better skill under "Not for" so skills route to each other.

## Failure modes

| Failure | Prevention |
|---|---|
| Generic advice that changes nothing | Interview for real steps, defaults and failures |
| Skill never triggers | "Use when" description with the user's words and tool names |
| Duplicate of an existing skill | Catalog search first |
| Untested scripts shipped | Scripts run on a sample before merge |
| Skill nobody can prove works | Eval scenario and baseline comparison |

## Verify

- `verify_repo.py` passes (factory) or the manual checks pass (project).
- The eval beats the baseline (`eval-data-skill`).

## Output

`<skill>/SKILL.md` plus any references, assets and scripts; an eval scenario;
and in the factory repo, a rebuilt catalog.
