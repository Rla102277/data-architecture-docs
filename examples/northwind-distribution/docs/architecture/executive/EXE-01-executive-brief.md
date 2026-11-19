---
doc_id: EXE-01
title: Executive Brief
persona: executive
status: draft
version: 0.1.0
owner: Director of Data
last_updated: 2026-11-19
facts_version: 0.1.0
related: [ADR-0001]
---

# Atlas: Executive Brief

## The decision
Approve $180K and a two-person team by Jan 15 so margin by customer and SKU is ready for the April renewal cycle.

## Bottom line
We recommend building a small, governed data platform on Microsoft Fabric. It
costs $180K to build and $62K a year to run, and gives Finance and Sales a
reconciled margin report by customer and SKU before April renewals.

## Why now, and the risk of the wrong choice
Today two analysts spend about 80 hours a month building margin in spreadsheets,
and the result does not tie to the general ledger. We will reprice renewals in
April either way. Without this, we reprice on numbers we cannot defend. If we
pick a heavier platform than this team can run, we miss April entirely.

## The evidence
- Margin work costs 80 analyst hours a month today (KPI-002).
- All three systems we need can feed the platform: the ERP supports change
  tracking (ASSUMPTION [A-001], confirmed by Jan 31), the warehouse system sends
  nightly files, and the CRM has an API.
- We already own Power BI and the identity system, so there is no new reporting
  tool to buy or train on (ADR-0001).

## What we will deliver
- Daily margin by customer and SKU, ready by 6am Central (KPI-001)
- One margin number that ties to the general ledger within half a percent
- Analyst time on margin cut from 80 to 8 hours a month (KPI-002)

## How we will know it worked, or that it is not working
| KPI | Today | Target | By when |
|---|---|---|---|
| Gross margin on renewed contracts | 21.0% | 22.5% | Renewal cycle close |
| Analyst hours per month on margin | 80 | 8 | End of March |

Early warning: if margin does not reconcile to the ledger within 0.5% by Feb 28,
we stop and fix cost allocation before building anything else. If Sales
leadership does not use the report in the first two renewal reviews, we have a
adoption problem, not a data problem, and we will say so.

## Cost and timeline
| | Amount | Notes |
|---|---|---|
| One-time build | $180K | Contract engineer for 6 months, setup, training |
| Annual run | $62K | Platform capacity and storage, prices as of Nov 19, 2026 |

| Phase | When | What the business gets |
|---|---|---|
| Margin foundation | Jan 15 to Mar 31 | Reconciled margin by customer and SKU for April renewals |

## Top risks
| Risk | What we are doing |
|---|---|
| Freight and rebate cost rules live in one analyst's spreadsheet (RSK-001) | Controller documents them in February; we reconcile before scaling |
| Account managers may resist repricing their own accounts (RSK-002) | VP Sales owns rollout; first reviews use regional views, not per-rep |

## The ask
| Decision | Options | We recommend | Needed by |
|---|---|---|---|
| Fund phase 1 | Approve $180K / delay to Q2 / decline | Approve | Jan 15 |
| Confirm run budget source (Q-001) | FY27 IT plan / new spend | Your call | Jan 15 |

## If the answer is no
We price April renewals on the current spreadsheets, add one more analyst-week
to check the largest 20 accounts by hand, and revisit in Q3. That keeps the
undefendable numbers and the 80 hours a month.

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0 | 2026-11-19 | Director of Data | First draft (example) |
