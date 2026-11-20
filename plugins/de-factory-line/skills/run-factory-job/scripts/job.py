#!/usr/bin/env python3
"""The factory line: push data engineering jobs through stages with evidence and gates.

Standard library only. State lives in the repo you work in, under .factory/,
so it is versioned with the work.

    job.py init                                    # create .factory/ in this repo
    job.py types                                   # list job types and their stages
    job.py new reimagine "Replace the SSIS sales warehouse"
    job.py list | board                            # all jobs | write .factory/BOARD.md
    job.py next JOB-0001                           # what to do now: stage, skill, outputs, gate
    job.py push JOB-0001 [--note "..."]            # check outputs and gate, move to the next stage
    job.py skip JOB-0001 --reason "..."            # skip an optional stage
    job.py test JOB-0001 -- python3 validate_docs.py docs/architecture
    job.py review JOB-0001 --verdict PASS --by "lead-engineer-reader" [--file r.md] [--independent]
    job.py approve JOB-0001 --by "Randy Archambault" --authorized [--note "..."]
    job.py block JOB-0001 --reason "..." | unblock JOB-0001
    job.py retarget JOB-0001 --stage review --outputs "docs/x/reviews/*.md" --reason "..."
                                                   # point a current or future stage at the repo's real paths
    job.py verify JOB-0001                         # re-hash evidence, report changed or missing files
    job.py show JOB-0001

Gates:
  test    a test recorded at this stage with exit code 0, after the stage's latest change
  review  a PASS review recorded at this stage, and no artifact changed since that review
  human   only `approve --authorized` passes it; it re-checks every earlier test and review
          (a review goes stale if any file it covered changed afterwards) and that no artifact is missing

`--authorized` is an attestation that the named human approved, not proof of
identity. Agents must only pass it when the human gave the approval in words.
"""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import glob
import hashlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

TYPES_FILE = Path(__file__).resolve().parents[1] / "assets" / "job-types.json"
FACTORY = ".factory"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def find_root(start: Path) -> Path | None:
    for p in [start, *start.parents]:
        if (p / FACTORY).is_dir():
            return p
    return None


def load_types() -> dict:
    return json.loads(TYPES_FILE.read_text(encoding="utf-8"))["types"]


class Line:
    def __init__(self, root: Path):
        self.root = root
        self.jobs = root / FACTORY / "jobs"

    def path(self, job_id: str) -> Path:
        return self.jobs / job_id / "job.json"

    def load(self, job_id: str) -> dict:
        p = self.path(job_id)
        if not p.exists():
            sys.exit(f"No job {job_id}. Try: job.py list")
        return json.loads(p.read_text(encoding="utf-8"))

    def save(self, job: dict) -> None:
        p = self.path(job["id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")
        tmp.replace(p)

    def all(self) -> list[dict]:
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.jobs.glob("JOB-*/job.json"))]

    def resolve(self, job: dict, pattern: str) -> list[Path]:
        pat = pattern.replace("{id}", job["id"])
        return sorted(Path(p) for p in glob.glob(str(self.root / pat), recursive=True) if Path(p).is_file())

    def snapshot(self, job: dict) -> dict[str, str]:
        """Current hashes of every artifact recorded on the job."""
        out = {}
        for rel in sorted(job["artifacts"]):
            p = self.root / rel
            out[rel] = sha(p) if p.exists() else "MISSING"
        return out


def stage(job: dict) -> dict | None:
    i = job["stage_index"]
    return job["stages"][i] if i < len(job["stages"]) else None


def event(job: dict, kind: str, by: str, **details) -> None:
    job["history"].append({"at": now(), "event": kind, "by": by,
                           "stage": (stage(job) or {}).get("id"), **details})


