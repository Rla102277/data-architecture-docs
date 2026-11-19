#!/usr/bin/env python3
"""Table-level lineage from SQL files.

    pip install sqlglot
    python3 extract_lineage.py <sql-file-or-folder>... --dialect tsql --out docs/reverse-engineering/lineage

Reads every *.sql file, splits it into statements, and records an edge
(source -> target) for each statement that writes: INSERT, MERGE, UPDATE,
DELETE, CREATE TABLE AS / SELECT INTO, CREATE VIEW. Writes:

  edges.csv     source,target,operation,file,statement_no
  lineage.md    Mermaid flowchart of all edges
  calls.csv     EXEC calls from one procedure or script to another
  unparsed.md   every statement the parser could not read (review by hand)
  objects.csv   every table seen, with read/write counts

It is honest about gaps: dynamic SQL (EXEC(@sql), sp_executesql) cannot be
resolved statically and is listed in unparsed.md. Temp tables (#t, @t) are
kept as nodes prefixed with the file name so flows through them stay visible.
Dialects: any sqlglot dialect (tsql, snowflake, spark, databricks, postgres, ...).
"""
from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import sqlglot
    from sqlglot import exp
except ImportError:  # pragma: no cover
    sys.exit("sqlglot is required: pip install sqlglot")

logging.getLogger("sqlglot").setLevel(logging.ERROR)

DYNAMIC = re.compile(r"\bEXEC(UTE)?\s*\(|\bsp_executesql\b", re.I)
GO_SPLIT = re.compile(r"^\s*GO\s*;?\s*$", re.I | re.M)


def table_name(t: exp.Table, file_tag: str) -> str:
    ident = t.this if isinstance(t.this, exp.Identifier) else None
    if (ident is not None and (ident.args.get("temporary") or ident.args.get("global"))) \
            or t.name.startswith(("#", "@")):
        return f"{file_tag}::#{t.name.lstrip('#')}"
    parts = [p for p in (t.catalog, t.db, t.name) if p]
    return ".".join(parts).lower()


PROC_HEAD = re.compile(r"\b(?:CREATE|ALTER)\s+(?:OR\s+ALTER\s+)?PROC(?:EDURE)?\s+([\[\]\w.]+).*?\bAS\b", re.I | re.S)


def strip_proc_wrapper(sql: str) -> tuple[str, str | None]:
    """Return (body, procedure name) for CREATE/ALTER PROCEDURE so inner statements parse."""
    m = PROC_HEAD.search(sql)
    if not m:
        return sql, None
    return sql[m.end():], m.group(1).strip("[]").replace("].[", ".").lower()


STARTERS = {"SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "MERGE", "CREATE", "ALTER", "DROP",
            "TRUNCATE", "EXEC", "EXECUTE", "SET", "DECLARE", "PRINT", "RAISERROR", "THROW", "IF",
            "ELSE", "WHILE", "BEGIN", "END", "RETURN", "COMMIT", "ROLLBACK", "OPEN", "FETCH",
            "CLOSE", "DEALLOCATE", "GOTO", "BREAK", "CONTINUE", "USE"}
