# DAX standards

```dax
Gross Margin % =
VAR _revenue = [Revenue]
VAR _cogs    = [COGS]
RETURN
    DIVIDE ( _revenue - _cogs, _revenue )
```

- Build measures on measures: `[Revenue]` is defined once, everything reuses it.
- `DIVIDE` instead of `/` (handles zero and blank).
- Variables (`VAR`) for any value used twice and for readability.
- Prefix variables with `_` so they never collide with column or measure names.
- Time intelligence on a marked date table: `TOTALYTD`, `SAMEPERIODLASTYEAR`,
  `DATEADD`, or calculation groups for a consistent set across measures.
- Semi-additive balances: `LASTNONBLANKVALUE` or `CALCULATE([Balance], LASTDATE('Date'[Date]))`
  so balances are not summed across months.
- `CALCULATE` filter arguments: prefer column filters (`'Customer'[Segment] = "Retail"`)
  over `FILTER(table, ...)` on whole tables for performance.
- Avoid `IFERROR` and iterators over large facts when a simpler form exists.
- Every measure has a description, a format string and a display folder.
