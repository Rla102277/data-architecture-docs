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

Turn a data project into one design doc set written three ways (CDO/CIO, Data
Director, Lead Data Engineer) from one facts file, so the CIO brief and the TDD
never disagree on a number.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- "Write the architecture docs and TDD for this platform."
- "We need an exec brief, a solution architecture and build docs for Foundation."
- Refreshing a doc set after the platform changed.

Not for: a single decision (use `architecture-decision`), or understanding an
undocumented legacy system first (run `reverse-engineer-data-system`, then this).

## Inspect first

1. Mode: **greenfield** (no code), **brownfield** (code exists, survey first),
   or **refresh** (`docs/architecture/` exists; diff facts against reality).
2. Which packs (default all three) and where (default `docs/architecture/`).
3. A `Role:` line (Deshi / Rōnin / Kensei) in the target repo's `AGENTS.md` or
   `CLAUDE.md`; default Rōnin.
4. Existing inputs: `SCROLL.md` (Data Warrior), `docs/reverse-engineering/`,
   existing ADRs. Start from them.
5. The three readers: [references/personas.md](references/personas.md).

## Procedure

Announce each phase in one line. Each uses a focused skill from this plugin.

| Phase | Do | Skill |
|---|---|---|
| 1 Facts (hard checkpoint) | Ground gate, survey, interview, facts file, user confirms | `project-facts` |
| 2 Decide | One ADR per real decision | `architecture-decision` |
| 3 Engineer pack | ENG-01..09 and contracts | `engineer-pack`, `data-contracts` |
| 4 Director pack | DIR-01..06 | `director-pack` |
| 5 Executive pack | EXE-01..04 | `executive-pack` |
| 6 Shared | Glossary, traceability matrix, RAID log (with void risks) from [assets/templates/](assets/templates/) | this skill |
| 7 Validate | Linter, consistency, wind patterns | `validate-architecture-docs` |
| 8 Review | Reader, specialist and Council reviewer subagents | `review-architecture-docs` |
| 9 Hand-off | README: single action first, reading guide, index, verdicts, open questions | this skill |

Write bottom-up (engineer, director, executive) so summaries summarize real
detail. If the single action cannot be written in one sentence at phase 1, stop
and say so: that is the most important finding. If the user is not around at
the checkpoint, continue and say so at the top of the README.

Companion plugins, used when installed: data-warrior (`know-the-ground`,
`study-the-wind`, `win-the-room`, `void-sight`), de-reverse-engineering (brownfield
survey), gordonmurray-data-engineering (Iceberg, Flink, Paimon and others).

## Standards

- **MUST** put every fact in the facts file first; docs cite it, never invent.
- **MUST** keep the same numbers, dates, costs and decisions across all packs.
- **MUST** mark unknowns as `ASSUMPTION [A-###]` or `OPEN QUESTION [Q-###]`.
- **MUST** never set `status: approved` or claim a review that did not run.
- **SHOULD** keep the executive brief to 2 pages and lead with the decision.
- **SHOULD** write the engineer pack so a new senior engineer can build without a meeting.

## Failure modes

| Failure | Prevention |
|---|---|
| Exec brief and TDD disagree on cost or dates | One facts file, consistency check in validation |
| Pretty docs that change no decision | Ground gate first; single action at the top of every pack |
| Docs describe an imagined system | Brownfield survey with file citations |
| Unknowns papered over | Tagged assumptions and open questions with owners |
| One agent "reviews" its own work and calls it independent | Reviewer subagents, honest mode labels |

## Verify

- `validate-architecture-docs` exits 0.
- The single action appears word for word in EXE-01, DIR-01 and ENG-01.
- Five facts traced through all three packs match.
- Every review file starts with a VERDICT line.

## Output

`docs/architecture/` with the facts file, executive, director, engineer, shared
and reviews folders, and a README; plus a hand-off message under 10 lines: what
was produced, the single action, top 3 open questions, top 3 risks. Kickoff
prompt: [KICKOFF_PROMPT.md](KICKOFF_PROMPT.md). Catalog of docs:
[references/doc-catalog.md](references/doc-catalog.md). Diagrams:
[references/diagram-standards.md](references/diagram-standards.md).
