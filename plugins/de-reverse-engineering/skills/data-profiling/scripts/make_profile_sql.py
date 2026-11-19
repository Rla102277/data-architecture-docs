#!/usr/bin/env python3
"""Generate read-only profiling SQL for one table.

    python3 make_profile_sql.py --dialect tsql --table dbo.Orders --columns OrderID,CustomerID,OrderDate,Amount
    python3 make_profile_sql.py --dialect snowflake --table SALES.ORDERS --columns-csv inventory/columns.csv
    python3 make_profile_sql.py ... --keys OrderID --keys CustomerID,OrderDate --sample 1000000

Writes SQL to stdout (or --out file). Standard library only. Dialects: tsql (SQL
Server, Azure SQL, Fabric Warehouse), snowflake, spark (Fabric/Databricks lakehouse).

Queries produced:
  1. column profile: rows, nulls, null %, distinct (approx where supported), min, max,
     min/max length, as one UNION ALL result (one row per column)
  2. top 10 values per column
  3. candidate key checks for each --keys set (duplicates found = not a key)
--sample N profiles a sample instead of the full table (TABLESAMPLE / LIMIT) for big tables.
"""
from __future__ import annotations

import argparse
import csv
import sys

DIALECTS = {
    "tsql": {"str": "CAST({c} AS NVARCHAR(4000))", "len": "LEN({c})", "approx": "APPROX_COUNT_DISTINCT({c})",
             "q": lambda c: f"[{c}]", "sample": "SELECT TOP ({n}) * FROM {t}", "top": "TOP 10 ", "limit": ""},
    "snowflake": {"str": "TO_VARCHAR({c})", "len": "LENGTH(TO_VARCHAR({c}))", "approx": "APPROX_COUNT_DISTINCT({c})",
                  "q": lambda c: f'"{c}"', "sample": "SELECT * FROM {t} SAMPLE ({n} ROWS)", "top": "", "limit": " LIMIT 10"},
    "spark": {"str": "CAST({c} AS STRING)", "len": "LENGTH(CAST({c} AS STRING))", "approx": "approx_count_distinct({c})",
              "q": lambda c: f"`{c}`", "sample": "SELECT * FROM {t} LIMIT {n}", "top": "", "limit": " LIMIT 10"},
}


def columns_from_csv(path: str, table: str) -> list[str]:
    schema, _, name = table.rpartition(".")
    cols = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            low = {k.lower(): v for k, v in row.items()}
            if low.get("table_name", "").lower() == name.lower() and \
               (not schema or low.get("table_schema", "").lower() == schema.lower()):
                cols.append(low["column_name"])
    return cols


def build(dialect: str, table: str, cols: list[str], keys: list[list[str]], sample: int | None) -> str:
    d = DIALECTS[dialect]
    src = f"({d['sample'].format(t=table, n=sample)}) AS s" if sample else f"{table} AS s"
    parts = []
    for c in cols:
        qc = "s." + d["q"](c)
        parts.append(
            f"SELECT '{c}' AS column_name, COUNT(*) AS row_count, "
            f"SUM(CASE WHEN {qc} IS NULL THEN 1 ELSE 0 END) AS null_count, "
            f"{d['approx'].format(c=qc)} AS distinct_approx, "
            f"MIN({d['str'].format(c=qc)}) AS min_value, MAX({d['str'].format(c=qc)}) AS max_value, "
            f"MIN({d['len'].format(c=qc)}) AS min_length, MAX({d['len'].format(c=qc)}) AS max_length "
            f"FROM {src}")
    out = [f"-- Profile of {table} ({dialect}){' sample ' + str(sample) + ' rows' if sample else ''}",
           "-- Read-only. Save results to docs/reverse-engineering/profiles/<table>.csv", "",
           "-- 1) column profile (min and max compare as text, so check numeric and date ranges separately)",
           "\nUNION ALL\n".join(parts) + ";", "", "-- 2) top 10 values per column"]
    for c in cols:
        qc = "s." + d["q"](c)
        out.append(f"SELECT {d['top']}'{c}' AS column_name, {d['str'].format(c=qc)} AS value, COUNT(*) AS n "
                   f"FROM {src} GROUP BY {qc} ORDER BY n DESC{d['limit']};")
    if keys:
        out += ["", "-- 3) candidate key checks: duplicate_groups = 0 and null_rows = 0 means the columns form a key"]
        for k in keys:
            qk = ", ".join("s." + d["q"](c) for c in k)
            nulls = " OR ".join(f"s.{d['q'](c)} IS NULL" for c in k)
            out.append(
                f"SELECT '{'+'.join(k)}' AS key_columns, "
                f"(SELECT COUNT(*) FROM (SELECT {qk} FROM {src} GROUP BY {qk} HAVING COUNT(*) > 1) AS dup) AS duplicate_groups, "
                f"(SELECT COUNT(*) FROM {src} WHERE {nulls}) AS null_rows;")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dialect", choices=sorted(DIALECTS), required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--columns")
    ap.add_argument("--columns-csv")
    ap.add_argument("--keys", action="append", default=[], help="comma list; repeat for more candidate keys")
    ap.add_argument("--sample", type=int)
    ap.add_argument("--out")
    args = ap.parse_args()
    cols = args.columns.split(",") if args.columns else columns_from_csv(args.columns_csv, args.table) if args.columns_csv else []
    if not cols:
        sys.exit("No columns: pass --columns or --columns-csv (inventory/columns.csv)")
    sql = build(args.dialect, args.table, [c.strip() for c in cols], [k.split(",") for k in args.keys], args.sample)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(sql)
    else:
        sys.stdout.write(sql)
    return 0


if __name__ == "__main__":
    sys.exit(main())
