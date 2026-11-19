---
name: eval-data-skill
description: >-
  Use when you need to prove a skill or plugin changes agent behavior: run
  scenario prompts with and without the plugin, grade transcripts against
  must-include and must-not-include behaviors, compare to a baseline, and
  report which skills earn their place. Uses the factory's run_evals.py with
  the Claude Code CLI in headless mode.
---

# Eval a Data Skill

A skill is only as good as the difference it makes. Measure the difference.

Follow [references/doctrine.md](references/doctrine.md) and
[references/skill-standard.md](references/skill-standard.md).

## When to use

- Before shipping a new or upgraded skill.
- Periodically, to catch skills that model upgrades made redundant or broke.

Not for: testing data pipelines (use `sql-testing` or `dbt-testing-and-contracts`).

## Inspect first

1. Scenarios exist: `evals/scenarios/<plugin>/<skill>.json` (factory repo).
2. The Claude Code CLI is installed and signed in (`claude --version`); headless
   runs use `claude -p`. Evals spend model usage: say roughly how many runs
   (scenarios x 2 for baseline) before starting.
3. Fixtures the scenarios need are present (small sample repos or SQL files).

## Procedure

1. **List** what would run, without running it:
   ```bash
   python3 scripts/run_evals.py --plugin de-reverse-engineering --dry-run
   ```
2. **Run** with a baseline:
   ```bash
   python3 scripts/run_evals.py --plugin de-reverse-engineering --skill lineage-extraction
   ```
   Each scenario runs twice: with `--plugin-dir plugins/<plugin>` and without.
   The agent gets read-only tools; fixtures are copied into a temporary folder.
3. **Read the report** (`evals/results/<timestamp>.md` and `.json`): score per run
   = share of `must_include` patterns found, minus a penalty for each
   `must_not_include` hit; and the lift over baseline.
4. **Read transcripts** for failures. A regex grade is a screen, not a verdict:
   confirm by reading what the agent did.
5. **Act**: lift at or below zero means the skill is not changing behavior. Fix
   the description (if it did not trigger) or the body (if it triggered but did
   not help) with `upgrade-data-skill`.

## Standards

- **MUST** compare against a no-skill baseline. Absolute scores mean little.
- **MUST** read failing transcripts before concluding.
- **MUST** keep must-include patterns about behavior unique to the skill (a
  specific check, file, query or step), not words any answer would contain.
- **SHOULD** run each scenario more than once when results are close; model
  output varies.
- **SHOULD** keep scenarios realistic: the words a data engineer would actually type.

## Failure modes

| Failure | Prevention |
|---|---|
| Patterns so generic the baseline passes too | Patterns tied to skill-specific behavior; baseline comparison exposes it |
| Single noisy run decides a ship | Repeat close calls |
| Regex passes while the answer is wrong | Read transcripts |
| Evals cost more than expected | Dry run and run count stated first |

## Verify

The report shows, per scenario, both runs' scores and the lift, with
transcripts saved next to it.

## Output

`evals/results/<timestamp>.md`, `.json`, and `transcripts/`.
