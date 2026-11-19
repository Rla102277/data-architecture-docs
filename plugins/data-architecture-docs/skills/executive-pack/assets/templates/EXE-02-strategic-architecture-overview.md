---
doc_id: EXE-02
title: Strategic Architecture Overview
persona: executive
status: draft
version: 0.1.0
owner: {{owner_role}}
last_updated: {{date}}
facts_version: {{facts_version}}
related: [EXE-01, DIR-01]
---

# {{project_name}}: Strategic Architecture Overview

## In one paragraph
<!-- What we are building, for whom, and why this shape. No tool names unless the tool is the decision. -->

## The picture
<!-- Max 7 boxes, business labels. Sources -> platform -> outcomes. -->
```mermaid
flowchart LR
  a[Business systems] --> b[One governed data platform] --> c[Trusted reports and analytics]
```

## What changes for the business
| Today | After |
|---|---|

## Capabilities we gain
<!-- 4-6 capabilities, one line each, e.g. "Point-in-time financial reporting for audits". -->

## What we retire or simplify
<!-- Old tools, spreadsheets, manual processes. Include savings if known. -->

## Why this approach
<!-- The 2-3 big decisions in one line each, with the alternative we did not pick. Link ADRs. -->
| Decision | Why | Instead of |
|---|---|---|

## Principles we will hold to
<!-- 4-6 principles, e.g. "One definition per metric", "Security by default", "Buy before build for commodity ingestion". -->

## Change log
| Version | Date | Author | Change |
|---|---|---|---|
