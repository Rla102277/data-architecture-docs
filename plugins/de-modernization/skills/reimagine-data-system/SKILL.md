---
name: reimagine-data-system
description: >-
  Use when someone wants to look at an existing data system and come up with a
  whole new way to do it: modernize, re-architect, re-platform or replace a
  legacy warehouse, ETL estate, reporting stack or data platform. Runs the full
  pass from evidence to decision: reverse engineer, assess the current state,
  design clean-sheet target options from the decisions the system serves,
  choose with ADRs, plan the move in waves, and produce the persona doc set.
---

# Reimagine a Data System

Understand what exists, then design what should exist, as if starting today,
and show how to get there without breaking the business on the way.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "Look at this system and come up with a whole new way."
- "We're moving off the old SQL Server / SSIS estate. What should replace it?"
- "Our reporting stack is a mess. Design the future state and the plan."

Not for: only understanding a system (use `reverse-engineer-data-system`), or
documenting a design that is already chosen (use `architecture-docs`).

## Inspect first

1. **The ground gate.** What decisions should the data serve better than today?
   Who owns the outcome? What would prove the new way wrong early? What is the
   single action in one sentence? Use `project-facts` (or Data Warrior
   `know-the-ground`). A redesign without this becomes a tool shopping trip.
2. **Terrain.** Non-negotiables: budget, team size and skills, deadlines and
   forcing events (license end, hardware end of life, audit), platforms already
   owned, compliance.
3. **Existing evidence.** `docs/reverse-engineering/` if a pass was done; if not,
   step 1 below creates it.

## Procedure

Announce each phase in one line. Each uses a focused skill.

| Phase | Do | Skill | Output |
|---|---|---|---|
| 1 Understand | Reverse engineer at triage depth across the whole estate, deep only on the top 20 percent | `reverse-engineer-data-system` | `docs/reverse-engineering/` |
| 2 Assess | Score fitness, gather pain from people, classify every object keep / rebuild / replace / retire | `current-state-assessment` | `docs/reimagine/01-assessment.md` |
| 3 Reimagine | Design from decisions and consumers backward; 3 real options plus status quo; recommend | `target-state-options` | `docs/reimagine/02-options.md`, `03-target-architecture.md` |
| 4 Decide | One ADR per real decision in the recommended option | `architecture-decision` | `docs/architecture/engineer/adr/` |
| 5 Plan the move | Waves, first wave that proves the pattern, parity, cutover, decommission | `migration-roadmap` | `docs/reimagine/04-roadmap.md` |
| 6 Document and sell | Persona doc set of the target, with the roadmap as the delivery plan | `architecture-docs` | `docs/architecture/` |
| 7 Review | Reader, specialist and Council reviewer subagents | `review-architecture-docs` | `docs/architecture/reviews/` |

**Checkpoint after phase 3.** Show the user the options table and the
recommendation before writing ADRs and the roadmap. The choice is theirs.

**The clean-sheet rule.** In phase 3, the legacy system is evidence (sources,
rules, volumes, pains), not a blueprint. Start from the decisions and data
products people need, then design the simplest platform that serves them.
Anything in the old system that serves no current decision goes on the retire
list, not into the new design.

## Standards

- **MUST** complete the ground gate before designing anything.
- **MUST** base the assessment on evidence (inventory, usage, profiles, people),
  and label opinion as opinion.
- **MUST** present at least three genuinely different options plus the status
  quo, and steelman the ones not recommended.
- **MUST** carry every confirmed business rule into the new design or onto an
  owner-approved retire list. Rules do not disappear by accident.
- **MUST** plan for parallel run and parity before any consumer switches.
- **SHOULD** make the first wave small, valuable and reversible: it proves the
  pattern and earns trust for the rest.
- **SHOULD** name what the new way removes (jobs, tools, licenses, manual work),
  with the saving, as plainly as what it adds.

## Failure modes

| Failure | Prevention |
|---|---|
| Lift and shift dressed up as modernization | Clean-sheet rule; options must differ in design, not just platform |
| Tool chosen first, problem fitted to it | Ground gate and decision-backward design |
| Big-bang migration that stalls in year two | Waves, a small first wave, kill criteria |
| Business rules lost in the rebuild | Rules catalog carried into the design or retired by an owner |
| Team cannot operate the new platform | "Can this team run it" scored in every option |
| Beautiful target nobody funds | Executive pack in the win-the-room shape, with what it removes and saves |

## Verify

- Every object in the inventory has a disposition (keep, rebuild, replace, retire).
- Every confirmed rule maps to a target component or an approved retirement.
- Each option has a score, a cost basis and a steelman.
- The first wave has exit criteria and a parity test.
- `validate-architecture-docs` exits 0 on the final doc set.

## Output

```
docs/reverse-engineering/          # from phase 1
docs/reimagine/
+-- 01-assessment.md               # fitness scores, pain, dispositions
+-- dispositions.csv               # every object: keep / rebuild / replace / retire
+-- 02-options.md                  # options, scores, steelman, recommendation
+-- 03-target-architecture.md      # the chosen future, diagrams, what disappears
`-- 04-roadmap.md                  # waves, parity, cutover, decommission
docs/architecture/                 # persona doc set of the target
```

Then a hand-off under 10 lines: the recommendation, what it removes, the first
wave, top risks and the decision needed.
