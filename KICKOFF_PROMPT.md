# Kickoff prompt

Paste this into Cursor Agent (or type `/data-architecture-docs` and paste the
part under "Project brief"). Fill the brackets or delete lines you do not know;
the skill will interview you for the rest.

---

Use the data-architecture-docs skill.

Produce the full design document set for this data engineering project in
`docs/architecture/`, in three persona packs: CDO/CIO (executive), Data Director,
and Lead Data Engineer, plus the shared glossary, traceability matrix and RAID log.

Operating rules for this run:
- Scan this repo first (dbt, pipelines, notebooks, IaC, CI, semantic models) and
  cite file paths for anything you describe as existing.
- Build `00-project-facts.yaml` before writing any doc. Show me the summary and
  wait for my corrections. If I say "go", proceed on defaults and log every
  default as an ASSUMPTION with an ID.
- Write ADRs first, then engineer pack, then director pack, then executive pack.
- Same facts across all packs. Different altitude only.
- Mermaid for every diagram. No em dashes. No vendor-brochure language.
- Run the validator and the persona consistency check before you tell me you're done.
- Finish with: what you produced, top 3 open questions, top 3 risks. Under 10 lines.

## Project brief
- Project name / code: [e.g. Foundation / fdn]
- Problem in one sentence: [ ]
- Sponsor and what they are judged on: [ ]
- Primary consumers: [ ]
- Phase 1 scope / out of scope: [ ]
- Sources (name, type, access method, sensitivity): [ ]
- Target platform and tools: [e.g. Microsoft Fabric, OneLake, dbt, Fabric Data Factory, Power BI, Git on Azure DevOps]
- Layering / modeling preference: [e.g. medallion with Data Vault 2.0 raw vault, Kimball gold]
- Key NFRs: [freshness, history, RPO/RTO, compliance]
- Team: [roles, headcount, hires]
- Budget envelope / licensing owned: [ ]
- Deadline or forcing event: [ ]
- Packs wanted: [all | executive | director | engineer]
