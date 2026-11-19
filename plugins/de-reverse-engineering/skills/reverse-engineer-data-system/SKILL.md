---
name: reverse-engineer-data-system
description: >-
  Use when you inherit or must replace a data system nobody fully understands:
  a legacy SQL Server warehouse, stored procedures, SSIS packages, ADF or
  Fabric pipelines, a Snowflake account, an undocumented dbt project. Runs the
  full reverse-engineering pass (inventory, code, ETL, lineage, rules,
  profiling) and produces a system map, lineage, a business rules catalog and
  open questions in docs/reverse-engineering/.
---

# Reverse Engineer a Data System

Turn an undocumented data system into evidence: what exists, what runs, what
feeds what, what the business rules are, and what nobody knows yet.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- "Figure out what this old warehouse does before we migrate it."
- "Document these 400 stored procedures / SSIS packages / ADF pipelines."
- "Where does this report number actually come from?"
- Before any migration, rebuild or decommission of an existing data system.

Not for: designing a new platform from scratch (use `architecture-docs`), or
tracing one column in a system you already know (use `lineage-extraction` directly).

## Inspect first

1. **Access and safety.** Confirm read-only access. Every query in this plugin is
   a catalog or `SELECT` query. Never run a procedure, job or package to "see what
   it does" in production. If someone asks you to, stop and ask for a copy or a
   non-production environment.
2. **The ground.** Why are we reverse engineering this? (migrate, replace, audit,
   fix a number, decommission). The answer decides depth. A decommission needs
   usage evidence; a migration needs rules and parity; an audit needs lineage.
3. **What you can reach.** Database connections, a repo with SQL, exported
   `.dtsx` files, ADF/Fabric pipeline JSON (Git integration or export), dbt
   `manifest.json`, report definitions. Code in files beats code in a live server.

## Procedure

Work in this order. Each step has its own skill; use it.

| Step | Do | Skill | Output |
|---|---|---|---|
| 1 | Catalog every object, size, dependency, job, schedule, usage signal | `sql-object-inventory` | `inventory/` |
| 2 | Extract the code: views, procs, functions, triggers, job steps | `sql-object-inventory` | `code/` |
| 3 | Read the ETL packages and pipelines | `etl-package-analysis` | `etl/` |
| 4 | Build table-level lineage from code and packages | `lineage-extraction` | `lineage/` |
| 5 | Spec the important procedures | `stored-procedure-analysis` | `procs/` |
| 6 | Pull out the business rules with evidence | `business-rule-extraction` | `rules/` |
| 7 | Profile the tables that matter | `data-profiling` | `profiles/` |
| 8 | Write the system map and open questions | this skill | `system-map.md`, `open-questions.md` |

**Triage before depth.** After step 1, rank objects by: feeds a known report or
consumer, row count and churn, recent execution, number of dependents. Go deep on
the top 20 percent; list the rest. Mark everything with no usage signal in 90
days as a decommission candidate, not as dead (usage stats reset on restart).

**Write the system map** (`system-map.md`):
- One paragraph: what this system does for the business, in plain words.
- A Mermaid flowchart of sources, staging, core, marts and consumers (max 20 nodes; detail lives in `lineage/`).
- Schedules: what runs when, in what order, and what depends on what.
- The 10 most important objects with one line each.
- Known landmines: dynamic SQL, cross-database or linked-server calls,
  `NOLOCK`, cursors, triggers, hard-coded dates or IDs, silent `TRY/CATCH`.

**Write open questions** (`open-questions.md`): every rule or behavior you
could not confirm from code or data, with the evidence you have, a confidence
(high/medium/low) and who could answer.

## Standards

- **MUST** save every catalog query result to a file (CSV) with the query, the
  server/database and the timestamp. Evidence you cannot reproduce is opinion.
- **MUST** label every claim: observed (cite file:line or query), inferred (say
  from what), or unknown (open question).
- **MUST** treat code as the spec and data as the truth. When they disagree
  (a rule in code that the data violates), record both. That is a finding.
- **SHOULD** extract code to files first and analyze files, not the live server.
- **SHOULD** keep object names exactly as the source spells them.
- **MAY** stop at triage depth when the goal is decommission or sizing.

## Failure modes

| Failure | Prevention |
|---|---|
| Running a proc or job to learn what it does, in production | Inspect first: read-only only; ask for a copy |
| Calling an object unused because usage stats are empty | Stats reset on restart; check job steps, code references and report sources too |
| Missing logic hidden in dynamic SQL, linked servers or synonyms | Inventory flags these; procs with dynamic SQL get manual review |
| Lineage that looks complete but skips unparsed statements | `lineage-extraction` lists every statement it could not parse |
| Rules stated as fact from a single code path | Rules carry evidence and confidence; low confidence becomes a question |
| Drowning in 2,000 objects | Triage ranking; depth only where it matters |

## Verify

- Every object in `inventory/objects.csv` appears in the system map, a lineage
  edge, or the decommission-candidate list.
- Pick the three most important report numbers and trace each end to end
  through `lineage/` back to a source column. If you cannot, that is an open question.
- Reconcile one row count per layer (source vs staging vs core) with a query.

## Output

```
docs/reverse-engineering/
+-- system-map.md          # What it does, flow diagram, schedules, top objects, landmines
+-- open-questions.md      # Unknowns with evidence, confidence, who can answer
+-- inventory/             # objects.csv, columns.csv, dependencies.csv, jobs.csv, usage.csv
+-- code/                  # One file per view, proc, function, trigger, job step
+-- etl/                   # One summary per package or pipeline
+-- lineage/               # edges.csv, lineage.md (Mermaid), unparsed.md
+-- procs/                 # One spec per important procedure
+-- rules/                 # rules-catalog.md
`-- profiles/              # One profile per important table
```

If the next step is a rebuild, hand `rules/` and `lineage/` to
`legacy-to-dbt-migration`. If it is a new design, hand the whole folder to
`architecture-docs` as the brownfield survey.