def actor(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    try:
        name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    except OSError:
        name = ""
    return name or getpass.getuser()


def snapshot_digest(snap: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(snap, sort_keys=True).encode()).hexdigest()


def stage_changed_at(job: dict, stage_id: str) -> str:
    """Latest time this stage's artifacts were recorded or the stage started."""
    times = [h["at"] for h in job["history"] if h.get("stage") == stage_id and h["event"] in ("entered", "artifacts")]
    return max(times) if times else "0"


def gate_problems(line: Line, job: dict, st: dict) -> list[str]:
    problems = []
    gate = st.get("gate")
    if gate == "test":
        since = stage_changed_at(job, st["id"])
        tests = [t for t in job["tests"] if t["stage"] == st["id"] and t["at"] >= since]
        if not tests:
            problems.append("test gate: no test recorded at this stage (job.py test ID -- <command>)")
        elif tests[-1]["exit_code"] != 0:
            problems.append(f"test gate: latest test failed with exit code {tests[-1]['exit_code']}")
    if gate == "review":
        reviews = [r for r in job["reviews"] if r["stage"] == st["id"]]
        if not reviews or reviews[-1]["verdict"] != "PASS":
            problems.append("review gate: latest review at this stage is not PASS")
        else:
            current = line.snapshot(job)
            stale = [f for f, h in reviews[-1]["files"].items() if current.get(f) != h]
            if stale:
                problems.append("review gate: changed after the review, review again: " + ", ".join(stale))
    return problems


def record_outputs(line: Line, job: dict, st: dict) -> list[str]:
    missing = []
    found_any = False
    for pattern in st.get("outputs", []):
        files = line.resolve(job, pattern)
        if not files:
            missing.append(pattern.replace("{id}", job["id"]))
        for f in files:
            rel = f.relative_to(line.root).as_posix()
            job["artifacts"][rel] = {"sha256": sha(f), "stage": st["id"], "at": now()}
            found_any = True
    if found_any:
        event(job, "artifacts", actor(), count=len(job["artifacts"]))
    return missing


def advance(job: dict, by: str, kind: str, **details) -> None:
    event(job, kind, by, **details)
    job["stage_index"] += 1
    nxt = stage(job)
    if nxt is None:
        job["status"] = "done"
        event(job, "done", by)
    else:
        job["status"] = "awaiting_approval" if nxt.get("gate") == "human" else "open"
        event(job, "entered", by)


def cmd_init(args, root: Path) -> int:
    base = root / FACTORY
    (base / "jobs").mkdir(parents=True, exist_ok=True)
    readme = base / "README.md"
    if not readme.exists():
        readme.write_text("# Factory line\n\nJobs, evidence and approvals for work done with the Data Engineering Factory.\n"
                          "Run `job.py board` for status. Do not edit job.json files by hand.\n", encoding="utf-8")
    print(f"Factory line ready at {base}")
    return 0


def cmd_types(args, line: Line | None) -> int:
    for name, t in load_types().items():
        print(f"{name}: {t['description']}")
        print("   " + " -> ".join(s["id"] + (f"[{s['gate']}]" if s.get("gate") else "") +
                                  ("?" if s.get("optional") else "") for s in t["stages"]))
    return 0


def cmd_new(args, line: Line) -> int:
    types = load_types()
    if args.type not in types:
        sys.exit(f"Unknown job type {args.type}. Types: {', '.join(types)}")
    n = len(list(line.jobs.glob("JOB-*"))) + 1
    job_id = f"JOB-{n:04d}"
    job = {"id": job_id, "type": args.type, "title": args.title, "created_at": now(), "created_by": actor(args.by),
           "status": "open", "stage_index": 0, "stages": types[args.type]["stages"],
           "artifacts": {}, "tests": [], "reviews": [], "approvals": [], "history": []}
    event(job, "created", job["created_by"])
    event(job, "entered", job["created_by"])
    if job["stages"][0].get("gate") == "human":
        job["status"] = "awaiting_approval"
    line.save(job)
    (line.jobs / job_id / "evidence").mkdir(exist_ok=True)
    print(f"{job_id} created ({args.type}): {args.title}")
    return cmd_next(argparse.Namespace(id=job_id), line)


def cmd_list(args, line: Line) -> int:
    for j in line.all():
        st = stage(j)
        print(f"{j['id']}  {j['type']:<16} {j['status']:<18} {(st or {}).get('id', '-'):<14} {j['title']}")
    return 0


def cmd_next(args, line: Line) -> int:
    job = line.load(args.id)
    st = stage(job)
    if st is None:
        print(f"{job['id']} is done.")
        return 0
    print(f"{job['id']} [{job['type']}] {job['title']}")
    print(f"Stage {job['stage_index'] + 1}/{len(job['stages'])}: {st['id']}   status: {job['status']}")
    if st.get("skill"):
        print(f"Use skill: {st['skill']}")
    outs = [o.replace("{id}", job["id"]) for o in st.get("outputs", [])]
    if outs:
        print("Must leave: " + ", ".join(outs))
    if st.get("gate"):
        print(f"Gate: {st['gate']}")
    if st.get("note"):
        print(f"Note: {st['note']}")
    if st.get("optional"):
        print("Optional: may be skipped with job.py skip ID --reason \"...\"")
    if st.get("gate") == "human":
        print("STOP: a human must approve this stage (job.py approve ID --by NAME --authorized).")
    return 0


def cmd_push(args, line: Line) -> int:
    job = line.load(args.id)
    st = stage(job)
    if st is None:
        sys.exit(f"{job['id']} is already done")
    if job["status"] == "blocked":
        sys.exit(f"{job['id']} is blocked: unblock it first")
    if st.get("gate") == "human":
        sys.exit(f"Stage {st['id']} needs a human: job.py approve {job['id']} --by NAME --authorized")
    missing = record_outputs(line, job, st)
    problems = [f"missing output: {m}" for m in missing] + gate_problems(line, job, st)
    if problems:
        line.save(job)
        print(f"Cannot push {job['id']} past {st['id']}:")
        for p in problems:
            print(f"  - {p}")
        return 1
    advance(job, actor(), "pushed", note=args.note or "")
    line.save(job)
    print(f"{job['id']}: {st['id']} done")
    return cmd_next(argparse.Namespace(id=job["id"]), line)


def cmd_skip(args, line: Line) -> int:
    job = line.load(args.id)
    st = stage(job)
    if not st or not st.get("optional"):
        sys.exit("Only optional stages can be skipped")
    advance(job, actor(), "skipped", reason=args.reason)
    line.save(job)
    print(f"{job['id']}: skipped {st['id']} ({args.reason})")
    return cmd_next(argparse.Namespace(id=job["id"]), line)


def cmd_test(args, line: Line) -> int:
    job = line.load(args.id)
    st = stage(job)
    if st is None:
        sys.exit(f"{job['id']} is done")
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        sys.exit("Give a command after --")
    record_outputs(line, job, st)
    started = now()
    try:
        r = subprocess.run(command, cwd=line.root, capture_output=True, text=True)
        code, out, err = r.returncode, r.stdout, r.stderr
    except FileNotFoundError as e:
        code, out, err = 127, "", str(e)
    n = len(job["tests"]) + 1
    log = line.jobs / job["id"] / "evidence" / f"test-{n:03d}-{st['id']}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(f"$ {shlex.join(command)}\n# started {started}\n# exit {code}\n\n[stdout]\n{out}\n[stderr]\n{err}\n",
                   encoding="utf-8")
    job["tests"].append({"at": now(), "stage": st["id"], "command": shlex.join(command), "exit_code": code,
                         "log": log.relative_to(line.root).as_posix(), "log_sha256": sha(log), "by": actor()})
    event(job, "tested", actor(), exit_code=code)
    line.save(job)
    sys.stdout.write(out)
    sys.stderr.write(err)
    print(f"\n{job['id']}: test at {st['id']} exited {code}; evidence {log.relative_to(line.root)}")
    return code


