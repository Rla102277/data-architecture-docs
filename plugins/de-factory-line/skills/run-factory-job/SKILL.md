---
name: run-factory-job
description: >-
  Use when work should go through the factory line as a tracked job: "start a
  job", "push this through the factory", "reimagine this system as a job",
  "what's the status of JOB-0003", "approve", or any reimagine,
  reverse-engineer, build, migrate, docs or incident work that needs evidence,
  tests, reviews and a human approval gate. Drives job.py: create the job, do
  each stage with its skill, record tests and reviews, push, and stop for a human.
---

# Run a Factory Job

Push a piece of data engineering work through the line, stage by stage, with
evidence a reviewer and an auditor can check, and stop when a human must decide.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Any multi-step data job you want tracked: reimagine a system, reverse engineer
  one, build or change a pipeline, migrate a subject area, write the doc set,
  handle an incident.
- "Where is JOB-0004?" "Push it." "What's next?"

Not for: a quick question or one-file change with no need for evidence (just
use the relevant skill directly).

## Inspect first

1. The CLI is [scripts/job.py](scripts/job.py) in this skill's folder (standard
   library Python 3). Call it with its full path; on the user's Mac that is
   usually `~/.cursor/plugins/local/de-factory-line/skills/run-factory-job/scripts/job.py`.
   The user may have an alias `job`.
2. Is the repo initialized? Look for `.factory/`. If not, run `job.py init` at
   the repo root.
3. Existing jobs: `job.py list` and `job.py board`. Continue an open job rather
   than starting a duplicate.
4. Job types and their stages: `job.py types` (defined in
   [assets/job-types.json](assets/job-types.json)).

## Procedure

1. **Create** the job: `job.py new <type> "<title>"`. Types: `reimagine`,
   `reverse-engineer`, `build`, `migrate`, `docs`, `incident`.
2. **Loop** until a human gate or the end:
   1. `job.py next <ID>`: read the stage, the skill to use, the files it must
      leave, the gate and the note.
   2. Do the stage with that skill. Write the outputs exactly where `next` says.
   3. If the gate is **test**: run the real check through the line, so the exit
      code is recorded: `job.py test <ID> -- <command>` (for example the docs
      linter, `dbt build --select ...`, a parity query runner, `pytest`).
   4. If the gate is **review**: run the reviewer (a reviewer subagent if the
      host has them, otherwise apply the persona yourself) and record it:
      `job.py review <ID> --verdict PASS|CHANGES --by <reviewer> [--file <review.md>] [--independent]`.
      Use `--independent` only when a separate subagent or person did the review.
   5. `job.py push <ID> --note "<what was done>"`. If it refuses, fix what it
      lists (missing output, failed or missing test, stale review) and push again.
   6. Optional stages that do not apply: `job.py skip <ID> --reason "<why>"`.
3. **Stop at every human gate.** `next` prints STOP. Summarize for the user what
   is ready, the evidence (tests, reviews), and the decision needed. Do not
   approve on your own.
4. **Approve only on the user's words**: if, and only if, the user explicitly
   approves in this conversation, run
   `job.py approve <ID> --by "<their name>" --authorized --note "<their words>"`.
   Otherwise tell them the command to run themselves.
5. **Report** with `job.py board` at natural breaks, so the user sees status
   without asking.
6. If blocked (waiting on access, an owner, a decision): `job.py block <ID> --reason "..."`.
   Resume with `unblock`.
7. If the repo keeps its docs somewhere other than the job type's default paths
   (for example `docs/architecture/<product>/`), point the current or a future
   stage at the real paths before doing it:
   `job.py retarget <ID> --stage <stage> --outputs "<glob>" ... --reason "<why>"`.
   Never retarget to dodge a gate; the change is recorded in the job history.

If a Data Warrior skill mentions the Forge CLI (`forge job ...`), use `job.py`
for the same step instead.

## Standards

- **MUST** record tests through `job.py test` so the real exit code and log are
  kept. Never claim a test passed that was not run through the line.
- **MUST NOT** pass `--authorized` without the human's explicit approval in words,
  and **MUST** quote those words in `--note`.
- **MUST NOT** edit `.factory/jobs/*/job.json` or evidence logs by hand.
- **MUST** label reviews honestly: `--independent` only for a separate reviewer.
- **SHOULD** commit `.factory/` with the work, so evidence travels with the code.

## Failure modes

| Failure | Prevention |
|---|---|
| "Tests pass" claimed without running them | Test gate needs a recorded exit code 0 after the stage's latest change |
| Files changed after review slip into approval | Reviews go stale when any covered file changes; approve re-checks |
| Agent approves its own work | Human gate refuses `push`; `approve` needs `--authorized` and the human's words |
| Stages skipped silently | Only optional stages skip, with a recorded reason |
| Status unknown between sessions | State and board live in the repo |

## Verify

- `job.py verify <ID>` shows no changed or missing artifacts and no tampered test logs.
- `job.py board` shows the job at the stage you claim.

## Output

`.factory/jobs/<ID>/job.json` (stages, artifacts with SHA-256, tests, reviews,
approvals, history), `.factory/jobs/<ID>/evidence/` (test logs), and
`.factory/BOARD.md`.
