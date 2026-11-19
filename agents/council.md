# The Council (Data Warrior review lenses)

From The Data Warrior: six perspectives to read a design through. They are
**lenses, not six agents**. One reviewer can apply several. Never claim six
independent reviews unless six different reviewers actually ran.

Use them on the doc set in Phase 5b of `data-architecture-docs`, alongside the
specialist reviewers in this folder. Use a lens only when it can change a verdict.

| Lens | Question it asks of the docs | Checks first | Pairs with |
|---|---|---|---|
| **Strategist** | Does this change a decision someone will actually make? Is the single action in one sentence? | EXE-01, EXE-03, facts `ground.single_action` | `cio-reader`, Data Warrior `win-the-room` |
| **Architect** | Are layers, keys, grain, ownership and naming clear and simple enough to operate? | DIR-01, ENG-01, ENG-02, ADRs | `data-architect` |
| **Engineer** | Can a senior engineer build this without a meeting? Idempotency, replay, deletes, drift? | ENG-03, ENG-05, ENG-06 | `analytics-engineer-reviewer`, `data-platform-reliability-reviewer` |
| **Guardian** | Secrets, access, PII, retention, destructive actions, compliance evidence? | DIR-03, ENG-07 | `data-security-and-compliance-auditor` |
| **Examiner** | Do the numbers reconcile? Grain, duplicates, null keys, contract fit, test evidence? | DIR-04, ENG-04, ENG-05, traceability matrix | Data Warrior `test-the-steel` |
| **Sensei** | Will the team and the business actually adopt this? What do incentives and culture say? Is the team being taught or just handed docs? | DIR-02, EXE-04, RAID log | Data Warrior `void-sight`, `name-the-wind` |

## Output

Write one file per lens actually applied to
`docs/architecture/reviews/council-<lens>.md`, starting with
`VERDICT: PASS` or `VERDICT: CHANGES`, then findings with doc_id and section.
State at the top who ran it and that lenses applied by one reviewer are
perspectives, not independent reviews.
