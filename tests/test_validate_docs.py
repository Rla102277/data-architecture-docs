"""Tests for skills/data-architecture-docs/scripts/validate_docs.py. Run:

    python3 -m unittest discover -s tests
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "plugins/de-architecture-docs/skills/validate-architecture-docs/scripts/validate_docs.py"
EXE = [
    "EXE-01-executive-brief.md",
    "EXE-02-strategic-architecture-overview.md",
    "EXE-03-investment-and-roadmap.md",
    "EXE-04-risk-and-governance-summary.md",
]
FACTS = textwrap.dedent("""\
    facts_version: 0.1.0
    ground:
      single_action: Approve phase 1 funding by Dec 15 so the ERP feed lands before year-end close.
    risks:
      - id: RSK-001
    nfrs:
      - id: NFR-001
""")


def doc(doc_id: str, body: str) -> str:
    return textwrap.dedent(f"""\
        ---
        doc_id: {doc_id}
        title: Test
        persona: executive
        status: draft
        version: 0.1.0
        last_updated: 2026-11-19
        ---
        # {doc_id}
        {body}

        ## Change log
        | Version | Date | Author | Change |
        |---|---|---|---|
        """)


def build(root: Path, facts: str = FACTS, brief_body: str = "Main risk RSK-001 against NFR-001.") -> None:
    (root / "executive").mkdir(parents=True)
    (root / "reviews").mkdir()
    (root / "00-project-facts.yaml").write_text(facts)
    (root / "README.md").write_text("# Docs\n")
    for name in EXE:
        body = brief_body if name.startswith("EXE-01") else "Content."
        (root / "executive" / name).write_text(doc(name[:6], body))
    (root / "reviews" / "cio-reader.md").write_text("VERDICT: PASS\n\nStands alone.\n")


def run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", str(VALIDATOR), str(root), "--packs", "executive"],
        capture_output=True, text=True,
    )


class ValidateDocsTest(unittest.TestCase):
    def test_clean_pack_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            r = run(Path(d))
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_facts_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            facts = Path(d) / "00-project-facts.yaml"
            moved = Path(d).parent / (Path(d).name + "-facts.yaml")
            facts.rename(moved)
            try:
                self.assertEqual(run(Path(d)).returncode, 1)
                r = subprocess.run([sys.executable, "-I", str(VALIDATOR), d, "--packs", "executive", "--facts", str(moved)],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout)
            finally:
                moved.unlink()

    def test_undefined_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d), brief_body="Depends on NFR-009.")
            r = run(Path(d))
            self.assertEqual(r.returncode, 1)
            self.assertIn("NFR-009", r.stdout)

    def test_untagged_assumption_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d), brief_body="> ASSUMPTION: capacity is F64")
            self.assertIn("marker without an id", run(Path(d)).stdout)

    def test_empty_ground_gate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d), facts=FACTS.replace(
                "single_action: Approve phase 1 funding by Dec 15 so the ERP feed lands before year-end close.",
                "single_action: null"))
            r = run(Path(d))
            self.assertEqual(r.returncode, 1)
            self.assertIn("ground gate incomplete", r.stdout)

    def test_placeholder_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d), brief_body="We recommend {{recommendation}}.")
            self.assertIn("placeholders", run(Path(d)).stdout)

    def test_review_without_verdict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            (Path(d) / "reviews" / "council-guardian.md").write_text("Looks fine.\n")
            r = run(Path(d))
            self.assertEqual(r.returncode, 1)
            self.assertIn("VERDICT", r.stdout)

    def test_em_dash_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d), brief_body="Fast \u2014 and cheap. RSK-001")
            r = run(Path(d))
            self.assertEqual(r.returncode, 0)
            self.assertIn("em dash", r.stdout)

    def test_exec_word_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            build(Path(d), brief_body="word " * 950)
            self.assertIn("ceiling", run(Path(d)).stdout)


if __name__ == "__main__":
    unittest.main()
