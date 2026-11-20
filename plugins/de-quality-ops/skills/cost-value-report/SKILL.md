---
name: cost-value-report
description: >-
  Use when reporting what a data platform build is costing (AI tooling, cloud,
  people hours), what it has delivered, and how that compares to contractors or
  additional hires, on a daily or weekly schedule. Produces a dated Markdown
  report and a CSV where every number is labeled measured, allocated or assumed.
---

# Cost and Value Report

Show leadership what the build costs, what it delivered and what the
alternatives would have cost, with every number traceable to its source.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- A daily or weekly cost and value report for a platform build run on the factory line.
- A business case update: factory delivery vs contractors vs an additional hire.
- Answering "what is the AI tooling actually costing us, and per project?"

Not for: cloud cost optimization of running workloads (use `microsoft-fabric-engineering` or `snowflake-engineering`).

## Inspect first

1. `docs/reports/inputs/`: `assumptions.csv`, `time-log.csv`, `baseline-estimates.csv`,
   and the `cursor-usage/` and `azure-cost/` export folders. If missing, run `--init`.
2. `.factory/jobs/*/job.json` for jobs, stages, tests, reviews, approvals and timestamps.
3. `git log` for activity per day.
4. Prior reports in `docs/reports/daily/` for the trend.

## Procedure

1. **Set up once**: `python3 <this-skill-dir>/scripts/cost_report.py --repo . --init`.
   Fill the `value` column of `assumptions.csv` with sources and dates.
2. **Feed it**: log hands-on hours daily in `time-log.csv` (date, job, stage, hours).
   Add a row to `baseline-estimates.csv` when a deliverable ships, with who
   estimated the traditional hours and how. Drop Cursor and Azure CSV exports in
   their folders; overlapping exports are de-duplicated.
3. **Run it**: `python3 <this-skill-dir>/scripts/cost_report.py --repo . --project "<name>"`.
   It writes `docs/reports/daily/<date>.md`, `<date>.csv` and `LATEST.md`.
4. **Schedule it** (macOS): add `--install-launchd --hour 18` to run every day.
   `--uninstall-launchd` stops it. On other systems use cron or Task Scheduler.
5. **Narrate only from the report**: if asked for commentary, read `LATEST.md` and
   its CSV; never restate a number the CSV does not contain.

## Standards

- **MUST** label every number MEASURED, ALLOCATED or ASSUMED, because a savings
  claim without provenance does not survive finance review.
- **MUST** never invent a rate, cost, hour count or baseline; missing inputs show as
  "not provided" and are listed, because a plausible guess becomes a fact once it is in a deck.
- **MUST** show savings as a low to high range, because baselines are estimates.
- **MUST** treat cycle time from job timestamps as calendar time, never as effort.
- **MUST** keep cloud run cost out of the build comparison, because the platform
  runs on it whoever builds it.
- **SHOULD** have a named person own the baselines; flag model-estimated baselines.

## Failure modes

| Failure | Prevention |
|---|---|
| Hours never logged, so savings look infinite | Report lists the missing time log as the top risk |
| Model invents a contractor rate to fill a gap | Script reads rates only from `assumptions.csv`; gaps print "not provided" |
| Cursor cost hidden on days with no hours | Shown as unallocated, called out in caveats |
| Overlapping exports double count | Rows de-duplicated across files |
| Hire comparison ignores the months to hire | Hiring lead and ramp weeks added to calendar time |

## Verify

The day's CSV contains every number in the Markdown report with a label and
source, and Missing inputs is empty or each gap has an owner.

## Output

`docs/reports/daily/<date>.md`, `<date>.csv` and `LATEST.md`, plus a daily
launchd schedule on macOS when requested.
