# Kickoff prompt

Paste this into Cursor Agent or Claude Code (or type `/data-architecture-docs`
and paste the part under "Project brief"). Fill what you know; delete the rest.
The skill grounds you first, then interviews for the gaps.

---

Use the data-architecture-docs skill. Role: Rōnin.

Produce the full design document set for this data engineering project in
`docs/architecture/`, in three persona packs: CDO/CIO (executive), Data Director,
and Lead Data Engineer, plus the shared glossary, traceability matrix, RAID log
and Phase 7 reviews.

Operating rules for this run:
- Ground first. Get the decision, outcome, terrain, falsifiers, owner and the
  single action in one sentence into the facts file before anything else. One
  question per turn for those six. If a SCROLL.md exists, start from it.
- Survey this repo (dbt, pipelines, notebooks, IaC, CI, semantic models) and
  cite file paths for anything you call existing.
- Build `00-project-facts.yaml` before any doc. Show me the summary and wait for
  corrections. If I say "go", proceed on defaults and log each as an ASSUMPTION.
- ADRs first, using study-the-wind: options plus status quo, a steelman of the
  rejected option, and a falsifiable validation test.
- Then engineer pack, director pack, executive pack. Same facts, different altitude.
- Exec brief in the win-the-room shape. RAID log includes void risks
  (incentives, power, culture, adoption).
- Mermaid for every diagram. No em dashes. No vendor-brochure language.
- Run the validator, the persona consistency check and the reviewer pass
  before you tell me you're done. Be honest about whether reviews were independent.
- Finish with: what you produced, the single action, top 3 open questions,
  top 3 risks. Under 10 lines.

## Project brief
- Project name / code: [e.g. Atlas / atl]
- The decision this makes clearer, and for whom: [ ]
- The single action, in one sentence: [ ]
- Sponsor and what they are judged on: [ ]
- Primary consumers: [ ]
- Phase 1 scope / out of scope: [ ]
- Sources (name, type, access method, sensitivity): [ ]
- Platform and tools, if already chosen: [e.g. Microsoft Fabric, dbt, Power BI, Git on Azure DevOps]
- Layering / modeling preference: [e.g. medallion with Data Vault 2.0 raw vault, Kimball gold]
- Key NFRs: [freshness, history, RPO/RTO, compliance]
- Team: [roles, headcount, hires]
- Budget envelope / licensing owned: [ ]
- Deadline or forcing event: [ ]
- What would prove this approach wrong early: [ ]
- Packs wanted: [all | executive | director | engineer]
