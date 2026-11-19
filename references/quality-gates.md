# Quality Gates

Run the validator script first, then walk this list. Do not hand off until every
box is checked or has a one-line reason.

## Automated (validate_docs.py)
- [ ] Every expected doc exists for the packs requested
- [ ] Every doc has front matter with doc_id, persona, status, version, last_updated
- [ ] Every ADR/REQ/NFR/RSK/SRC/PL/DP/TST ID referenced is defined somewhere
- [ ] No leftover template placeholders (`{{...}}`, `TBD` without an ID, `lorem`)
- [ ] Every ASSUMPTION and OPEN QUESTION has an ID
- [ ] Every mermaid block opens and closes
- [ ] Exec docs under word ceiling
- [ ] No em dashes, no banned filler phrases

## Persona consistency check (manual)
Pick five facts and trace them through all three packs:
- [ ] Annual run cost
- [ ] Go-live date of phase 1
- [ ] The freshness SLA of the main data product
- [ ] The platform decision and its main reason
- [ ] The number one risk
They must match exactly or round correctly from the facts file.

## Executive pack
- [ ] First 3 lines state the recommendation, cost and timeline
- [ ] "Decisions needed from you" has options and a recommendation
- [ ] No unexplained acronyms; no tool names without the business reason
- [ ] Diagram has 7 or fewer boxes with business labels
- [ ] Brief fits on 2 printed pages

## Director pack
- [ ] Every role in RACI is a real role on the team or a named hire
- [ ] Every SLA has a measurement method and an owner
- [ ] Every phase in the delivery plan has exit criteria
- [ ] Cost model shows unit x volume x frequency and the price date
- [ ] Governance doc maps each sensitive data class to a control

## Engineer pack
- [ ] Every pipeline spec states: pattern, schedule, incremental key, idempotency, late data, schema drift, retries, backfill, owner
- [ ] Every gold model states grain and primary key
- [ ] Every NFR maps to a design section AND a test
- [ ] Every failure mode in the TDD has a runbook entry
- [ ] Environments doc has the exact promotion steps, not just a diagram
- [ ] A new senior engineer could start building without a meeting

## Writing
- [ ] Read every exec paragraph aloud. If it sounds like a vendor brochure, rewrite.
- [ ] Delete any sentence that survives deletion.
