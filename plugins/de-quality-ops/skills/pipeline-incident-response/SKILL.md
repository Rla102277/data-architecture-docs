---
name: pipeline-incident-response
description: >-
  Use when a data pipeline or data product is broken now: failed or silently
  wrong loads, stale dashboards, duplicate or missing data, a bad deploy, a
  source outage. Triage severity, stop the spread, communicate to consumers,
  find the root cause with evidence, fix and backfill safely, and write a
  blameless postmortem with the check that would have caught it.
---

# Pipeline Incident Response

Stop the bleeding, tell people, fix it properly, and make sure it cannot happen
the same way again.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "The dashboard is wrong." "The load failed." "We have duplicates in finance data."

Not for: planned backfills (use `backfill-and-replay`).

## Inspect first

1. **What is the impact right now?** Which data products, which consumers, which
   decisions in the next hours (a board deck, a payroll run, month-end close).
2. **When did it start?** Last known good run and first bad run.
3. **What changed?** Deploys, source changes, schema changes, capacity or
   credential changes, in the window.

## Procedure

1. **Triage** severity ([references/severity.md](references/severity.md)) and
   name an incident lead. One person coordinates; others investigate.
2. **Contain**: stop wrong data spreading. Pause downstream refreshes or
   schedules, mark the data product as stale or under investigation in the BI
   tool or channel, roll back a bad deploy. Do not delete data while investigating.
3. **Communicate** early, then on a schedule: what is affected, what users should
   do (use yesterday's report, hold the decision), next update time. Plain words.
4. **Find the root cause with evidence**: logs, run history, the audit table,
   row counts per layer to find where good became bad, diffs of the code and
   schema. Write down each hypothesis and the evidence for or against.
5. **Fix** the cause, not just the symptom: code fix with a test that reproduces
   the problem, config fix, or source fix through its owner.
6. **Repair the data** with `backfill-and-replay`: scoped, validated, announced.
7. **Close** when data is correct and validated, consumers are told, and monitoring is green.
8. **Postmortem** within a week ([assets/postmortem-template.md](assets/postmortem-template.md)):
   timeline, impact, root cause, why it was not caught, and actions with owners.
   At least one action adds a check or monitor that would have caught it.

## Standards

- **MUST** contain before you fix when wrong numbers are spreading.
- **MUST** communicate impact to consumers, even before the cause is known.
- **MUST NOT** delete, truncate or overwrite production data during an incident
  without explicit approval and a backup or time travel path.
- **MUST** add a test or monitor for every incident's failure mode.
- **SHOULD** keep postmortems blameless: systems and gaps, not people.

## Failure modes

| Failure | Prevention |
|---|---|
| Hot fix makes it worse | Contain first, fix with a reproducing test |
| Consumers act on wrong data during the incident | Early "do not use" message |
| Evidence destroyed by cleanup | No deletes during investigation |
| Same incident repeats next quarter | Postmortem action that adds a check |
| Silent success masked the failure for days | Monitor row counts and audit status, not only job status |

## Verify

- Data validated after repair (counts, totals, reconciliation).
- The new check fails on a replay of the incident's bad data.

## Output

Incident log with timeline and evidence, consumer messages, the fix with its
test, repair validation, and the postmortem.
