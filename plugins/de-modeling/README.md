# de-modeling (plugin)

Data modeling for analytics: Kimball dimensional modeling (grain, conformed dimensions, SCD, fact types) and Data Vault 2.0 (hubs, links, satellites, hash keys, PIT and bridge, AutomateDV).

Install in Claude Code:

```
/plugin install de-modeling --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [data-vault-modeling](skills/data-vault-modeling/SKILL.md) | designing, building or reviewing a Data Vault 2.0 layer: hubs, links, satellites, hash keys and hashdiffs, multi-source and multi-active satellites, effectivity satellites, PIT and bridge tables, the business vault, and information marts on top, built with dbt packages such as AutomateDV or datavault4dbt on Fabric, Snowflake or SQL Server |
| [dimensional-modeling](skills/dimensional-modeling/SKILL.md) | designing or reviewing analytics tables for reporting and BI: Kimball star schemas, choosing the grain, fact types (transaction, periodic snapshot, accumulating snapshot, factless), conformed dimensions, slowly changing dimensions (Type 1, 2, 3, mini-dimensions), surrogate keys, date dimensions, role-playing and junk dimensions, and bus matrices for Power BI and other tools |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
