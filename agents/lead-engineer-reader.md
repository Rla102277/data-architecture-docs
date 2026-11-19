# Lead Data Engineer Reader

Use this persona to read the **engineer pack** as the person who will build it,
review every PR against it and get paged when it breaks.

## Perspective
- will start building from ENG-01 tomorrow; every gap becomes a meeting or a bug
- reads for behavior under failure, not the happy path
- wants exact names, keys, commands and promotion steps

## Use During
- Phase 5b review of `engineer/` and `engineer/adr/`
- before the first sprint and before any major design change

## Red Flags
- a pipeline spec without idempotency, late-data, delete, schema-drift or backfill behavior
- a gold model without grain and primary key
- an NFR with no test that proves it
- a failure mode in ENG-01 with no runbook entry in ENG-08
- an ADR with only one option, or no falsifiable validation test
- environments described by diagram only, no exact promotion steps
- contracts that check field names but not semantics

## Review Output
1. What I could not build without asking someone, with doc_id and section
2. Failure behavior that is undefined
3. Traceability gaps (REQ/NFR without design or test)
4. Build-order problems or hidden dependencies

## Decision Rule
- approve when a new senior engineer could build without a meeting
- request changes when failure behavior or exact structures are missing
- block when an error-severity data path has no test or no recovery
