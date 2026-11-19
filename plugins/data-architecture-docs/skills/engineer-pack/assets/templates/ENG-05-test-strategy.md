---
doc_id: ENG-05
title: Test Strategy
persona: lead-data-engineer
status: draft
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
related: [DIR-04, ENG-03, ENG-06]
---

# {{project_name}}: Test Strategy

## 1. Principles
- Tests run in CI on every PR against a dev/CI target, and in production on every run.
- Error-severity failures block publish to consumers. Warn-severity alerts but publishes.
- Every gold model has: primary key unique + not null, relationships to conformed dims, freshness.

## 2. Test pyramid for data
| Level | What | Tool | Where it runs | Blocks |
|---|---|---|---|---|
| Unit | Transformation logic on fixed inputs | dbt unit tests / pytest | CI | PR merge |
| Schema / contract | Columns, types, constraints | dbt contracts / contract YAML | CI + prod | PR merge / publish |
| Data quality | Nulls, uniqueness, ranges, accepted values, referential | dbt tests / DQ tool | prod every run | publish (error) |
| Reconciliation | Row counts and sums vs source | custom SQL | prod daily | publish (financials) |
| Freshness | Age of latest data | source freshness / monitor | prod | alert |
| Performance | Runtime and capacity budget | orchestrator metrics | prod + pre-release | release |
| UAT | Business sign-off on numbers | report walkthrough + recon pack | test env | go-live |

## 3. Test catalog
| TST | Object | Type | Rule | Severity | Traces to |
|---|---|---|---|---|---|

## 4. Test data
<!-- Fixtures, masked prod samples, synthetic data. How PII is kept out of dev. -->

## 5. Reconciliation design
<!-- Which measures, source query, target query, tolerance, where results are stored and shown. -->

## 6. Regression and release testing
<!-- State-based CI (modified + downstream), full refresh tests before release, comparison of prod vs candidate (audit_helper or equivalent). -->

## 7. UAT plan
| Data product | Business tester | Scenarios | Sign-off criteria |
|---|---|---|---|

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
