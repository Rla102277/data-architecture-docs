# Conventions (shared by every architecture-docs skill)

Canonical copy: `plugins/data-architecture-docs/shared/conventions.md`.
Each skill carries a built copy in `references/conventions.md`. Do not edit the
copies; edit the canonical file and run `python3 scripts/build.py`.

## Output location

Default `docs/architecture/` in the target repo:

```
docs/architecture/
+-- 00-project-facts.yaml   # Single source of truth, ground gate first
+-- README.md               # Single action, reading guide, index, open questions
+-- executive/              # EXE-01..04
+-- director/               # DIR-01..06
+-- engineer/               # ENG-01..09
|   +-- adr/                # ADR-####-<slug>.md
|   `-- ENG-04-data-contracts/
+-- reviews/                # <persona>.md, each starts with a VERDICT line
`-- shared/                 # glossary, traceability matrix, RAID log
```

## Facts first

Every fact (sources, volumes, SLAs, costs, dates, decisions, owners, risks)
lives in `00-project-facts.yaml` first. Docs reference facts; they never invent
them inline. To change a fact, change the facts file, bump `facts_version`, then
update every doc that uses it.

## Stable IDs

| Prefix | Meaning | Example |
|---|---|---|
| `REQ-###` | Functional requirement | REQ-004 |
| `NFR-###` | Non-functional requirement | NFR-001 |
| `KPI-###` | Business measure | KPI-002 |
| `SRC-###` | Source system | SRC-003 |
| `DP-###` | Data product | DP-001 |
| `PL-###` | Pipeline | PL-012 |
| `TST-###` | Test or monitor | TST-041 |
| `RSK-###` | Risk | RSK-002 |
| `ADR-####` | Decision record | ADR-0003 |
| `A-###` / `Q-###` | Assumption / open question | A-001, Q-007 |

An ID must be defined (in the facts file, a heading or the first cell of a
table row) before any doc references it.

## Unknowns

- `> ASSUMPTION [A-###]: ...` when you chose a reasonable default
- `> OPEN QUESTION [Q-###]: ... (Owner: role, Needed by: phase)` when a human must decide

Register every A- and Q- in the facts file. Separate what you observed (cite the
file), what you assumed, and what was decided.

## Front matter and change log

```yaml
---
doc_id: ENG-01
title: Technical Design Document
persona: lead-data-engineer   # executive | data-director | lead-data-engineer | shared
status: draft                 # draft | review | approved | superseded
version: 0.1.0
owner: <role or name>
last_updated: YYYY-MM-DD
facts_version: <from 00-project-facts.yaml>
related: [ADR-0001, DIR-01]
---
```

Every doc ends with `## Change log` (version, date, author, change).
`status: approved` only when a named human approved it. Never set it yourself.

## Writing

- Short sentences, active voice, plain words. Summary first, then detail.
- No vendor-brochure language ("robust", "seamless", "best-in-class", "leverage").
- No em dashes.
- If a sentence survives being deleted, delete it.
- Every choice names the alternative rejected. Every number has a basis.

## Diagrams

Mermaid only, in fenced `mermaid` blocks. Data flows left to right. Exec
diagrams: 7 boxes max, business labels. Director: logical names. Engineer: real
names.

## Honesty

- Never invent approvals, reviews, sign-offs, test results, prices or volumes.
- The sword is not the warrior: no platform is preselected. Tools are justified
  by terrain (volume, latency, team, budget, compliance) in an ADR.
- Roles (Deshi / Rōnin / Kensei) change collaboration style, never permissions.
