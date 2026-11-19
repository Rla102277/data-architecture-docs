# Atlas design docs (fictional example)

**Single action:** Approve $180K and a two-person team by Jan 15 so margin by customer and SKU is ready for the April renewal cycle.

| Reader | Start here |
|---|---|
| CFO / CIO | executive/EXE-01-executive-brief.md |
| Data Director | (not included in this example) |
| Lead Data Engineer | (not included in this example) |

Review verdicts: `reviews/cio-reader.md` (CHANGES, perspective).

Open questions: Q-001 (run budget source, CFO, Jan 15).

This example covers the executive pack only. Validate it with:

```bash
python3 plugins/de-architecture-docs/skills/validate-architecture-docs/scripts/validate_docs.py examples/northwind-distribution/docs/architecture --packs executive
```