def cmd_review(args, line: Line) -> int:
    job = line.load(args.id)
    st = stage(job)
    if st is None:
        sys.exit(f"{job['id']} is done")
    record_outputs(line, job, st)
    snap = line.snapshot(job)
    entry = {"at": now(), "stage": st["id"], "verdict": args.verdict, "by": args.by,
             "independent": bool(args.independent), "files": snap, "snapshot": snapshot_digest(snap)}
    if args.file:
        f = line.root / args.file
        if not f.exists():
            sys.exit(f"Review file not found: {args.file}")
        entry["file"] = args.file
        entry["file_sha256"] = sha(f)
    job["reviews"].append(entry)
    event(job, "reviewed", args.by, verdict=args.verdict, independent=bool(args.independent))
    line.save(job)
    mode = "independent" if args.independent else "perspective"
    print(f"{job['id']}: {args.verdict} review by {args.by} ({mode}) at {st['id']}")
    return 0


def cmd_approve(args, line: Line) -> int:
    job = line.load(args.id)
    st = stage(job)
    if st is None or st.get("gate") != "human":
        sys.exit(f"{job['id']} is not waiting for a human approval")
    if not args.authorized:
        sys.exit("Approval needs --authorized: the named human approved this stage")
    problems = []
    for prior in job["stages"][: job["stage_index"]]:
        skipped = any(h["event"] == "skipped" and h.get("stage") == prior["id"] for h in job["history"])
        if prior.get("gate") in ("test", "review") and not skipped:
            problems += [f"{prior['id']}: {p}" for p in gate_problems(line, job, prior)]
    missing = [rel for rel, h in line.snapshot(job).items() if h == "MISSING"]
    problems += [f"artifact missing: {rel}" for rel in missing]
    if problems:
        print(f"Cannot approve {job['id']} at {st['id']}:")
        for p in problems:
            print(f"  - {p}")
        return 1
    job["approvals"].append({"at": now(), "stage": st["id"], "by": args.by, "authorized": True,
                             "note": args.note or "", "os_user": getpass.getuser(),
                             "snapshot": snapshot_digest(line.snapshot(job))})
    advance(job, args.by, "approved", note=args.note or "")
    line.save(job)
    print(f"{job['id']}: {st['id']} approved by {args.by}")
    return cmd_next(argparse.Namespace(id=job["id"]), line)


