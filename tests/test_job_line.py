"""Tests for the factory line CLI (plugins/de-factory-line/.../job.py)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "plugins/de-factory-line/skills/run-factory-job/scripts/job.py"
TYPES = ROOT / "plugins/de-factory-line/skills/run-factory-job/assets/job-types.json"


class JobLineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.run_job("init")
        self.run_job("new", "build", "Make fct_orders incremental", "--by", "tester")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_job(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(JOB), *args], cwd=self.dir, capture_output=True, text=True)

    def job(self) -> dict:
        return json.loads((self.dir / ".factory/jobs/JOB-0001/job.json").read_text())

    def write(self, rel: str, text: str) -> None:
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def to_review(self) -> None:
        self.write(".factory/jobs/JOB-0001/spec.md", "spec")
        self.assertEqual(self.run_job("push", "JOB-0001").returncode, 0)
        self.assertEqual(self.run_job("skip", "JOB-0001", "--reason", "small").returncode, 0)
        self.assertEqual(self.run_job("push", "JOB-0001").returncode, 0)          # build
        self.run_job("test", "JOB-0001", "--", sys.executable, "-c", "pass")
        self.assertEqual(self.run_job("push", "JOB-0001").returncode, 0)          # test
        self.write(".factory/jobs/JOB-0001/review-sql.md", "ok")

    def test_outputs_required(self) -> None:
        r = self.run_job("push", "JOB-0001")
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing output", r.stdout)

    def test_test_gate_needs_passing_test(self) -> None:
        self.write(".factory/jobs/JOB-0001/spec.md", "spec")
        self.run_job("push", "JOB-0001")
        self.run_job("skip", "JOB-0001", "--reason", "small")
        self.run_job("push", "JOB-0001")
        self.assertIn("no test recorded", self.run_job("push", "JOB-0001").stdout)
        self.assertEqual(self.run_job("test", "JOB-0001", "--", sys.executable, "-c", "raise SystemExit(3)").returncode, 3)
        self.assertIn("exit code 3", self.run_job("push", "JOB-0001").stdout)
        self.run_job("test", "JOB-0001", "--", sys.executable, "-c", "pass")
        self.assertEqual(self.run_job("push", "JOB-0001").returncode, 0)
        log = self.dir / self.job()["tests"][-1]["log"]
        self.assertIn("# exit 0", log.read_text())

    def test_review_goes_stale_and_human_gate(self) -> None:
        self.to_review()
        self.run_job("review", "JOB-0001", "--verdict", "PASS", "--by", "reader")
        self.write(".factory/jobs/JOB-0001/review-sql.md", "changed")
        self.assertIn("changed after the review", self.run_job("push", "JOB-0001").stdout)
        self.run_job("review", "JOB-0001", "--verdict", "PASS", "--by", "reader", "--independent")
        self.assertEqual(self.run_job("push", "JOB-0001").returncode, 0)
        self.assertNotEqual(self.run_job("push", "JOB-0001").returncode, 0)                 # human gate
        self.assertNotEqual(self.run_job("approve", "JOB-0001", "--by", "Randy").returncode, 0)  # needs --authorized
        self.write(".factory/jobs/JOB-0001/spec.md", "tampered")
        r = self.run_job("approve", "JOB-0001", "--by", "Randy", "--authorized")
        self.assertEqual(r.returncode, 1)
        self.assertIn("spec.md", r.stdout)
        self.write(".factory/jobs/JOB-0001/spec.md", "spec")
        self.assertEqual(self.run_job("approve", "JOB-0001", "--by", "Randy", "--authorized").returncode, 0)
        self.assertEqual(self.job()["approvals"][0]["by"], "Randy")

    def test_only_optional_stages_skip(self) -> None:
        self.assertNotEqual(self.run_job("skip", "JOB-0001", "--reason", "x").returncode, 0)

    def test_verify_detects_tampered_log(self) -> None:
        self.to_review()
        self.assertEqual(self.run_job("verify", "JOB-0001").returncode, 0)
        log = self.dir / self.job()["tests"][-1]["log"]
        log.write_text("forged")
        self.assertIn("TAMPERED", self.run_job("verify", "JOB-0001").stdout)

    def test_board_and_types_reference_real_skills(self) -> None:
        self.assertIn("JOB-0001", self.run_job("board").stdout)
        skills = {p.parent.name for p in (ROOT / "plugins").rglob("SKILL.md")}
        for name, t in json.loads(TYPES.read_text())["types"].items():
            for s in t["stages"]:
                if s.get("skill"):
                    self.assertIn(s["skill"], skills, f"{name}.{s['id']} names unknown skill {s['skill']}")


if __name__ == "__main__":
    unittest.main()
