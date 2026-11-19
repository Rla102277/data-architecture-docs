---
doc_id: DIR-01
title: Solution Architecture
persona: data-director
status: draft
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
related: [EXE-02, ENG-01]
---

# {{project_name}}: Solution Architecture

## Executive summary
<!-- One paragraph: what, why this shape, biggest trade-off accepted. -->

## Context and scope
### Business drivers
### In scope / out of scope
### Stakeholders and consumers
| Group | Need | Data products used |
|---|---|---|

## Architecture principles
<!-- 6-10 principles with a one-line rationale each. -->

## Logical architecture
```mermaid
flowchart LR
  %% layers x domains, 10-20 boxes
```
### Layer responsibilities
| Layer | Purpose | Contract with next layer | History kept? |
|---|---|---|---|

### Domains and subject areas
| Domain | Subject areas | Owner | Key sources |
|---|---|---|---|

## Source landscape
| SRC | System | Owner | Access method | Volume | Sensitivity | Refresh need |
|---|---|---|---|---|---|---|

## Integration patterns
<!-- Pattern per source class and why (CDC, watermark, full, API, files, mirroring). Link ADR. -->

## Data products
| DP | Name | Grain | Owner | Consumers | Freshness | Sources |
|---|---|---|---|---|---|---|

## Consumption and semantic layer
<!-- Shared model vs domain models, self-service boundaries, certified content. -->

## Non-functional requirements
| NFR | Category | Target | How measured | Design response |
|---|---|---|---|---|

## Key decisions
| ADR | Decision | Status | Trade-off accepted |
|---|---|---|---|

## Alternatives considered
<!-- The 2-3 credible alternative architectures and why not. -->

## Risks and open questions
<!-- Link RAID log. List only those that affect architecture. -->

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
