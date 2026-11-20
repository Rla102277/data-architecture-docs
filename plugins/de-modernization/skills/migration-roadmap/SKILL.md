---
name: migration-roadmap
description: >-
  Use when a target data architecture is chosen and the move must be planned:
  waves by data product and consumer (strangler pattern), a small first wave
  that proves the pattern, parallel runs and parity gates, cutover and
  rollback per wave, decommissioning legacy objects with evidence, capacity
  and dependencies, and kill criteria.
---

# Migration Roadmap

Move from the old system to the new one in waves people can trust, and actually
turn the old one off.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Phase 5 of `reimagine-data-system`.
- "We picked the target. How do we get there without breaking month end?"

Not for: rebuilding one subject area's logic (use `legacy-to-dbt-migration`
inside each wave).

## Inspect first

1. The recommended target and its dispositions (what is rebuilt, replaced, retired).
2. Lineage: which consumers depend on which legacy objects.
3. The business calendar: month-end and quarter-end close, peak seasons, audits.
4. Team capacity and other commitments.

## Procedure

1. **Slice by consumer value**, not by legacy object: a wave delivers one or
   more data products end to end and lets specific legacy objects retire.
2. **Pick wave 1** to prove the pattern: valuable to a visible consumer, small,
   low regulatory risk, exercises the full path (ingest, model, test, serve).
3. **Per wave** ([assets/roadmap-template.md](assets/roadmap-template.md)):
   scope, data products, legacy objects retired, dependencies, effort vs
   capacity, parity tests, parallel-run length (including a month end for
   finance data), cutover steps, rollback steps, exit criteria, owner sign-off.
4. **Foundation work** goes before or inside wave 1 only as far as wave 1 needs
   it (environments, CI/CD, security, monitoring). No year-long foundation phase.
5. **Decommission** as part of each wave: disable, wait an agreed period, archive,
   then remove, each step approved. Track license and infrastructure savings.
6. **Kill criteria**: what result would stop or reshape the program (parity not
   reached after N weeks, cost overrun beyond X, adoption below Y).
7. **Timeline**: a Mermaid gantt by wave with the business calendar marked.

## Standards

- **MUST** run old and new in parallel with parity checks before each cutover.
- **MUST** have a tested rollback for every cutover.
- **MUST** get owner approval before disabling or removing any legacy object.
- **SHOULD** deliver visible value within the first 90 days.
- **SHOULD** avoid cutovers during close, audits or peak season.

## Failure modes

| Failure | Prevention |
|---|---|
| Two systems run forever because nothing is turned off | Decommission is part of every wave's exit criteria |
| Year one spent on "foundation" with nothing to show | Foundation only as far as the next wave needs |
| Cutover at month end breaks finance | Business calendar on the plan |
| Program continues past the point it should stop | Kill criteria agreed up front |
| Plan assumes people the team does not have | Effort vs capacity per wave |

## Verify

- Every legacy object with a rebuild, replace or retire disposition belongs to a wave.
- Every wave has parity tests, rollback steps, exit criteria and an owner.
- Wave 1 delivers a named data product to a named consumer.

## Output

`docs/reimagine/04-roadmap.md`, which also feeds the delivery plan (DIR-05) and
investment and roadmap (EXE-03) in the architecture doc set.
