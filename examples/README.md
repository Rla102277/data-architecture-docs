# Examples

| Example | What it shows |
|---|---|
| [northwind-distribution](northwind-distribution/BRIEF.md) | Fictional distributor. Kickoff brief, a facts file with a full ground gate, a complete executive pack (EXE-01..04) in the win-the-room shape, and a CIO reader review with real findings. |

The example covers the executive pack only, and passes the linter:

```bash
python3 plugins/data-architecture-docs/skills/validate-architecture-docs/scripts/validate_docs.py \
  examples/northwind-distribution/docs/architecture --packs executive
```

All companies, people and numbers are invented.
