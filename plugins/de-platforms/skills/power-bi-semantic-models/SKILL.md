---
name: power-bi-semantic-models
description: >-
  Use when designing, reviewing or deploying Power BI semantic models (datasets)
  on Fabric or Power BI: star schema shape, storage mode (Direct Lake, Import,
  DirectQuery, composite), DAX measure standards, calculation groups, RLS and
  OLS with Entra groups, incremental refresh, PBIP and TMDL in Git, deployment
  pipelines, performance with DAX query view and Best Practice Analyzer, and
  working from a Mac.
---

# Power BI Semantic Models

One well-built model, many thin reports, measures everyone trusts.

Follow [references/doctrine.md](references/doctrine.md).

## When to use

- New semantic model on top of marts.
- "Numbers differ between reports." "The report is slow." "How do we version this?"

Not for: visual design of report pages, or mart design (use `dimensional-modeling`).

## Inspect first

1. The marts the model reads, their grain and keys.
2. Storage mode options available on your capacity, and data size.
3. Existing models covering the same facts (consolidate before adding another).
4. Authoring setup. On a Mac there is no Power BI Desktop: author through the
   web (web modeling in the service), TMDL files via Fabric Git integration in
   VS Code, and the DAX query view in the browser where available. Recheck what
   the web editor supports today.

## Procedure

1. **Shape**: star schema from marts. Dimensions filter facts, one-to-many,
   single direction. Hide keys and technical columns. A real date table marked
   as the date table.
2. **Storage mode** in an ADR:
   - Direct Lake (Fabric): reads Delta tables in OneLake without import; know
     the guardrails for your capacity SKU and when queries fall back to DirectQuery.
   - Import: fastest queries, scheduled or incremental refresh, size limits.
   - DirectQuery: live, slower, puts load on the source.
3. **Measures** ([references/dax-standards.md](references/dax-standards.md)):
   explicit measures only (no implicit summarization), `DIVIDE` for ratios,
   variables for readability, format strings and display folders, one
   definition per business metric with a description that names its owner.
4. **Security**: RLS roles mapped to Entra security groups, tested with "view as";
   OLS for sensitive columns. Workspace access does not replace RLS for Viewers.
5. **Refresh**: incremental refresh policies on large Import tables
   (`RangeStart` / `RangeEnd` parameters); refresh triggered after the upstream
   load finishes, not on a guessed clock time.
6. **Source control**: PBIP / TMDL in Git through Fabric Git integration;
   reports separate from the model (thin reports bound to a shared model).
7. **Deploy**: deployment pipelines dev to test to prod with parameter rules for
   connections; endorse (promoted, certified) only after review.
8. **Performance**: measure with DAX query view or Performance Analyzer, check
   model size and cardinality, run Best Practice Analyzer rules (Tabular Editor,
   where available), remove unused columns, avoid bi-directional relationships.

## Standards

- **MUST** use explicit measures with descriptions for every business metric.
- **MUST** test RLS for every role before publishing.
- **MUST** keep one certified model per subject area; reports connect to it.
- **SHOULD** store additive components in marts and compute ratios in measures.
- **SHOULD** avoid calculated columns on large facts when the mart can provide the column.
- **SHOULD** name measures for business users ("Gross Margin %"), not code.

## Failure modes

| Failure | Prevention |
|---|---|
| Same metric defined differently in three reports | One certified model, thin reports |
| Ratio averaged across rows | Measure computes from summed components |
| Bi-directional filters create ambiguous totals | Single direction, explicit `CROSSFILTER` in a measure when needed |
| Direct Lake silently falls back to DirectQuery and slows | Know guardrails; monitor fallback |
| RLS bypassed by workspace roles | Consumers get Viewer and an app, RLS tested |
| Refresh runs before data lands | Refresh triggered by the pipeline |

## Verify

- Key measures match the mart totals for a period (query both).
- RLS: each role sees only its rows ("view as").
- Report page loads within the agreed time on the production capacity.

## Output

The model (TMDL in Git), measure catalog with descriptions, RLS role matrix,
refresh and deploy notes, and an ADR for storage mode.
