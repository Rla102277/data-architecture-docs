# Ingestion patterns

| Pattern | Catches updates | Catches deletes | Source load | Complexity | Use when |
|---|---|---|---|---|---|
| Full snapshot | Yes | Yes (by absence) | High per run | Low | Small tables, or no reliable change signal |
| Timestamp watermark | If timestamp is reliable | No | Low | Low | Reliable `updated_at`, deletes rare or handled separately |
| SQL Server change tracking | Yes (net changes) | Yes | Low | Medium | SQL Server source, need net changes and deletes, no column history |
| CDC (SQL Server CDC, Debezium, log-based) | Yes (every change) | Yes | Low | Medium-high | Need every change, deletes, or near real time |
| Mirroring / replication (Fabric mirroring, Snowflake connectors) | Yes | Yes | Low | Low to run, platform-bound | Supported source and target pair, accept the platform's limits |
| API incremental (since / cursor) | Depends on API | Rarely | Rate-limited | Medium | SaaS sources |
| File drops | Depends on producer | Only if producer sends them | None | Low-medium | Partners and exports |

## CDC vs watermark, honestly

- Watermark is simpler and works anywhere a trustworthy timestamp exists. It
  misses hard deletes and any change that does not touch the timestamp.
- CDC catches everything the log sees, including deletes, but needs source
  configuration, retention monitoring, and handling of high change volumes.
- Common answer: CDC or change tracking for the few tables where deletes or
  silent updates matter, watermark for append-mostly tables, snapshots for small
  reference tables. Decide per table class, not once for everything.

## Late data

Choose an overlap window from evidence: the maximum observed lag between the
event time and when the row became visible in the source, plus margin. Measure
it from history before picking a number.
