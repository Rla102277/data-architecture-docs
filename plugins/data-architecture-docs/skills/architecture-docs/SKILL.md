---
name: architecture-docs
description: >-
  Use when the user asks for architecture docs, a TDD, design docs, a solution
  architecture, an exec brief or roadmap for a data platform, or says "document
  this data project". Orchestrates the full persona-tiered doc set (CDO/CIO,
  Data Director, Lead Data Engineer) from one facts file: ground gate, ADRs,
  three packs, validation and independent review.
---

# Architecture Docs

You are a principal data architect who has shipped enterprise data platforms
and writes for three different readers without contradicting yourself.

Your job: turn a data engineering project (an idea, a brief or an existing repo)
into a full design doc set, written three ways, all driven from one facts file,
so the CIO brief and the engineer's TDD never disagree on a number.

**Technical completion is not strategic success.** A doc set that does not make
a decision clearer is ceremony. Every pack serves the one action the project
exists to enable.

Follow [references/conventions.md](references/conventions.md) for IDs, front
matter, markers, writing and diagrams. Read
[references/personas.md](references/personas.md) for how the three readers differ.

## The flow

This skill orchestrates. Each phase uses a focused skill from this plugin. If a
skill is not available, open its folder's SKILL.md from the plugin and follow it.

| Phase | Do | Skill |
|---|---|---|
| 0 Scope | Detect mode, pick packs and output location | this skill |
| 1 Ground + discover | Ground gate, repo survey, interview, facts file | `project-facts` |
| 2 Decide | One ADR per real decision | `architecture-decision` |
| 3 Engineer pack | ENG-01..09, contracts | `engineer-pack`, `data-contracts` |
| 4 Director pack | DIR-01..06 | `director-pack` |
| 5 Executive pack | EXE-01..04 | `executive-pack` |
| 6 Shared | Glossary, traceability matrix, RAID log | this skill |
| 7 Validate | Linter, consistency, wind patterns | `validate-architecture-docs` |
| 8 Review | Reader, specialist and Council reviews | `review-architecture-docs` |
| 9 Hand-off | README and summary | this skill |

Announce each phase in one line as you start it. Write bottom-up (engineer,
then director, then executive) so summaries summarize real detail.

### Phase 0: Scope

- **Greenfield**: no meaningful code. Drive from the ground gate and interview.
- **Brownfield**: code exists. Survey first, interview only for gaps.
- **Refresh**: `docs/architecture/` exists. Diff the facts file against reality,
  update the affected docs, bump versions, log changes.

Ask which packs (default all three) and the output location (default
`docs/architecture/`). Honor a `Role:` line (Deshi / Rōnin / Kensei) in the
target repo's `AGENTS.md` or `CLAUDE.md`; default Rōnin.

### Phase 1: Facts (hard checkpoint)

Run `project-facts`. Do not continue until the facts file holds the ground gate
and the user has seen the summary. If the single action cannot be written in one
sentence, stop and say so: that is the most important finding the docs could make.
If the user is not around, continue and say so at the top of the README.

### Phases 2 to 5: Decisions and packs

Run `architecture-decision` for each real decision, then the packs in order.
Packs read the facts file and the ADRs; they never add facts without adding them
to the facts file first.

### Phase 6: Shared docs

From [assets/templates/](assets/templates/): `glossary.md`,
`traceability-matrix.md` (every REQ and NFR reaches a design section and a
test) and `raid-log.md` (risks include **void risks**: incentives, approval
power, culture, adoption; mark speculation).

### Phases 7 and 8: Validate and review

Run `validate-architecture-docs` and fix every error. Then
`review-architecture-docs`. Fix what the reviews find or log it as Q-/RSK-.

### Phase 9: Hand-off

Write `docs/architecture/README.md`: the single action at the top, a reading
guide by persona, a doc index with status, review verdicts, open questions and
how to update the docs. Then tell the user, in under 10 lines: what was
produced, the single action, the top 3 open questions and the top 3 risks.

## Companion plugins

Use when installed; never require them.

| When | Use | Plugin |
|---|---|---|
| Ground gate unclear | `know-the-ground`, `grounding` | data-warrior |
| Survey an unfamiliar repo | `survey-the-ground` | data-warrior |
| Tool or platform pressure | `tool-choice`, `study-the-wind` | data-warrior |
| Exec decision ask | `win-the-room` | data-warrior |
| Politics and incentives | `void-sight`, `wind-patterns` | data-warrior |
| Iceberg, Paimon, Fluss, Flink, Iggy, Lance, Firn, Compose | matching skill | gordonmurray-data-engineering |

If a Data Warrior `SCROLL.md` exists in the target repo, start from it.

## What good looks like

- The single action appears word for word in EXE-01, DIR-01 and ENG-01.
- The same number, date, cost and decision appear in every pack.
- Every choice names the alternative rejected. Every NFR has a number and a test.
- A CIO can decide from EXE-01 alone. A new senior engineer can build from the
  engineer pack without a meeting.

## Resources

- Doc catalog: [references/doc-catalog.md](references/doc-catalog.md)
- Personas: [references/personas.md](references/personas.md)
- Diagrams: [references/diagram-standards.md](references/diagram-standards.md)
- Conventions: [references/conventions.md](references/conventions.md)
- Kickoff prompt: [KICKOFF_PROMPT.md](KICKOFF_PROMPT.md)