def cmd_retarget(args, line: Line) -> int:
    job = line.load(args.id)
    ids = [s["id"] for s in job["stages"]]
    if args.stage not in ids:
        sys.exit(f"No stage {args.stage}. Stages: {', '.join(ids)}")
    i = ids.index(args.stage)
    if i < job["stage_index"]:
        sys.exit(f"Stage {args.stage} is already passed; only current or future stages can be retargeted")
    old = job["stages"][i].get("outputs", [])
    job["stages"][i] = dict(job["stages"][i], outputs=args.outputs)
    event(job, "retargeted", actor(), target_stage=args.stage, old=old, new=args.outputs, reason=args.reason)
    line.save(job)
    print(f"{job['id']}: {args.stage} outputs {old} -> {args.outputs} ({args.reason})")
    return 0


def cmd_block(args, line: Line) -> int:
    job = line.load(args.id)
    job["status"] = "blocked"
    event(job, "blocked", actor(), reason=args.reason)
    line.save(job)
    print(f"{job['id']} blocked: {args.reason}")
    return 0


def cmd_unblock(args, line: Line) -> int:
    job = line.load(args.id)
    st = stage(job)
    job["status"] = "done" if st is None else ("awaiting_approval" if st.get("gate") == "human" else "open")
    event(job, "unblocked", actor())
    line.save(job)
    print(f"{job['id']} unblocked")
    return 0


def cmd_verify(args, line: Line) -> int:
    job = line.load(args.id)
    bad = 0
    for rel, h in line.snapshot(job).items():
        ok = h == job["artifacts"][rel]["sha256"]
        bad += not ok
        print(f"{'ok      ' if ok else 'CHANGED ' if h != 'MISSING' else 'MISSING '} {rel}")
    for t in job["tests"]:
        p = line.root / t["log"]
        if not p.exists() or sha(p) != t["log_sha256"]:
            bad += 1
            print(f"TAMPERED {t['log']}")
    print(f"{job['id']}: {len(job['artifacts'])} artifacts, {bad} problem(s)")
    return 1 if bad else 0


