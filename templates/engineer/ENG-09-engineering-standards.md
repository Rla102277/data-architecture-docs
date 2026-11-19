---
doc_id: ENG-09
title: Engineering Standards
persona: lead-data-engineer
status: draft
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
related: [ENG-02, ENG-06]
---

# {{project_name}}: Engineering Standards

Keywords MUST, SHOULD, MAY follow RFC 2119.

## 1. Naming
| Object | Pattern | Example |
|---|---|---|
| Workspace / database | `<code>-<layer>-<env>` | |
| Schema | | |
| Staging model | `stg_<source>__<entity>` | |
| Intermediate model | `int_<entity>__<verb>` | |
| Dimension | `dim_<entity>` | |
| Fact | `fct_<business_process>` | |
| Pipeline | `pl_<src>_<entity>_<pattern>` | |
| Column | snake_case; booleans `is_`/`has_`; timestamps `_utc` | |

## 2. Folder layout
```text
```

## 3. SQL style
<!-- sqlfluff config summary: casing, CTE style, no SELECT * past staging, explicit column lists, comments. -->

## 4. Python / notebook style
<!-- ruff config, parameterization, no hardcoded env values, logging standard. -->

## 5. Pull request checklist
- [ ] Linked ticket and REQ/ADR ids
- [ ] Tests added or updated, all passing in CI
- [ ] Model and column descriptions written
- [ ] Contract version bumped if schema changed
- [ ] No secrets, no hardcoded environment values
- [ ] Docs in `docs/architecture/` updated if design changed

## 6. Definition of done (per data product)
- [ ] Built and passing tests in test env
- [ ] Contract published
- [ ] RLS / access verified per role
- [ ] Monitoring and alerts live
- [ ] Runbook entry exists
- [ ] Consumer sign-off recorded

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
