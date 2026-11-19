---
doc_id: EXE-04
title: Risk and Governance Summary
persona: executive
status: draft
version: 0.1.0
owner: Director of Data
last_updated: 2026-11-19
facts_version: 0.1.0
related: [EXE-01]
---

# Atlas: Risk and Governance Summary

## Summary
The technical risk is manageable. The real risk is people: whether account
managers will use margin numbers that expose their own accounts.

## Top risks
| ID | Risk | Likelihood | Impact | Owner | What we are doing |
|---|---|---|---|---|---|
| RSK-001 | Freight and rebate cost rules live in one analyst's spreadsheet | High | High | Controller | Document the rules in February; reconcile before scaling |
| RSK-002 | Account managers resist repricing their own accounts | Medium | High | VP Sales | VP Sales owns rollout; first reviews use regional views |

## What the org chart will decide
Margin by customer makes some account managers look worse than they think they
are. If their incentives reward revenue and not margin, they have a reason to
argue with the numbers instead of using them. This is a judgment, not a fact we
have tested. The test is the second falsifier: whether Sales leadership uses the
report in the first two renewal reviews.

## Compliance posture
| Framework | What it requires of data | How we meet it |
|---|---|---|
| SOX | Financial numbers are traceable and controlled | Margin reconciles to the ledger monthly; changes go through review |
| State privacy law | Personal contact data is protected | Contact details stay out of margin reports |

## Who owns the data
The Controller owns the margin definition and cost allocation. The Director of
Data owns the platform. Access is approved by the data owner, through
security groups.

## Vendor and lock-in
Data is stored in an open table format, so it can be read by other tools if we
ever leave the platform.

## Key-person risk
One data engineer and one contractor. If the engineer leaves, the run book and
the facts file are what the next person starts from.

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0 | 2026-11-19 | Director of Data | First draft (example) |
