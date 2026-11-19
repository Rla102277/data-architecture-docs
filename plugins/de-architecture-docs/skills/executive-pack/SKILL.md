---
name: executive-pack
description: >-
  Use when writing or revising the CDO/CIO executive documents for a data
  platform: the executive brief, strategic architecture overview, investment
  and roadmap, and risk and governance summary (EXE-01..04). Decision-first,
  2-page brief in the win-the-room shape, every number from the facts file.
---

# Executive Pack (CDO / CIO)

Give the person who funds the platform what they need to decide in five minutes.

Follow [references/doctrine.md](references/doctrine.md) and
[references/conventions.md](references/conventions.md).

## When to use

- Phase 5 of `architecture-docs`, after the engineer and director packs.
- "Write the exec brief for the CIO."

Not for: build detail (engineer pack) or operating detail (director pack).

## Inspect first

1. The facts file (ground gate, costs, timeline, risks), the ADR exec one-liners,
   and the director pack.
2. The reader: owns the data and technology agenda, answers to the CEO, CFO and
   board, reads on a phone. Cares, in order, about outcome, total cost and timing,
   risk (including adoption), milestones to report upward, and what they must do.

## Procedure

1. Write `executive/EXE-01..04` from [assets/templates/](assets/templates/).
2. EXE-01 follows the **win-the-room** shape: the decision in one sentence;
   bottom line (recommendation, cost, timeline) in three lines; why now and the
   risk of the wrong choice; the evidence (observed only); how we will know it
   worked or is not working (KPIs plus falsifiers); the ask (approve, delay,
   refuse) with a clear exit; what we do if the answer is no.
3. Translate engineering into business consequences, e.g. "Direct Lake" becomes
   "one governed copy of company data that reports read directly, so numbers match everywhere".
4. Diagrams: 7 boxes max, business labels.
5. Top risks include at least one adoption or organizational (void) risk when one exists.

## Standards

- **MUST** take every number from the facts file; rounded numbers round from it.
- **MUST** lead with the decision and the ask.
- **MUST NOT** claim agreement, approval or sign-off that did not happen.
- **SHOULD** keep EXE-01 to about 900 words (2 pages), EXE-02..04 to 3 pages each.
- **SHOULD** avoid tool names unless the tool is the decision, and avoid acronyms.

## Failure modes

| Failure | Prevention |
|---|---|
| Reads like a vendor pitch | Decision, evidence, risk, ask structure |
| CFO challenges a number that differs from the director pack | Numbers only from the facts file |
| Only technical risks listed | Void risk required when present |

## Verify

- The linter's word ceilings pass; the `cio-reader` review can decide from EXE-01 alone.

## Output

`docs/architecture/executive/EXE-01..04`.
