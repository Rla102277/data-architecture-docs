# Changelog

## 2.2.0 (2026-11-20)

- New skill `de-quality-ops/cost-value-report`: daily cost and value report from your inputs, the factory
  line's job history and git. Every number labeled MEASURED, ALLOCATED or ASSUMED; savings vs contractors
  and an additional hire shown as ranges; `--install-launchd` runs it every day on macOS.

## 2.1.1 (2026-11-20)

- `job.py retarget`: point a current or future stage at the repo's real paths (recorded in history).
- `validate_docs.py --facts`: validate a doc set in a subfolder against one shared facts file.

## 2.1.0 (2026-11-20): Modernization and the job line

- **de-modernization** (4 skills): `reimagine-data-system` (look at a system and
  design a whole new way, end to end), `current-state-assessment`,
  `target-state-options` (evolve / re-platform / reimagine plus status quo,
  designed backward from decisions), `migration-roadmap` (waves, parity,
  cutover, decommission, kill criteria).
- **de-factory-line**: `job.py`, a standard-library job line. Job types
  reimagine, reverse-engineer, build, migrate, docs and incident; stages name
  their skill and required files; test, review and human gates; SHA-256 artifact
  hashes; reviews go stale on change; tamper check on test logs; `.factory/BOARD.md`.
  Skill `run-factory-job` teaches the agent to drive it and stop for humans.
- 86 skills in 13 plugins; 20 tests.

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
