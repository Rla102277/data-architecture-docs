---
name: review-architecture-docs
description: >-
  Use when a data architecture doc set (or one pack) is drafted and needs
  review before it is shared: CIO, Data Director and Lead Data Engineer reader
  reviews, specialist reviews (architecture, analytics engineering,
  reliability, infrastructure, security) and the Data Warrior Council lenses.
  Writes verdict files to docs/architecture/reviews/.
---

# Review Architecture Docs

Review the set through the people who will read it, honestly labeled.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- Phase 8 of `architecture-docs`.
- Before sharing any pack.

Not for: linting (use `validate-architecture-docs` first).

## Inspect first

1. The linter passed.
2. Whether the host can launch subagents (Claude Code and Cursor can, with this
   plugin's `agents/`). That decides independent vs perspective mode.

## Procedure

| Pack | Reader subagent | Specialist subagents |
|---|---|---|
| Executive | `cio-reader` | |
| Director | `data-director-reader` | `data-platform-reliability-reviewer`, `data-security-and-compliance-auditor` |
| Engineer and ADRs | `lead-engineer-reader` | `data-architect`, `analytics-engineer-reviewer`, `data-platform-infrastructure-reviewer` |
| Whole set | `council` lenses (Strategist, Architect, Engineer, Guardian, Examiner, Sensei) | |

1. **Independent if you can**: launch each reviewer as its own subagent with only
   the docs path; run the three readers in parallel. Mode: independent.
2. **Otherwise**: apply each persona in turn yourself. Mode: perspective (single agent).
3. Write each returned review to `docs/architecture/reviews/<persona>.md`; first
   line exactly `VERDICT: PASS` or `VERDICT: CHANGES`, then mode, then findings
   with doc_id and section. Council: `reviews/council-<lens>.md` per lens applied.
4. Fix what you can; log the rest as `Q-###` or `RSK-###`; re-run only reviewers
   whose findings changed.

## Standards

- **MUST** label each review independent or perspective, truthfully.
- **MUST** block hand-off when exec numbers disagree with other packs, an
  error-severity data path has no test or recovery, sensitive data has no
  control, or an SLA cannot be measured or staffed.
- **SHOULD** use a Council lens only when it can change a verdict.

## Failure modes

| Failure | Prevention |
|---|---|
| Self-review claimed as independent | Mode label required |
| Reviewer edits docs instead of reviewing | Reviewers are read-only and return text |
| Findings lost | Unfixed findings become Q-/RSK- items |

## Verify

Every review file starts with a VERDICT line (the linter enforces it) and states its mode.

## Output

`docs/architecture/reviews/*.md` and updated Q-/RSK- items in the facts file.
