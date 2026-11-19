# Third-party notices

This repo includes material from the following projects. Each keeps its own
license. Vendored folders carry the upstream LICENSE and an UPSTREAM.md with the
source commit.

## The Data Warrior
- Source: https://github.com/Rla102277/The-data-warrior-agent
- License: MIT, Copyright (c) 2026 THE DATA WARRIOR contributors
- Included: `plugins/data-warrior/` (31 skills, THE_WAY.md, WELCOME.md, ROLE-BEHAVIOR.md, PARITY.md), synced by `scripts/sync_upstream.py`
- Adapted ideas (rewritten, not copied): ground gate, study-the-wind ADR discipline, win-the-room brief shape, void risks, Council lenses, Deshi / Rōnin / Kensei roles

## gordonmurray/data-engineering-skills
- Source: https://github.com/gordonmurray/data-engineering-skills
- License: MIT, Copyright (c) 2025 Gordon Murray. Note: the `firn` skill's front matter declares `license: Apache-2.0`; follow that for that skill.
- Included: `plugins/gordonmurray-data-engineering/` (9 skills), synced by `scripts/sync_upstream.py`

## vaquarkhan/data-engineering-agent-skills
- Source: https://github.com/vaquarkhan/data-engineering-agent-skills
- License: MIT, Copyright (c) 2026
- Included, modified (YAML front matter and an Output section added so they run as read-only subagents):
  `plugins/data-architecture-docs/agents/data-architect.md`, `analytics-engineer-reviewer.md`,
  `data-platform-reliability-reviewer.md`, `data-platform-infrastructure-reviewer.md`,
  `data-security-and-compliance-auditor.md`
- Included unchanged:
  `plugins/data-architecture-docs/skills/data-contracts/assets/source-contract.yaml`,
  `dataset-contract.yaml`, `metric-contract.yaml`;
  `plugins/data-architecture-docs/skills/engineer-pack/assets/plans/backfill-plan.yaml`,
  `schema-change-plan.yaml`, `release-gate-evidence.yaml`

## MADR
- Source: https://github.com/adr/madr
- The ADR template follows the MADR structure; no files copied.

---

MIT License text (applies to each MIT project above, with its own copyright line):

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
