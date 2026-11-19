---
name: executive-pack
description: >-
  Use when writing or revising the CDO/CIO executive documents for a data
  platform: the executive brief, strategic architecture overview, investment
  and roadmap, and risk and governance summary (EXE-01..04). Decision-first,
  2-page brief in the win-the-room shape, every number from the facts file.
---

# Executive Pack (CDO / CIO)

Write `docs/architecture/executive/EXE-01..04` from
[assets/templates/](assets/templates/). Read the facts file, the ADR exec
one-liners and the director pack first. Follow
[references/conventions.md](references/conventions.md).

## The reader

Owns the data and technology agenda. Answers to the CEO, CFO and board. Reads on
a phone between meetings, five minutes, deciding: fund it, sequence it, accept
the risk, or stop. Cares in order about outcome and value, total cost and when it
is spent, risk (delivery, security, compliance, lock-in, key-person, adoption),
milestones to report upward, and what they personally must do.

They do not want tool names without a reason, acronyms, diagrams with more than
7 boxes, or anything that reads like a vendor pitch.

## Voice

Decisive, numeric, honest about risk. Lead with the answer. "We recommend."
Every paragraph passes the "so what" test.

| Engineer says | Exec reads |
|---|---|
| Medallion lakehouse with Direct Lake | One governed copy of company data that reports read directly, so numbers match everywhere |
| CDC via change tracking | Systems update the platform within minutes instead of overnight |
| Data Vault raw vault | We keep full history of every change, so audits and restatements are cheap |
| RLS in the semantic model | Each person only sees the data they are allowed to see |

## EXE-01 shape (win the room)

1. The decision, in one sentence (the facts file single action).
2. Bottom line: recommendation, cost, timeline, in three lines.
3. Why now, and the risk of the wrong choice.
4. The evidence: observed facts only, each traceable.
5. How we will know it worked, or is not working (KPIs plus the falsifiers).
6. The ask: approve, delay or refuse, with a clear exit for the reader.
7. If the answer is no: what we do instead and what that costs.

Never claim agreement, approval or sign-off that did not happen.

## Limits

| Doc | Ceiling |
|---|---|
| EXE-01 | 2 printed pages (about 900 words) |
| EXE-02..04 | 3 pages each |

Diagrams: 7 boxes max, business labels. Rounded numbers must round from the
exact facts-file number. The top risks include at least one adoption or
organizational (void) risk when one exists.
