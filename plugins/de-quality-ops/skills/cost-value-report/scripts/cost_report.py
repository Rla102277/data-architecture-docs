#!/usr/bin/env python3
"""Daily cost and value report for a data platform build. Standard library only.

Reads inputs you maintain, the factory line's job history (.factory/) and git,
and writes a dated Markdown report plus a CSV of every number with its label
and source. Every number is labeled:

    MEASURED   from an export, a log or a timestamp
    ALLOCATED  a measured total split across jobs (the method is stated)
    ASSUMED    from assumptions.csv or baseline-estimates.csv

Nothing is invented. A missing input shows as "not provided" and is listed.

    cost_report.py --repo . --init                     # create input templates, then fill them in
    cost_report.py --repo . --project Foundation       # write today's report
    cost_report.py --repo . --date 2026-11-20          # report as of a date
    cost_report.py --repo ~/Code/foundation --project Foundation --install-launchd --hour 18
    cost_report.py --uninstall-launchd                 # macOS: stop the daily run

Inputs (default <repo>/docs/reports/inputs/):
    assumptions.csv          key,value,source,as_of
    time-log.csv             date,job_id,stage,hours,note
    baseline-estimates.csv   deliverable,job_id,delivered_on,traditional_hours_low,traditional_hours_high,estimated_by,method
    cursor-usage/*.csv       usage exports from the Cursor dashboard (optional)
    azure-cost/*.csv         Azure Cost Management exports (optional)
Rows whose first cell starts with # are ignored.

Output (default <repo>/docs/reports/daily/): YYYY-MM-DD.md, YYYY-MM-DD.csv, and LATEST.md.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ASSUMPTION_KEYS = [
    ("tracking_start", "First day to count (YYYY-MM-DD). Blank = earliest job or time-log date."),
    ("cursor_monthly_cost", "Cursor plan cost per month for the people on this project, USD."),
    ("my_loaded_hourly", "Your fully loaded cost per hour, USD (salary, benefits, overhead)."),
    ("contractor_hourly_low", "Contractor hourly rate, low end, USD."),
    ("contractor_hourly_high", "Contractor hourly rate, high end, USD."),
    ("contractor_hours_per_week", "Hours a contractor bills per week (often 40)."),
    ("fte_loaded_annual", "Additional employee fully loaded annual cost, USD."),
    ("fte_hours_per_year", "Productive hours per employee per year (often 1800 to 2000)."),
    ("fte_hiring_lead_weeks", "Weeks from approval to a new hire's start date."),
    ("fte_ramp_weeks", "Weeks before a new hire is productive on this platform."),
]
TEMPLATES = {
    "time-log.csv": "date,job_id,stage,hours,note\n# 2026-11-20,JOB-0001,decide,2.5,EXAMPLE row: lines starting with # are ignored\n",
    "baseline-estimates.csv": ("deliverable,job_id,delivered_on,traditional_hours_low,traditional_hours_high,estimated_by,method\n"
                               "# Architecture doc set (3 personas),JOB-0001,2026-11-21,120,200,Randy Archambault,EXAMPLE: past projects of similar size\n"),
}
WEEK = 7
UNALLOCATED = "(no hours logged)"


# ---------- parsing helpers ----------

def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        lines = [ln for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


def num(value) -> float | None:
    if value is None:
        return None
    s = str(value).strip().replace("$", "").replace(",", "")
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(value) -> dt.date | None:
    s = str(value or "").strip()
    if not s:
        return None
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return dt.date(int(m[3]), int(m[1]), int(m[2]))
    m = re.match(r"(\d{4})(\d{2})(\d{2})$", s)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    return None


def pick(headers: list[str], *needles: str, avoid: tuple[str, ...] = ()) -> str | None:
    low = {h: h.lower().replace(" ", "") for h in headers}
    for needle in needles:
        for h, l in low.items():
            if needle in l and not any(a in l for a in avoid):
                return h
    return None


def money(v: float | None) -> str:
    return "not provided" if v is None else f"${v:,.0f}" if abs(v) >= 100 else f"${v:,.2f}"


def hrs(v: float | None) -> str:
    return "not provided" if v is None else f"{v:,.1f} h"


# ---------- report model ----------

class Report:
    def __init__(self, as_of: dt.date):
        self.as_of = as_of
        self.rows: list[dict] = []
        self.missing: list[str] = []
        self.caveats: list[str] = []

    def put(self, section: str, metric: str, value, label: str, source: str, unit: str = "USD") -> None:
        self.rows.append({"section": section, "metric": metric, "value": "" if value is None else round(value, 2),
                          "unit": unit, "label": label, "source": source})

    def need(self, text: str) -> None:
        if text not in self.missing:
            self.missing.append(text)


def load_assumptions(inputs: Path, rep: Report) -> dict[str, tuple[float | str | None, str]]:
    out: dict[str, tuple] = {}
    for r in read_rows(inputs / "assumptions.csv"):
        key = (r.get("key") or "").strip()
        raw = (r.get("value") or "").strip()
        if not key or not raw:
            continue
        src = (r.get("source") or "assumptions.csv").strip() + (f" ({r.get('as_of').strip()})" if (r.get("as_of") or "").strip() else "")
        out[key] = (raw if key == "tracking_start" else num(raw), src)
    for key, why in ASSUMPTION_KEYS:
        if key != "tracking_start" and out.get(key, (None,))[0] is None:
            rep.need(f"assumptions.csv `{key}`: {why}")
    return out


def a(assume: dict, key: str) -> float | None:
    return assume.get(key, (None, ""))[0]


def load_jobs(repo: Path) -> list[dict]:
    jobs = []
    for p in sorted((repo / ".factory" / "jobs").glob("JOB-*/job.json")):
        try:
            jobs.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return jobs


def ts_date(s: str) -> dt.date | None:
    try:
        return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).astimezone().date()
    except (TypeError, ValueError):
        return parse_date(s)


def git_commits(repo: Path) -> dict[dt.date, int]:
    counts: dict[dt.date, int] = defaultdict(int)
    if not shutil.which("git"):
        return counts
    try:
        out = subprocess.run(["git", "-C", str(repo), "log", "--all", "--format=%ad", "--date=short"],
                             capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        return counts
    for line in out.split():
        d = parse_date(line)
        if d:
            counts[d] += 1
    return counts


def cursor_usage(folder: Path, rep: Report) -> tuple[dict[dt.date, float], dict[dt.date, float]]:
    """Usage-based charges and tokens per day from Cursor dashboard CSV exports."""
    cost: dict[dt.date, float] = defaultdict(float)
    tokens: dict[dt.date, float] = defaultdict(float)
    files = sorted(folder.glob("*.csv")) if folder.exists() else []
    seen: set[tuple] = set()
    for f in files:
        rows = read_rows(f)
        if not rows:
            continue
        headers = list(rows[0].keys())
        dcol = pick(headers, "date", "time")
        ccol = pick(headers, "cost", "usd", "charge", "amount")
        tcol = pick(headers, "totaltokens", "tokens")
        if not dcol:
            rep.caveats.append(f"Cursor export {f.name}: no date column found, skipped.")
            continue
        for r in rows:
            key = tuple(r.values())
            if key in seen:  # overlapping exports
                continue
            seen.add(key)
            d = parse_date(r.get(dcol))
            if not d:
                continue
            c = num(r.get(ccol)) if ccol else None
            if c:
                cost[d] += c
            t = num(r.get(tcol)) if tcol else None
            if t:
                tokens[d] += t
    return cost, tokens


def azure_costs(folder: Path, rep: Report) -> dict[dt.date, dict[str, float]]:
    by_day: dict[dt.date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    files = sorted(folder.glob("*.csv")) if folder.exists() else []
    seen: set[tuple] = set()
    for f in files:
        rows = read_rows(f)
        if not rows:
            continue
        headers = list(rows[0].keys())
        dcol = pick(headers, "usagedate", "date")
        ccol = pick(headers, "costinbillingcurrency", "pretaxcost", "costusd", "cost", avoid=("unit", "center"))
        scol = pick(headers, "servicename", "metercategory", "consumedservice", "service")
        if not dcol or not ccol:
            rep.caveats.append(f"Azure export {f.name}: no date or cost column found, skipped.")
            continue
        for r in rows:
            key = tuple(r.values())
            if key in seen:
                continue
            seen.add(key)
            d = parse_date(r.get(dcol))
            c = num(r.get(ccol))
            if d and c is not None:
                by_day[d][(r.get(scol) or "Other").strip() or "Other"] += c
    return by_day


# ---------- the report ----------

def build(repo: Path, inputs: Path, as_of: dt.date, project: str) -> tuple[str, Report]:
    rep = Report(as_of)
    assume = load_assumptions(inputs, rep)
    jobs = load_jobs(repo)
    log = read_rows(inputs / "time-log.csv")
    baselines = read_rows(inputs / "baseline-estimates.csv")
    commits = git_commits(repo)
    cur_cost, cur_tokens = cursor_usage(inputs / "cursor-usage", rep)
    azure = azure_costs(inputs / "azure-cost", rep)

    if not (inputs / "time-log.csv").exists() or not log:
        rep.need("time-log.csv: your hands-on hours per day and job. Nothing else can measure this.")
    if not baselines:
        rep.need("baseline-estimates.csv: traditional hours per deliverable, so the contractor and hire comparison has a basis.")
    if not cur_cost and not cur_tokens:
        rep.need("cursor-usage/: a usage CSV export from the Cursor dashboard (optional; plan cost is used without it).")
    if not azure:
        rep.need("azure-cost/: a Cost Management CSV export for the project's resources.")

    # hours per day and job
    hours: dict[dt.date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    stage_hours: dict[tuple[str, str], float] = defaultdict(float)
    for r in log:
        d, h = parse_date(r.get("date")), num(r.get("hours"))
        if d and h and d <= as_of:
            job = (r.get("job_id") or "").strip() or "(no job)"
            hours[d][job] += h
            stage_hours[(job, (r.get("stage") or "").strip() or "-")] += h

    starts = [ts_date(j.get("created_at", "")) for j in jobs] + list(hours)
    start = parse_date(a(assume, "tracking_start")) or min([s for s in starts if s] or [as_of])
    week_start = as_of - dt.timedelta(days=as_of.weekday())
    month_start = as_of.replace(day=1)
    windows = {"Today": (as_of, as_of), "Week to date": (max(week_start, start), as_of),
               "Month to date": (max(month_start, start), as_of), "To date": (start, as_of)}

    def days(lo: dt.date, hi: dt.date):
        d = lo
        while d <= hi:
            yield d
            d += dt.timedelta(days=1)

    plan = a(assume, "cursor_monthly_cost")
    rate = a(assume, "my_loaded_hourly")

    def cursor_day(d: dt.date) -> float:
        p = plan / calendar.monthrange(d.year, d.month)[1] if plan is not None else 0.0
        return p + cur_cost.get(d, 0.0)

    # spend by window
    spend: dict[str, dict[str, float | None]] = {}
    for name, (lo, hi) in windows.items():
        ds = list(days(lo, hi)) if lo <= hi else []
        h = sum(sum(hours[d].values()) for d in ds)
        cur = sum(cursor_day(d) for d in ds) if (plan is not None or cur_cost) else None
        az = sum(sum(azure[d].values()) for d in ds) if azure else None
        people = h * rate if rate is not None else None
        spend[name] = {"hours": h, "cursor": cur, "azure": az, "people": people,
                       "total": sum(v for v in (cur, az, people) if v is not None)}
        rep.put("spend", f"{name}: my hours", h, "MEASURED", "time-log.csv", "hours")
        rep.put("spend", f"{name}: Cursor", cur, "ASSUMED" if not cur_cost else "MEASURED+ASSUMED",
                "plan cost spread per day (assumptions.csv) + usage charges (cursor-usage/)")
        rep.put("spend", f"{name}: Azure", az, "MEASURED", "azure-cost/")
        rep.put("spend", f"{name}: my time at loaded cost", people, "ASSUMED", "time-log.csv x my_loaded_hourly")
        rep.put("spend", f"{name}: total", spend[name]["total"], "MIXED", "sum of the lines above")

    # Cursor cost allocated to jobs by hours logged that day
    alloc: dict[str, float] = defaultdict(float)
    alloc_week: dict[str, float] = defaultdict(float)
    for d in days(start, as_of):
        c = cursor_day(d)
        if not c:
            continue
        total_h = sum(hours[d].values())
        targets = {j: h / total_h for j, h in hours[d].items()} if total_h else {UNALLOCATED: 1.0}
        for j, share in targets.items():
            alloc[j] += c * share
            if d >= week_start:
                alloc_week[j] += c * share

    # project breakdown
    job_ids = [j["id"] for j in jobs]
    logged_jobs = sorted({j for d in hours for j in hours[d]} - set(job_ids))
    breakdown = []
    for j in jobs:
        jid = j["id"]
        created = ts_date(j.get("created_at", ""))
        last = max((ts_date(h["at"]) for h in j.get("history", []) if ts_date(h.get("at", ""))), default=created)
        end = last if j.get("status") == "done" else as_of
        done_stages = j.get("stage_index", 0)
        h_all = sum(hours[d].get(jid, 0) for d in hours)
        h_week = sum(hours[d].get(jid, 0) for d in hours if d >= week_start)
        today_events = [h for h in j.get("history", []) if ts_date(h.get("at", "")) == as_of]
        stage = j["stages"][done_stages]["id"] if done_stages < len(j.get("stages", [])) else "done"
        breakdown.append({
            "id": jid, "title": j.get("title", ""), "type": j.get("type", ""), "status": j.get("status", ""),
            "stage": stage, "progress": f"{done_stages}/{len(j.get('stages', []))}",
            "hours": h_all, "hours_week": h_week, "cursor": alloc.get(jid, 0.0), "cursor_week": alloc_week.get(jid, 0.0),
            "cycle_days": (end - created).days + 1 if created and end else None,
            "tests": sum(1 for t in j.get("tests", []) if t.get("exit_code") == 0),
            "reviews": len(j.get("reviews", [])), "approvals": len(j.get("approvals", [])),
            "today": today_events,
        })
        rep.put("jobs", f"{jid} hours to date", h_all, "MEASURED", "time-log.csv", "hours")
        rep.put("jobs", f"{jid} Cursor to date", alloc.get(jid, 0.0), "ALLOCATED", "Cursor cost split by hours logged per day")
        rep.put("jobs", f"{jid} cycle days", breakdown[-1]["cycle_days"], "MEASURED", ".factory job timestamps", "days")
    for jid in logged_jobs:
        h_all = sum(hours[d].get(jid, 0) for d in hours)
        breakdown.append({"id": jid, "title": "(in time log, not a factory job)", "type": "", "status": "", "stage": "",
                          "progress": "", "hours": h_all, "hours_week": sum(hours[d].get(jid, 0) for d in hours if d >= week_start),
                          "cursor": alloc.get(jid, 0.0), "cursor_week": alloc_week.get(jid, 0.0), "cycle_days": None,
                          "tests": 0, "reviews": 0, "approvals": 0, "today": []})
    if alloc.get(UNALLOCATED):
        rep.caveats.append(f"{money(alloc[UNALLOCATED])} of Cursor cost fell on days with no hours logged and is unallocated.")

    # comparison
    delivered = []
    for b in baselines:
        d = parse_date(b.get("delivered_on"))
        lo, hi = num(b.get("traditional_hours_low")), num(b.get("traditional_hours_high"))
        if d and d <= as_of and lo is not None and hi is not None:
            delivered.append({**b, "_lo": lo, "_hi": hi, "_job": (b.get("job_id") or "").strip()})
            if "claude" in (b.get("estimated_by") or "").lower() or "cursor" in (b.get("estimated_by") or "").lower() \
                    or "model" in (b.get("estimated_by") or "").lower():
                rep.caveats.append(f"Baseline for '{b.get('deliverable')}' was estimated by a model, not a person. Expect it to be challenged.")
    comp = None
    if delivered:
        base_lo = sum(x["_lo"] for x in delivered)
        base_hi = sum(x["_hi"] for x in delivered)
        jobs_in = {x["_job"] for x in delivered if x["_job"]}
        f_hours = sum(sum(hours[d].get(j, 0) for d in hours) for j in jobs_in)
        f_cursor = sum(alloc.get(j, 0.0) for j in jobs_in)
        f_cost = (f_hours * rate if rate is not None else None)
        f_total = None if f_cost is None else f_cost + f_cursor
        cycle = [b["cycle_days"] for b in breakdown if b["id"] in jobs_in and b["cycle_days"]]
        c_lo, c_hi = a(assume, "contractor_hourly_low"), a(assume, "contractor_hourly_high")
        cpw = a(assume, "contractor_hours_per_week")
        fte, fhy = a(assume, "fte_loaded_annual"), a(assume, "fte_hours_per_year")
        lead, ramp = a(assume, "fte_hiring_lead_weeks"), a(assume, "fte_ramp_weeks")
        con = (base_lo * c_lo, base_hi * c_hi) if c_lo is not None and c_hi is not None else None
        con_wk = (base_lo / cpw, base_hi / cpw) if cpw else None
        hire = (base_lo / fhy * fte, base_hi / fhy * fte) if fte is not None and fhy else None
        hire_wk = ((lead or 0) + (ramp or 0) + base_lo / (fhy / 52), (lead or 0) + (ramp or 0) + base_hi / (fhy / 52)) \
            if fhy and lead is not None and ramp is not None else None
        comp = {"n": len(delivered), "items": delivered, "base": (base_lo, base_hi), "f_hours": f_hours,
                "f_cursor": f_cursor, "f_total": f_total, "f_weeks": (max(cycle) / 7) if cycle else None,
                "con": con, "con_wk": con_wk, "hire": hire, "hire_wk": hire_wk, "jobs": sorted(jobs_in)}
        rep.put("compare", "traditional hours low", base_lo, "ASSUMED", "baseline-estimates.csv", "hours")
        rep.put("compare", "traditional hours high", base_hi, "ASSUMED", "baseline-estimates.csv", "hours")
        rep.put("compare", "factory hours", f_hours, "MEASURED", "time-log.csv for jobs with delivered baselines", "hours")
        rep.put("compare", "factory cost", f_total, "MIXED", "my hours x loaded rate + allocated Cursor")
        for nm, pair, lab in (("contractor cost", con, "ASSUMED"), ("additional hire cost", hire, "ASSUMED")):
            rep.put("compare", f"{nm} low", pair[0] if pair else None, lab, "baselines x rates in assumptions.csv")
            rep.put("compare", f"{nm} high", pair[1] if pair else None, lab, "baselines x rates in assumptions.csv")
        if con and f_total is not None:
            rep.put("compare", "savings vs contractor low", con[0] - f_total, "MIXED", "contractor low - factory cost")
            rep.put("compare", "savings vs contractor high", con[1] - f_total, "MIXED", "contractor high - factory cost")
        if hire and f_total is not None:
            rep.put("compare", "savings vs hire low", hire[0] - f_total, "MIXED", "hire low - factory cost")
            rep.put("compare", "savings vs hire high", hire[1] - f_total, "MIXED", "hire high - factory cost")

    return render(project, as_of, windows, spend, breakdown, comp, commits, cur_tokens, azure, rep), rep


def rng(pair, fmt=money) -> str:
    if not pair:
        return "not provided"
    lo, hi = pair
    return fmt(lo) if round(lo) == round(hi) else f"{fmt(lo)} to {fmt(hi)}"


def weeks(v: float) -> str:
    return f"{v:,.1f} wk"


def render(project, as_of, windows, spend, breakdown, comp, commits, tokens, azure, rep: Report) -> str:
    out = [f"# {project} cost and value report: {as_of.isoformat()}", ""]
    t, w, a_ = spend["Today"], spend["Week to date"], spend["To date"]
    out += ["## Summary", ""]
    out.append(f"- Spend today {money(t['total'])}, week to date {money(w['total'])}, to date {money(a_['total'])} "
               f"({hrs(a_['hours'])} of my time logged).")
    active = [b for b in breakdown if b["today"] or b["hours_week"]]
    out.append(f"- Active jobs this week: {', '.join(b['id'] for b in active) or 'none'}. "
               f"Commits today: {commits.get(as_of, 0)}, this week: {sum(v for d, v in commits.items() if windows['Week to date'][0] <= d <= as_of)}.")
    if comp and comp["f_total"] is not None and comp["con"]:
        out.append(f"- Delivered work to date would have cost {rng(comp['con'])} with contractors and "
                   f"{rng(comp['hire'])} with an additional hire, against {money(comp['f_total'])} here (ASSUMED baselines and rates).")
    else:
        out.append("- Savings comparison: not enough inputs yet (see Missing inputs).")
    out.append(f"- Biggest risk to these numbers: {rep.missing[0] if rep.missing else (rep.caveats[0] if rep.caveats else 'baselines are estimates, not measurements')}")
    out += ["", "Labels: MEASURED (export, log or timestamp), ALLOCATED (measured total split across jobs), ASSUMED (your inputs).", ""]

    out += ["## Spend", "", "| | Today | Week to date | Month to date | To date | Label |", "|---|---|---|---|---|---|"]
    order = ["Today", "Week to date", "Month to date", "To date"]
    for key, label, tag in (("hours", "My hours", "MEASURED"), ("people", "My time at loaded cost", "ASSUMED rate"),
                            ("cursor", "Cursor", "plan ASSUMED, usage MEASURED"), ("azure", "Azure", "MEASURED"),
                            ("total", "Total", "")):
        f = hrs if key == "hours" else money
        out.append(f"| {label} | " + " | ".join(f(spend[o][key]) for o in order) + f" | {tag} |")
    if tokens:
        tot = sum(v for d, v in tokens.items() if d <= as_of)
        out += ["", f"Cursor tokens to date: {tot:,.0f} (MEASURED, cursor-usage/)."]
    if azure:
        svc: dict[str, float] = defaultdict(float)
        lo = windows["To date"][0]
        for d, m in azure.items():
            if lo <= d <= as_of:
                for s, c in m.items():
                    svc[s] += c
        out += ["", "Azure by service, to date (MEASURED):", "", "| Service | Cost |", "|---|---|"]
        out += [f"| {s} | {money(c)} |" for s, c in sorted(svc.items(), key=lambda x: -x[1])]

    out += ["", "## Project breakdown", "",
            "| Job | Title | Type | Stage | Progress | Hours (week / total) | Cursor ALLOCATED (week / total) | Cycle days | Tests passed | Reviews | Approvals |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in breakdown:
        out.append(f"| {b['id']} | {b['title']} | {b['type']} | {b['stage']} | {b['progress']} | "
                   f"{b['hours_week']:.1f} / {b['hours']:.1f} | {money(b['cursor_week'])} / {money(b['cursor'])} | "
                   f"{b['cycle_days'] if b['cycle_days'] is not None else '-'} | {b['tests']} | {b['reviews']} | {b['approvals']} |")
    if not breakdown:
        out.append("| (no factory jobs or time-log entries yet) | | | | | | | | | | |")
    out += ["", "Cursor cost is allocated to jobs by the share of hours logged to each job that day. "
                "Cycle days are calendar time from job creation, not effort."]

    events = [(b["id"], e) for b in breakdown for e in b["today"]]
    out += ["", "## Today on the factory line", ""]
    out += [f"- {jid}: {e.get('event')} at stage {e.get('stage') or '-'} by {e.get('by', '?')}"
            + (f" ({e['note']})" if e.get("note") else "") for jid, e in events] or ["- No job events today."]

    out += ["", "## Factory vs contractors vs additional hire", ""]
    if comp:
        out += [f"Deliverables counted: {comp['n']} (jobs {', '.join(comp['jobs']) or 'unlinked'}).", "",
                "| Deliverable | Job | Delivered | Traditional hours | Estimated by |", "|---|---|---|---|---|"]
        out += [f"| {x.get('deliverable')} | {x['_job'] or '-'} | {x.get('delivered_on')} | {rng((x['_lo'], x['_hi']), hrs)} | {x.get('estimated_by') or 'not provided'} |"
                for x in comp["items"]]
        out += ["", "| Option | Cost | Calendar time | Basis |", "|---|---|---|---|",
                f"| Factory (actual) | {money(comp['f_total'])} | {weeks(comp['f_weeks']) if comp['f_weeks'] else 'not provided'} | "
                f"{hrs(comp['f_hours'])} my time x loaded rate + {money(comp['f_cursor'])} Cursor ALLOCATED |",
                f"| Contractor | {rng(comp['con'])} | {rng(comp['con_wk'], weeks)} | {rng(comp['base'], hrs)} x contractor rate low to high |",
                f"| Additional hire | {rng(comp['hire'])} | {rng(comp['hire_wk'], weeks)} | {rng(comp['base'], hrs)} at loaded annual cost; time includes hiring lead and ramp |"]
        if comp["f_total"] is not None and comp["con"]:
            out += ["", f"Savings vs contractor: {rng((comp['con'][0] - comp['f_total'], comp['con'][1] - comp['f_total']))}."]
        if comp["f_total"] is not None and comp["hire"]:
            out += [f"Savings vs additional hire: {rng((comp['hire'][0] - comp['f_total'], comp['hire'][1] - comp['f_total']))}."]
        out += ["", "Azure is excluded from this comparison: the platform runs on it whoever builds it."]
    else:
        out.append("Not enough inputs yet: add delivered rows to baseline-estimates.csv.")

    out += ["", "## Missing inputs and caveats", ""]
    out += [f"- Missing: {m}" for m in rep.missing] + [f"- {c}" for c in rep.caveats] or ["- None."]
    out += ["", f"Every number above is in {as_of.isoformat()}.csv with its label and source.", ""]
    return "\n".join(out)


# ---------- setup and scheduling ----------

def init(inputs: Path) -> int:
    inputs.mkdir(parents=True, exist_ok=True)
    (inputs / "cursor-usage").mkdir(exist_ok=True)
    (inputs / "azure-cost").mkdir(exist_ok=True)
    made = []
    p = inputs / "assumptions.csv"
    if not p.exists():
        with p.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["key", "value", "source", "as_of"])
            for key, why in ASSUMPTION_KEYS:
                w.writerow([key, "", why, ""])
        made.append(p)
    for name, body in TEMPLATES.items():
        q = inputs / name
        if not q.exists():
            q.write_text(body, encoding="utf-8")
            made.append(q)
    for m in made:
        print(f"created {m}")
    print(f"Fill in {inputs}/assumptions.csv (value column), log hours in time-log.csv, "
          "add baselines, and drop exports in cursor-usage/ and azure-cost/.")
    return 0


LABEL = "com.dataengineeringfactory.cost-report"


def install_launchd(repo: Path, project: str, hour: int, minute: int) -> int:
    if sys.platform != "darwin":
        sys.exit("--install-launchd is for macOS. On other systems, schedule this command with cron or Task Scheduler.")
    agents = Path.home() / "Library" / "LaunchAgents"
    agents.mkdir(parents=True, exist_ok=True)
    logs = Path.home() / "Library" / "Logs"
    logs.mkdir(parents=True, exist_ok=True)
    plist = agents / f"{LABEL}.plist"
    data = {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, str(Path(__file__).resolve()), "--repo", str(repo), "--project", project],
        "StartCalendarInterval": {"Hour": hour, "Minute": minute},
        "WorkingDirectory": str(repo),
        "StandardOutPath": str(logs / "cost-report.log"),
        "StandardErrorPath": str(logs / "cost-report.log"),
        "EnvironmentVariables": {"PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"},
    }
    uid = str(os.getuid())
    subprocess.run(["launchctl", "bootout", f"gui/{uid}", str(plist)], capture_output=True)
    with plist.open("wb") as fh:
        plistlib.dump(data, fh)
    r = subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(plist)], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip())
        sys.exit(f"Wrote {plist} but launchctl could not load it.")
    print(f"Scheduled daily at {hour:02d}:{minute:02d}: {project} report for {repo}")
    print(f"Log: {logs / 'cost-report.log'}   Run now: launchctl kickstart gui/{uid}/{LABEL}")
    print("If your Mac is asleep at that time, launchd runs it when the Mac wakes.")
    return 0


def uninstall_launchd() -> int:
    plist = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", str(plist)], capture_output=True)
    if plist.exists():
        plist.unlink()
    print("Daily report unscheduled.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--project", default="Project")
    ap.add_argument("--inputs", type=Path, help="default <repo>/docs/reports/inputs")
    ap.add_argument("--out", type=Path, help="default <repo>/docs/reports/daily")
    ap.add_argument("--date", help="report as of YYYY-MM-DD (default today)")
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--install-launchd", action="store_true")
    ap.add_argument("--uninstall-launchd", action="store_true")
    ap.add_argument("--hour", type=int, default=18)
    ap.add_argument("--minute", type=int, default=0)
    args = ap.parse_args()
    if args.uninstall_launchd:
        return uninstall_launchd()
    repo = args.repo.expanduser().resolve()
    if not repo.is_dir():
        sys.exit(f"No such repo folder: {repo}")
    inputs = (args.inputs or repo / "docs" / "reports" / "inputs").expanduser()
    if args.init:
        return init(inputs)
    if args.install_launchd:
        return install_launchd(repo, args.project, args.hour, args.minute)
    as_of = parse_date(args.date) if args.date else dt.date.today()
    if not as_of:
        sys.exit("--date must be YYYY-MM-DD")
    md, rep = build(repo, inputs, as_of, args.project)
    out = (args.out or repo / "docs" / "reports" / "daily").expanduser()
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{as_of.isoformat()}.md").write_text(md, encoding="utf-8")
    (out / "LATEST.md").write_text(md, encoding="utf-8")
    with (out / f"{as_of.isoformat()}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["section", "metric", "value", "unit", "label", "source"])
        w.writeheader()
        w.writerows(rep.rows)
    print(f"Wrote {out / (as_of.isoformat() + '.md')} ({len(rep.missing)} missing input(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
