# de-skill-factory (plugin)

Make more data engineering skills to one standard: create a new skill, upgrade a thin skill into a deep one, and eval a skill against a no-skill baseline.

Install in Claude Code:

```
/plugin install de-skill-factory --marketplace Rla102277/data-architecture-docs
```

Cursor and skills-only installs: `docs/INSTALL.md` at the repo root.

| Skill | Use when |
|---|---|
| [create-data-skill](skills/create-data-skill/SKILL.md) | someone wants a new agent skill for a data engineering task: "make a skill for X", "turn how we do Y into a skill", "we keep explaining Z to the agent" |
| [eval-data-skill](skills/eval-data-skill/SKILL.md) | you need to prove a skill or plugin changes agent behavior: run scenario prompts with and without the plugin, grade transcripts against must-include and must-not-include behaviors, compare to a baseline, and report which skills earn their place |
| [upgrade-data-skill](skills/upgrade-data-skill/SKILL.md) | an existing skill is too thin, too generic or not triggering: "this skill doesn't do anything", "deepen the Data Warrior skills", "make this skill follow the standard" |

Every skill follows the factory skill standard and the Data Warrior doctrine (`references/doctrine.md`).
