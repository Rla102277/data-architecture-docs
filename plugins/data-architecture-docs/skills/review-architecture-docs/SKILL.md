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

Review the set through the people who will read it. Follow
[references/conventions.md](references/conventions.md).

## Who reviews what

| Pack | Reader | Specialists |
|---|---|---|
| Executive | `cio-reader` | |
| Director | `data-director-reader` | `data-platform-reliability-reviewer`, `data-security-and-compliance-auditor` |
| Engineer and ADRs | `lead-engineer-reader` | `data-architect`, `analytics-engineer-reviewer`, `data-platform-infrastructure-reviewer` |
| Whole set | `council` lenses: Strategist, Architect, Engineer, Guardian, Examiner, Sensei | |

These are subagents shipped in this plugin's `agents/` folder. Each one is
read-only and returns its review; you write the file.

## How to run

1. **Independent if you can.** If the host can launch subagents, run each
   reviewer as its own subagent with only the docs path and its brief. Run the
   three readers in parallel. Mark those reviews `independent`.
2. **Otherwise, one agent, honest.** Apply each persona in turn and mark the
   review `perspective (single agent)`. Never claim independence that did not happen.
3. Write each to `docs/architecture/reviews/<persona>.md`. The first line is
   exactly `VERDICT: PASS` or `VERDICT: CHANGES`. Then: reviewer, mode
   (independent or perspective), and findings with doc_id and section.
4. Council: use a lens only when it can change a verdict. Write
   `reviews/council-<lens>.md` for each lens actually applied.
5. Fix what you can. Log the rest as `Q-###` or `RSK-###` in the facts file.
   Re-run only the reviewers whose findings you changed.

## Block conditions

Any reviewer blocks the hand-off when: exec numbers disagree with other packs;
an error-severity data path has no test or recovery; sensitive data has no
control; the plan commits to SLAs nobody can measure or staff.
