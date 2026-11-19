# Backfill plan: <name>

| Field | Value |
|---|---|
| Reason | |
| Tables / models | |
| Date range | |
| Replay source | raw layer / source system / time travel |
| Chunk size and order | e.g. one month, oldest first |
| Isolation | separate schema and swap / pause downstream refresh |
| Concurrency limit | |
| Estimated duration | per chunk x chunks |
| Estimated cost | warehouse or capacity units, with basis |
| Window | dates and hours; avoid close and reporting days |
| Owner approval | name, date |

## Validation per chunk

| Check | Query or method | Pass rule |
|---|---|---|
| Row count | | matches source within 0 |
| Totals | | matches source within tolerance |

## Rollback

Steps to restore the previous state, and how long they take.

## Communication

Who is told, before and after, and what the change note says.

## Checkpoint log

| Chunk | Started | Ended | Rows | Validation | Status |
|---|---|---|---|---|---|
