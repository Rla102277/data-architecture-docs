# <schema>.<procedure>

| Field | Value |
|---|---|
| File | `code/<schema>.<procedure>.PROCEDURE.sql` |
| Purpose (from code) | |
| Purpose (claimed by name/comments) | |
| Called by | jobs, pipelines, procs, apps (with evidence) |
| Runs | frequency and typical duration (proc-stats.csv, job history) |
| Idempotent | yes / no / partly, and why |
| Status | in use / candidate to retire / unknown |

## Signature

| Parameter | Type | Default | Direction | Meaning |
|---|---|---|---|---|

## Steps

1. Lines a-b: <plain-language step>

## Data in and out

| Object | Read / Write | Operation | Lines |
|---|---|---|---|

Temp tables and table variables:

| Name | Built at lines | Used at lines | Holds |
|---|---|---|---|

## Side effects

| Call or effect | Lines | Notes |
|---|---|---|

## Business rules

| ID | Rule in plain words | Code | Lines | Confidence |
|---|---|---|---|---|
| BR-<proc>-01 | | | | high / medium / low |

## Transactions and errors

- Transaction scope:
- XACT_ABORT:
- TRY/CATCH: re-throws? logs where?
- State left after a failure halfway through:

## Risks

| Risk | Lines | Why it matters |
|---|---|---|

## Open questions

- 
