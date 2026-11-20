---
name: current-state-assessment
description: >-
  Use when an existing data platform, warehouse, ETL estate or reporting stack
  must be judged before deciding what to do with it: fitness scores with
  evidence (trust, freshness, cost, operability, change speed, security,
  key-person risk, adoption), pain gathered from consumers and operators, root
  causes vs symptoms, and a keep / rebuild / replace / retire disposition for
  every object.
---

# Current State Assessment

Judge the current system on evidence, find the root causes, and decide the fate
of every piece of it.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- Phase 2 of `reimagine-data-system`.
- "Is this warehouse worth saving?" "What is actually wrong with our reporting?"

Not for: building the inventory itself (use `sql-object-inventory` and the rest
of `reverse-engineer-data-system` first).

## Inspect first

1. Reverse-engineering evidence: inventory, usage, lineage, rules, profiles,
   job history, incidents.
2. The people: two or three consumers (finance, ops, sales), the operators who
   get paged, and the owner. Their pain is data too.
3. Cost: licenses, hardware or cloud spend, support contracts, and people time
   (hours per month on manual fixes and spreadsheet work).

## Procedure

1. **Score fitness** with [assets/assessment-scorecard.md](assets/assessment-scorecard.md):
   eight dimensions, 1 (failing) to 5 (strong), each with the evidence that
   justifies the score. No evidence, no score: mark it unknown.
2. **Collect pain** in short interviews (15 minutes each): what decision do you
   make with this data, what goes wrong, what do you do instead, what would you
   stop doing if it worked. Record quotes and frequency.
3. **Separate symptoms from causes.** "Reports are late" is a symptom; "the
   nightly chain is serial and one proc takes 3 hours" is a cause. For each pain,
   trace to a cause with evidence, or mark it unexplained.
4. **Disposition every object** in `docs/reimagine/dispositions.csv`
   (object, type, disposition, reason, evidence, owner):
   - **keep**: works, used, fits the future
   - **rebuild**: logic needed, implementation not (procs, SSIS, fragile jobs)
   - **replace**: a product or platform service does it better (ingestion
     connectors, scheduling, BI)
   - **retire**: no consumer, no decision, duplicate (with usage evidence and an
     owner who agrees)
5. **Write the assessment**: summary in five lines, scorecard, top causes with
   evidence, disposition counts, quick wins (fixes worth doing even if
   everything is replaced), and the questions only the owner can answer.

## Standards

- **MUST** cite evidence for every score and disposition.
- **MUST** keep "retire" as a proposal until an owner agrees; usage stats reset
  on restart, so absence of use is weak evidence on its own.
- **MUST** separate consumer pain from engineer preference.
- **SHOULD** count the human cost (hours of manual work), not only licenses.
- **SHOULD** name quick wins honestly; some pains are cheap to fix now.

## Failure modes

| Failure | Prevention |
|---|---|
| Assessment that just confirms "it's legacy, replace it" | Scores need evidence; some may come out strong |
| Retiring a report someone uses at quarter end | Owner agreement and a full business cycle of usage evidence |
| Fixing symptoms in the new design | Cause tracing step |
| Engineers' wishlist mistaken for business need | Pain comes from consumer interviews |

## Verify

- Every inventory object has a row in `dispositions.csv`.
- Every score has evidence or says unknown.
- Each top pain has a traced cause or is marked unexplained.

## Output

`docs/reimagine/01-assessment.md` and `docs/reimagine/dispositions.csv`.
