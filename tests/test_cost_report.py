"""Tests for cost_report.py. Run: python3 -m unittest discover -s tests"""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "plugins" / "de-quality-ops" / "skills" / "cost-value-report" / "scripts" / "cost_report.py"
JOB = ROOT / "plugins" / "de-factory-line" / "skills" / "run-factory-job" / "scripts" / "job.py"


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True, cwd=cwd)


class CostReportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        run(str(JOB), "init", cwd=self.repo)
        run(str(JOB), "new", "build", "Thing", cwd=self.repo)
        self.inputs = self.repo / "docs" / "reports" / "inputs"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def report(self) -> tuple[str, list[dict]]:
        r = run(str(REPORT), "--repo", ".", "--project", "Foundation", "--date", "2026-11-20", cwd=self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = self.repo / "docs" / "reports" / "daily"
        with (out / "2026-11-20.csv").open(newline="") as fh:
            return (out / "2026-11-20.md").read_text(), list(csv.DictReader(fh))

    def test_no_inputs_never_invents_numbers(self) -> None:
        md, rows = self.report()
        self.assertIn("Foundation cost and value report", md)
        self.assertIn("Missing: assumptions.csv `contractor_hourly_low`", md)
        self.assertIn("Missing: time-log.csv", md)
        self.assertNotIn("Savings vs contractor", md)
        self.assertTrue(all(r["value"] in ("", "0", "0.0") for r in rows if r["label"] == "ASSUMED"))

    def test_full_inputs(self) -> None:
        self.assertEqual(run(str(REPORT), "--repo", ".", "--init", cwd=self.repo).returncode, 0)
        (self.inputs / "assumptions.csv").write_text(
            "key,value,source,as_of\ntracking_start,2026-11-16,,\ncursor_monthly_cost,30,,\nmy_loaded_hourly,100,,\n"
            "contractor_hourly_low,100,,\ncontractor_hourly_high,200,,\ncontractor_hours_per_week,40,,\n"
            "fte_loaded_annual,180000,,\nfte_hours_per_year,1800,,\nfte_hiring_lead_weeks,10,,\nfte_ramp_weeks,6,,\n")
        (self.inputs / "time-log.csv").write_text(
            "date,job_id,stage,hours,note\n# 2026-11-20,JOB-0001,x,99,EXAMPLE\n2026-11-20,JOB-0001,spec,2,\n2026-11-19,JOB-0001,spec,3,\n")
        (self.inputs / "baseline-estimates.csv").write_text(
            "deliverable,job_id,delivered_on,traditional_hours_low,traditional_hours_high,estimated_by,method\n"
            "Spec,JOB-0001,2026-11-20,40,80,Randy,history\nLater,JOB-0001,2026-12-31,500,900,Randy,history\n")
        az = "UsageDate,ServiceName,CostInBillingCurrency\n11/20/2026,Fabric,10.00\n2026-11-19,Fabric,5\n"
        (self.inputs / "azure-cost" / "a.csv").write_text(az)
        (self.inputs / "azure-cost" / "b.csv").write_text(az)  # overlapping export
        md, rows = self.report()
        val = {r["metric"]: float(r["value"]) for r in rows if r["value"] != ""}
        self.assertEqual(val["To date: my hours"], 5.0)        # EXAMPLE row ignored
        self.assertEqual(val["To date: Azure"], 15.0)          # de-duplicated
        self.assertEqual(val["traditional hours low"], 40.0)   # future delivery excluded
        self.assertEqual(val["contractor cost high"], 16000.0)
        self.assertAlmostEqual(val["To date: Cursor"], 5 * 1.0, places=2)
        self.assertIn("Savings vs contractor", md)
        self.assertIn("to", md.split("Savings vs contractor:")[1].splitlines()[0])  # a range
        self.assertNotIn("—", md)


if __name__ == "__main__":
    unittest.main()
