---
doc_id: ADR-{{nnnn}}
title: {{short title of decision}}
persona: lead-data-engineer
status: proposed      # proposed | accepted | rejected | superseded by ADR-xxxx
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
deciders: []
consulted: []
related: []
---

# ADR-{{nnnn}}: {{short title of decision}}

## Context and problem
<!-- 2-5 sentences. What forces this decision now. Observed facts vs assumptions labeled. -->

## Decision drivers
- {{driver, e.g. NFR-002 freshness under 15 minutes}}

## Options considered
<!-- At least two viable options, plus the status quo when one exists. For ingestion, CDC vs timestamp watermark explicitly. -->
0. Status quo: {{what happens if we do nothing}}
1. {{option A}}
2. {{option B}}

## Option analysis
| Criterion | Status quo | Option A | Option B |
|---|---|---|---|
| Correctness under failure / replay | | | |
| Operational burden | | | |
| Latency / freshness | | | |
| Governance and security | | | |
| Cost (run + build) | | | |
| Reversibility | | | |
| Team can operate it today | | | |

## Steelman of the strongest rejected option
<!-- The best honest case for the option we did not pick. If you cannot write one, you have not compared fairly. -->

## Decision
Chosen: **{{option}}**, because {{one-sentence justification tied to drivers}}.
Not chosen because of habit, vendor preference or resume value.

## Consequences
- Good:
- Bad / accepted trade-off:
- Follow-up work:

## Validation test
<!-- Falsifiable. What measurable result by when would make us revisit this decision. -->

## Exec one-liner
<!-- How EXE docs should describe this decision in one plain sentence. -->

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
