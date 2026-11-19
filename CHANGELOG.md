# Changelog

## 2.0.0 (2026-11-19): Data Engineering Factory

Rewritten from a single docs plugin into a skill factory for data engineers.

- **New plugins (32 new skills):** de-reverse-engineering (8), de-sql (4),
  de-dbt (4), de-modeling (2), de-pipelines (3), de-platforms (4),
  de-quality-ops (4), de-skill-factory (3).
- **Tested tools inside skills:** T-SQL-aware lineage extractor (procs,
  control flow, MERGE, temp tables, UPDATE aliases, EXEC calls, TRUNCATE,
  dynamic SQL listed as unparsed), SSIS / ADF / Fabric package analyzer
  (password masking, run-time SQL flagged), profiling SQL generator with
  candidate key checks.
- **Factory:** skill standard (`factory/SKILL_STANDARD.md`) enforced by
  `verify_repo.py`; doctrine built into every skill; `new_skill.py` scaffolder;
  generated skill catalog; eval scenarios for all 41 first-party skills and
  `run_evals.py` (with vs without plugin, transcripts saved).
- **de-architecture-docs** (renamed from data-architecture-docs): all 9 skills
  rewritten to the standard.
- Marketplace renamed `data-engineering-factory`. Plugin icons. Category moved to
  marketplace entries. Claude Code validator clean.

## 1.0.0 (2026-11-19)

- Restructured into a plugin marketplace: data-architecture-docs split into nine
  skills, reviewer subagents, generated manifests, installer.

## 0.2.0 (2026-11-19)

- Data Warrior ground gate, study-the-wind ADRs, win-the-room brief, void risks.
  Vendored Data Warrior and gordonmurray. vaquarkhan contracts and reviewers.

## 0.1.0 (2026-11-19)

- First version: one skill, persona-tiered templates, facts file, validator.
