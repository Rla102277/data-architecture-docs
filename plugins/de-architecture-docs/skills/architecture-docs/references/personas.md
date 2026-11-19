# Personas

Three readers. Same facts. Different altitude. Before writing any doc, decide which
persona it is for and write ONLY for that reader.

---

## 1. CDO / CIO (Executive)

**Who they are.** Owns the data and technology agenda for the company. Answers to
the CEO, CFO and board. Reads on a phone between meetings. Has 5 minutes.

**What they need to decide.** Fund it, sequence it, accept the risk, or kill it.

**What they care about, in order.**
1. Business outcome and value (revenue, margin, cycle time, risk avoided)
2. Total cost and when the money is spent (capex vs opex, run-rate)
3. Risk: delivery, security, compliance, vendor lock-in, key-person
4. Timeline and milestones they can report upward
5. What they personally must do (approve, sponsor, unblock, pick)

**What they do NOT want.** Tool names without a reason. Acronyms. Diagrams with
more than 7 boxes. Anything that reads like a vendor pitch.

**Voice.** Decisive, numeric, honest about risk. Lead with the answer. Use "we
recommend". Every paragraph passes the "so what" test.

**Format.**
- BLUF (bottom line up front) in the first 3 lines
- One context diagram, max 7 boxes, business labels ("Sales data", not "Bronze Lakehouse")
- Tables for cost, timeline, risk
- A clear "Decisions needed from you" section with options and a recommendation
- 1 to 3 pages

**Translation examples.**
| Engineer says | Exec reads |
|---|---|
| Medallion lakehouse on Fabric with Direct Lake | One governed copy of company data that reports read directly, so numbers match everywhere |
| CDC via SQL Server change tracking | Systems update the platform within minutes instead of overnight |
| Data Vault 2.0 raw vault | We keep full history of every change, so audits and restatements are cheap |
| RLS in the semantic model | Each person only sees the data they are allowed to see |

---

## 2. Data Director (Director of Data / Head of Data & Analytics)

**Who they are.** Owns the data platform, the team and the roadmap. Translates
strategy into delivery. Accountable for quality, adoption, cost and people.
Technical enough to challenge a design, but is not writing the code.

**What they need to decide.** Scope, sequencing, staffing, standards, governance
model, build vs buy, which trade-offs are acceptable.

**What they care about.**
1. Solution architecture at the logical level: domains, layers, data products
2. Operating model: who owns what (RACI), stewardship, intake, support
3. Data governance, classification, access model, compliance controls
4. Quality and reliability: SLAs/SLOs, DQ framework, incident process
5. Delivery plan: phases, dependencies, team capacity, hiring
6. Cost model and FinOps levers
7. Adoption: who uses it, how they learn it, how success is measured

**Voice.** Clear and structured. Confident about recommendations, explicit about
trade-offs. Uses data vocabulary freely (medallion, CDC, semantic model, SCD2) but
explains anything vendor-specific in one line.

**Format.**
- Executive summary paragraph, then sections
- Logical architecture diagram (layers + domains), 10 to 20 boxes
- Lots of tables: RACI, SLA matrix, phase plan, cost model, risk register
- 4 to 12 pages per doc

---

## 3. Lead Data Engineer

**Who they are.** Builds and runs it. Sets coding standards. Reviews PRs. Gets paged.

**What they need.** Enough detail to build without a meeting: exact layers, naming,
schemas, load patterns, orchestration, testing, CI/CD, environments, security
implementation, observability and runbooks.

**What they care about.**
1. Physical architecture: workspaces/accounts, storage, compute, networking
2. Data models: grain, keys, SCD types, partitioning, clustering
3. Pipeline behavior: incremental logic, idempotency, retries, backfills, late data, schema drift
4. Contracts and tests: what breaks the build vs what alerts
5. Environments and promotion: dev/test/prod, branching, deployment
6. Operability: logging, alerting, lineage, cost per pipeline, runbooks
7. Standards: naming, folder layout, code style, PR checklist

**Voice.** Precise and imperative. "Pipeline PL-004 MUST be idempotent on
`load_date`. Re-running a day overwrites that partition." Uses RFC 2119 words
(MUST, SHOULD, MAY) for standards.

**Format.**
- Physical diagrams, sequence diagrams for key flows, ERDs
- Code blocks: DDL, dbt model skeletons, YAML contracts, config, CLI commands
- Checklists
- Length as needed, but no section without an actionable point

---

## Consistency contract across personas

| Item | Exec | Director | Engineer |
|---|---|---|---|
| Total cost | Annual run-rate + one-time, rounded | Full cost model by component | Cost per pipeline / capacity sizing |
| Timeline | Phases + quarter | Phases + month + dependencies | Sprint-level build order |
| A decision | The choice + why in one line | Choice, alternatives, trade-offs | Full ADR + implementation impact |
| A risk | Top 3-5, plain words | Full register | Technical mitigations in design |
| SLA | "Ready by 6am" | SLA/SLO matrix | Freshness checks, alert thresholds |

All rounded numbers must round FROM the exact number in the facts file.