LEADING_COMMENTS = re.compile(r"^(?:\s*(?:--[^\n]*\n|/\*.*?\*/))*\s*", re.S)
DML = {"SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "MERGE", "CREATE"}
TRUNC = re.compile(r"^\s*TRUNCATE\s+TABLE\s+([\[\]\w.#]+)", re.I)
CALL = re.compile(r"^\s*EXEC(?:UTE)?\s+(?:@\w+\s*=\s*)?([\[\]\w.]+)", re.I)


def _words(sql: str) -> list[tuple[int, str, int, bool]]:
    """(position, UPPER word, paren depth, next non-space char is '(') outside strings/comments."""
    out, i, depth, n = [], 0, 0, len(sql)
    while i < n:
        c = sql[i]
        if c == "'":
            i += 1
            while i < n and not (sql[i] == "'" and (i + 1 >= n or sql[i + 1] != "'")):
                i += 2 if sql[i] == "'" else 1
            i += 1
        elif c == "[":
            i = sql.find("]", i) + 1 or n
        elif sql.startswith("--", i):
            i = sql.find("\n", i) + 1 or n
        elif sql.startswith("/*", i):
            i = sql.find("*/", i) + 2 or n
        elif c == "(":
            depth += 1
            i += 1
        elif c == ")":
            depth = max(0, depth - 1)
            out.append((i, ")", depth, False))
            i += 1
        elif c == ";":
            out.append((i, ";", depth, False))
            i += 1
        elif c.isalpha() or c in "_#@":
            j = i
            while j < n and (sql[j].isalnum() or sql[j] in "_#@$"):
                j += 1
            k = j
            while k < n and sql[k].isspace():
                k += 1
            out.append((i, sql[i:j].upper(), depth, k < n and sql[k] == "("))
            i = j
        else:
            i += 1
    return out


def split_tsql(body: str) -> list[str]:
    """Split a T-SQL batch or procedure body into statements, dropping control flow."""
    cuts, chunk_first, seen_main, case_depth, prev = [0], None, False, 0, ""
    for pos, word, depth, paren_next in _words(body):
        if depth:
            prev = word
            continue
        if word == ")":
            prev = word
            continue
        if word == ";":
            cuts.append(pos + 1)
            chunk_first, seen_main, prev = None, False, ";"
            continue
        if word == "CASE":
            case_depth += 1
        if word == "END" and case_depth:
            case_depth -= 1
            prev = word
            continue
        if word in STARTERS:
            split = True
            if chunk_first == "MERGE":
                split = False  # MERGE runs to its mandatory semicolon
            elif word == "WITH" and paren_next:
                split = False  # table hint WITH (NOLOCK)
            elif prev in {"UNION", "ALL", "EXCEPT", "INTERSECT", "THEN", "INTO", "FOR"}:
                split = False
            elif chunk_first == "WITH" and not seen_main and word in DML - {"WITH", "CREATE"}:
                split, seen_main = False, True
            elif chunk_first == "INSERT" and word in {"SELECT", "WITH", "EXEC", "EXECUTE"}:
                split = False
            elif chunk_first in {"UPDATE", "MERGE"} and word == "SET":
                split = False
            elif chunk_first == "CREATE" and word in {"SELECT", "WITH"} and prev in {"AS", ")"}:
                split = False
            elif word == "BEGIN" and prev == "END":
                split = True
            if split and chunk_first is not None:
                cuts.append(pos)
                chunk_first, seen_main = word, False
            elif chunk_first is None:
                chunk_first = word
        prev = word
    cuts.append(len(body))
    chunks = [body[a:b].strip().rstrip(";").strip() for a, b in zip(cuts, cuts[1:])]
    return [c for c in chunks if c]


def statements(sql: str, dialect: str) -> list[tuple[int, str, object]]:
    out = []
    n = 0
    for batch in GO_SPLIT.split(sql):
        body, proc = strip_proc_wrapper(batch)
        if dialect == "tsql":
            pieces = split_tsql(body)
        else:
            pieces = [body]
        for piece in pieces:
            piece = LEADING_COMMENTS.sub("", piece, count=1)
            first = piece.split(None, 1)[0].upper() if piece.split() else ""
            if dialect == "tsql" and first in {"EXEC", "EXECUTE"}:
                n += 1
                m = CALL.match(piece)
                out.append((n, piece[:400], ("CALL", m.group(1) if m else None, proc)))
                continue
            if first == "TRUNCATE":
                n += 1
                m = TRUNC.match(piece)
                out.append((n, piece[:400], ("TRUNCATE", m.group(1) if m else None, proc)))
                continue
            if dialect == "tsql" and first not in DML:
                continue  # control flow, DECLARE, SET options: no lineage
            try:
                parsed = sqlglot.parse(piece, read=dialect, error_level=sqlglot.ErrorLevel.IGNORE)
            except Exception as err:  # noqa: BLE001
                n += 1
                out.append((n, piece.strip()[:400], err))
                continue
            for stmt in parsed:
                if stmt is None:
                    continue
                n += 1
                out.append((n, stmt.sql(dialect=dialect)[:400], stmt))
    return out


def writes_and_reads(stmt: exp.Expression, tag: str) -> tuple[list[str], list[str], str]:
    targets: list[str] = []
    op = type(stmt).__name__.upper()
    if isinstance(stmt, (exp.Insert, exp.Merge, exp.Update, exp.Delete)):
        t = stmt.this if isinstance(stmt.this, exp.Table) else stmt.find(exp.Table)
        if t is not None:
            if not t.db and isinstance(stmt, (exp.Update, exp.Delete)):
                # T-SQL: UPDATE f ... FROM dw.Fact f  -> resolve the alias
                for cand in stmt.find_all(exp.Table):
                    if cand is not t and cand.alias and cand.alias.lower() == t.name.lower():
                        t = cand
                        break
            targets.append(table_name(t, tag))
    elif isinstance(stmt, exp.Create):
        t = stmt.this.find(exp.Table) if stmt.this is not None else None
        if t is not None and stmt.expression is not None:
            targets.append(table_name(t, tag))
            op = f"CREATE {stmt.args.get('kind', '')}".strip()
    elif isinstance(stmt, exp.Select) and stmt.args.get("into") is not None:
        t = stmt.args["into"].find(exp.Table)
        if t is not None:
            targets.append(table_name(t, tag))
            op = "SELECT INTO"
    if not targets:
        return [], [], op
    ctes = {c.alias_or_name.lower() for c in stmt.find_all(exp.CTE)}
    reads = []
    aliases = {x.alias.lower() for x in stmt.find_all(exp.Table) if x.alias}
    for t in stmt.find_all(exp.Table):
        name = table_name(t, tag)
        if name in targets or t.name.lower() in ctes:
            continue
        if not t.db and t.name.lower() in aliases and not t.alias:
            continue  # bare alias used as UPDATE/DELETE target
        reads.append(name)
    if isinstance(stmt, (exp.Update, exp.Merge)):
        reads = [r for r in reads if r not in targets]
    return targets, sorted(set(reads)), op


def node_id(name: str) -> str:
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--dialect", default="tsql")
    ap.add_argument("--out", default="lineage")
    args = ap.parse_args()

    files: list[Path] = []
    for p in map(Path, args.paths):
        files += sorted(p.rglob("*.sql")) if p.is_dir() else [p]

    edges, unparsed, calls = [], [], []
    reads_count: dict[str, int] = defaultdict(int)
    writes_count: dict[str, int] = defaultdict(int)
    for f in files:
        sql = f.read_text(encoding="utf-8", errors="replace")
        tag = f.stem
        if DYNAMIC.search(sql):
            unparsed.append((str(f), 0, "dynamic SQL present: lineage for dynamic statements is unknown"))
        for n, text, stmt in statements(sql, args.dialect):
            if isinstance(stmt, tuple) and stmt[0] == "TRUNCATE":
                if stmt[1]:
                    tgt = stmt[1].strip("[]").replace("].[", ".").lower()
                    tgt = f"{tag}::{tgt}" if tgt.startswith("#") else tgt
                    writes_count[tgt] += 1
                    edges.append(("(truncate)", tgt, "TRUNCATE", str(f), n))
                continue
            if isinstance(stmt, tuple) and stmt[0] == "CALL":
                callee = (stmt[1] or "").strip("[]").replace("].[", ".").lower()
                if not callee or callee.startswith("@") or callee == "sp_executesql":
                    unparsed.append((str(f), n, f"dynamic call: {text[:200]}"))
                else:
                    calls.append((stmt[2] or tag.lower(), callee, str(f), n))
                continue
            if isinstance(stmt, Exception):
                unparsed.append((str(f), n, f"{type(stmt).__name__}: {text[:200]}"))
                continue
            if isinstance(stmt, exp.Command):
                unparsed.append((str(f), n, f"not analyzable as SQL: {text[:200]}"))
                continue
            targets, reads, op = writes_and_reads(stmt, tag)
            for t in targets:
                writes_count[t] += 1
                if not reads:
                    edges.append(("(literal or no source)", t, op, str(f), n))
                for r in reads:
                    reads_count[r] += 1
                    edges.append((r, t, op, str(f), n))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "edges.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "target", "operation", "file", "statement_no"])
        w.writerows(edges)
    with (out / "calls.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["caller", "callee", "file", "statement_no"])
        w.writerows(calls)
    names = sorted(set(reads_count) | set(writes_count))
    with (out / "objects.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["object", "read_by_statements", "written_by_statements"])
        for nme in names:
            w.writerow([nme, reads_count[nme], writes_count[nme]])
    pairs = sorted({(s, t) for s, t, *_ in edges})
    lines = ["# Lineage (table level)", "", f"{len(pairs)} edges from {len(files)} files.", "", "```mermaid", "flowchart LR"]
    for nme in sorted({x for pr in pairs for x in pr}):
        lines.append(f'  {node_id(nme)}["{nme}"]')
    for s, t in pairs:
        lines.append(f"  {node_id(s)} --> {node_id(t)}")
    lines += ["```", ""]
    (out / "lineage.md").write_text("\n".join(lines), encoding="utf-8")
    ulines = ["# Unparsed or unresolved statements", "",
              "Review each by hand. Lineage above does not include these.", "",
              "| File | Statement | Reason |", "|---|---|---|"]
    for f, n, why in unparsed:
        ulines.append(f"| {f} | {n} | {why.replace('|', '/').replace(chr(10), ' ')} |")
    (out / "unparsed.md").write_text("\n".join(ulines) + "\n", encoding="utf-8")
    print(f"{len(files)} files, {len(edges)} edges, {len(calls)} calls, {len(names)} objects, {len(unparsed)} unparsed -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
