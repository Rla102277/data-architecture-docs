"""Tests for the factory's tools. Run: python3 -m unittest discover -s tests"""
from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RE = ROOT / "plugins" / "de-reverse-engineering" / "skills"
FIX = ROOT / "evals" / "fixtures" / "legacy-warehouse"
HAS_SQLGLOT = importlib.util.find_spec("sqlglot") is not None


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True, cwd=cwd)


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@unittest.skipUnless(HAS_SQLGLOT, "sqlglot not installed (pip install sqlglot)")
class LineageTest(unittest.TestCase):
    def test_tsql_procs_views_and_calls(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            r = run(str(RE / "lineage-extraction/scripts/extract_lineage.py"), str(FIX / "code"),
                    "--dialect", "tsql", "--out", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            edges = {(e["source"], e["target"]) for e in rows(Path(out) / "edges.csv")}
            stage = "dbo.usp_LoadSales.PROCEDURE::#stage"
            for edge in [("src.orders", stage), ("src.orderlines", stage), (stage, "dw.factsales"),
                         ("dw.dimcustomer", "dw.factsales"), ("src.refunds", "dw.factsales"),
                         ("dw.factsales", "rpt.vsalesbycustomer"), ("dw.dimcustomer", "rpt.vsalesbycustomer")]:
                self.assertIn(edge, edges)
            self.assertNotIn(("dw.factsales", "f"), edges)  # UPDATE alias resolved
            calls = {(c["caller"], c["callee"]) for c in rows(Path(out) / "calls.csv")}
            self.assertIn(("dbo.usp_nightly", "dbo.usp_loadsales"), calls)
            self.assertIn("sp_executesql", (Path(out) / "unparsed.md").read_text())


class EtlPackageTest(unittest.TestCase):
    def test_ssis_and_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            r = run(str(RE / "etl-package-analysis/scripts/analyze_etl_package.py"), str(FIX / "etl"), "--out", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            ssis = (Path(out) / "LoadSales.md").read_text()
            self.assertIn("Password=***", ssis)
            self.assertNotIn("NOT-A-REAL-SECRET", ssis)
            self.assertIn("built by expression", ssis)
            pl = (Path(out) / "pl_nightly.md").read_text()
            self.assertIn("| Copy Orders | Load Fact | Succeeded |", pl)
            self.assertEqual(pl.count("SQL built by expression"), 1)  # nested activity not double counted
            sqls = {p.name: p.read_text() for p in (Path(out) / "sql").glob("*.sql")}
            self.assertTrue(any("EXEC dbo.usp_LoadSales" in s for s in sqls.values()))


class ProfileSqlTest(unittest.TestCase):
    def test_key_check_detects_duplicates(self) -> None:
        r = run(str(RE / "data-profiling/scripts/make_profile_sql.py"), "--dialect", "spark",
                "--table", "orders", "--columns", "OrderID,Amount", "--keys", "OrderID")
        self.assertEqual(r.returncode, 0, r.stderr)
        sql = r.stdout.replace("approx_count_distinct(", "COUNT(DISTINCT ")
        con = sqlite3.connect(":memory:")
        con.execute("create table orders(OrderID int, Amount real)")
        con.executemany("insert into orders values(?,?)", [(1, 10), (2, None), (2, 5)])
        results = []
        for stmt in sql.split(";"):
            body = "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("--")).strip()
            if body:
                results.append(con.execute(body).fetchall())
        profile = {row[0]: row for row in results[0]}
        self.assertEqual(profile["OrderID"][1:4], (3, 0, 2))   # rows, nulls, distinct
        self.assertEqual(profile["Amount"][2], 1)               # one null amount
        self.assertEqual(results[-1][0][1], 1)                  # one duplicate group: OrderID is not a key


class EvalGradeTest(unittest.TestCase):
    def test_grade(self) -> None:
        spec = importlib.util.spec_from_file_location("run_evals", ROOT / "scripts" / "run_evals.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        g = mod.grade("Use NOT EXISTS. Avoid NOLOCK.", [r"NOT EXISTS", r"half-open"], [r"hunter2"])
        self.assertEqual(g["score"], 0.5)
        g = mod.grade("NOT EXISTS ... hunter2", [r"NOT EXISTS"], [r"hunter2"])
        self.assertEqual(g["score"], 0.75)

    def test_dry_run(self) -> None:
        r = run(str(ROOT / "scripts" / "run_evals.py"), "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("headless runs", r.stdout)


class NewSkillTest(unittest.TestCase):
    def test_scaffold_in_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "repo"
            shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "results", "__pycache__"))
            r = run(str(dst / "scripts" / "new_skill.py"), "--plugin", "de-dbt", "--name", "dbt-snapshots-test",
                    "--trigger", "tracking history with dbt snapshots")
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            skill = dst / "plugins/de-dbt/skills/dbt-snapshots-test"
            self.assertTrue((skill / "SKILL.md").exists())
            self.assertTrue((skill / "references/doctrine.md").exists())
            self.assertTrue((dst / "evals/scenarios/de-dbt/dbt-snapshots-test.json").exists())
            catalog = json.loads((dst / "catalog/skills.json").read_text())
            self.assertIn("dbt-snapshots-test", {c["skill"] for c in catalog})
            dup = run(str(dst / "scripts" / "new_skill.py"), "--plugin", "de-dbt", "--name", "dbt-snapshots-test",
                      "--trigger", "x")
            self.assertNotEqual(dup.returncode, 0)


if __name__ == "__main__":
    unittest.main()
