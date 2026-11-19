---
name: upgrade-data-skill
description: >-
  Use when an existing skill is too thin, too generic or not triggering: "this
  skill doesn't do anything", "deepen the Data Warrior skills", "make this
  skill follow the standard". Audits the skill against the factory standard,
  rewrites it with real procedure, defaults, failure modes and verification,
  and proves the upgrade with a before/after eval.
---

# Upgrade a Data Skill

Turn a skill that says the right words into one that changes what the agent does.

Follow [references/doctrine.md](references/doctrine.md) and
[references/skill-standard.md](references/skill-standard.md).

## When to use

- A skill under about 30 lines, or one that reads like a slogan.
- A skill that does not trigger when it should.
- Bringing a vendored or older skill up to the factory standard.

Not for: brand-new skills (use `create-data-skill`).

## Inspect first

1. **Ownership.** Where is the canonical copy? A vendored skill (for example in
   `plugins/data-warrior/`) must be upgraded **upstream** in its own repo, then
   synced. Never edit vendored copies in the factory.
2. **The current skill**: front matter, body, references, and what other skills
   call it.
3. **Its eval**, if any. If none exists, write one first so the upgrade can be measured.

## Procedure

1. **Audit** against the standard and write the gaps as a list:
   - description: starts with "Use when"? names the user's words and tools?
   - each required section present and specific?
   - real commands, queries, code? defaults with reasons? named failure modes?
   - a way to verify? a defined output?
2. **Baseline eval**: run the scenario with the current skill and with no skill
   (`eval-data-skill`). Record both scores.
3. **Rewrite**, keeping the skill's intent and voice (and its doctrine, for Data
   Warrior skills), adding:
   - Inspect first: what to read or query before acting
   - Procedure: numbered, concrete steps
   - Standards: MUST / SHOULD with reasons
   - Failure modes table and Verify section with real checks
   - references/assets for detail, so SKILL.md stays readable
4. **Keep compatibility**: same `name` (callers depend on it); same command vs
   discipline role (`disable-model-invocation` unchanged unless that is the bug).
5. **After eval**: rerun. The upgrade ships only if it scores higher than both
   the old skill and the baseline, without new `must_not_include` hits.
6. **Ship**: in the factory, `build.py` and `verify_repo.py`; upstream, a PR with
   the before/after eval results in the description.

## Standards

- **MUST** measure before and after; an upgrade with no eval is a rewrite by taste.
- **MUST** upgrade vendored skills upstream, then sync.
- **MUST** keep the skill's name and contract with its callers.
- **SHOULD** preserve the author's voice and doctrine while adding substance.

## Failure modes

| Failure | Prevention |
|---|---|
| Upgrade edits a vendored copy and is lost on the next sync | Upstream first, then sync |
| Longer skill, same behavior | Before/after eval gate |
| Renamed skill breaks commands that call it | Name kept |
| Voice and doctrine lost in the rewrite | Intent and voice preserved explicitly |

## Verify

Eval results table: baseline, old skill, upgraded skill, with must-include hits
and must-not-include hits for each scenario.

## Output

The upgraded skill (or upstream PR), its eval scenario, and the before/after results.