def cmd_show(args, line: Line) -> int:
    job = line.load(args.id)
    print(json.dumps({k: job[k] for k in ("id", "type", "title", "status", "stage_index")}, indent=2))
    for i, s in enumerate(job["stages"]):
        mark = "x" if i < job["stage_index"] else ">" if i == job["stage_index"] else " "
        print(f"  [{mark}] {s['id']}" + (f" ({s['gate']})" if s.get("gate") else ""))
    print(f"artifacts {len(job['artifacts'])}, tests {len(job['tests'])}, reviews {len(job['reviews'])}, "
          f"approvals {len(job['approvals'])}")
    return 0


def cmd_board(args, line: Line) -> int:
    rows = ["# Factory board", "", f"Updated {now()}. Generated by job.py board.", "",
            "| Job | Type | Title | Stage | Status | Next | Last test exit | Last review |", "|---|---|---|---|---|---|---|---|"]
    for j in line.all():
        st = stage(j)
        nxt = "-" if st is None else (st.get("skill") or ("human approval" if st.get("gate") == "human" else "-"))
        last_test = j["tests"][-1]["exit_code"] if j["tests"] else "-"
        last_rev = j["reviews"][-1]["verdict"] if j["reviews"] else "-"
        rows.append(f"| {j['id']} | {j['type']} | {j['title']} | {(st or {}).get('id', 'done')} | "
                    f"{j['status']} | {nxt} | {last_test} | {last_rev} |")
    board = line.root / FACTORY / "BOARD.md"
    board.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="job.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="repo root (default: nearest folder with .factory/, or cwd for init)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("types")
    p = sub.add_parser("new"); p.add_argument("type"); p.add_argument("title"); p.add_argument("--by")
    sub.add_parser("list")
    sub.add_parser("board")
    for name in ("next", "show", "verify", "unblock"):
        sub.add_parser(name).add_argument("id")
    p = sub.add_parser("push"); p.add_argument("id"); p.add_argument("--note")
    p = sub.add_parser("skip"); p.add_argument("id"); p.add_argument("--reason", required=True)
    p = sub.add_parser("block"); p.add_argument("id"); p.add_argument("--reason", required=True)
    p = sub.add_parser("retarget"); p.add_argument("id"); p.add_argument("--stage", required=True)
    p.add_argument("--outputs", nargs="+", required=True); p.add_argument("--reason", required=True)
    p = sub.add_parser("test"); p.add_argument("id"); p.add_argument("command", nargs=argparse.REMAINDER)
    p = sub.add_parser("review"); p.add_argument("id")
    p.add_argument("--verdict", choices=["PASS", "CHANGES"], required=True)
    p.add_argument("--by", required=True); p.add_argument("--file"); p.add_argument("--independent", action="store_true")
    p = sub.add_parser("approve"); p.add_argument("id"); p.add_argument("--by", required=True)
    p.add_argument("--authorized", action="store_true"); p.add_argument("--note")
    args = ap.parse_args(argv)

    if args.cmd == "init":
        return cmd_init(args, Path(args.root or os.getcwd()).resolve())
    if args.cmd == "types":
        return cmd_types(args, None)
    root = Path(args.root).resolve() if args.root else find_root(Path.cwd())
    if root is None:
        sys.exit("No .factory/ found here or above. Run: job.py init")
    line = Line(root)
    return {"new": cmd_new, "list": cmd_list, "board": cmd_board, "next": cmd_next, "show": cmd_show,
            "verify": cmd_verify, "push": cmd_push, "skip": cmd_skip, "block": cmd_block,
            "unblock": cmd_unblock, "retarget": cmd_retarget, "test": cmd_test, "review": cmd_review,
            "approve": cmd_approve}[args.cmd](args, line)


if __name__ == "__main__":
    sys.exit(main())
