"""OURS. Layer 2 verifier: drill checks on any plan.jsonl.

Usage: python tools/verify_plan.py out/<name>/plan.jsonl --labels data/labels.csv --data data/
                                   [--report reports/<name>_plan.json] [--offsets gen/<name>/offsets.jsonl]
                                   [--stores N]   (only check coverage for the first N stores)

Checks (hard = counts toward G2):
  schema        JSONL validity, type in PLAN_TYPES, required fields, enum values         (hard)
  classify      PULL recall/precision, 3x3 confusion incl. HOLD_VERIFY, decoys pulled   (decoys hard)
  coverage      every (store, truth-PULL SKU, facing) has a PULL shelf_task              (hard)
  reference     unique ids, cross-references between records and to data/               (hard)
  conservation  allocations never exceed DC stock; dc_balance_after consistent          (hard)
  capacity      truck cube/weight; every pulled case on exactly one stop; no empty manifests (hard)
  labor         windows inside shifts, no overlaps per associate, shift minutes,
                one store per floater per window, associate belongs to the store         (hard)
  deadline      every window ends before the scenario deadline in the store's local tz  (hard)
  contradiction KEEP verdict with PULL task, playbook counts vs tasks, one-sided handoffs (hard)
Errors are grouped by `src` (mapped to token ranges when offsets are available).
Exit 0 when there are zero hard errors.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contract import (PLAN_TYPES, Verdict, Action, StoreFormat, ExceptionKind, HandoffKind,  # noqa: E402
                      DecidedBy)

ENUMS = {("sku_verdict", "verdict"): {e.value for e in Verdict},
         ("sku_verdict", "decided_by"): {e.value for e in DecidedBy},
         ("shelf_task", "action"): {e.value for e in Action},
         ("store_playbook", "format"): {e.value for e in StoreFormat},
         ("exception", "kind"): {e.value for e in ExceptionKind},
         ("handoff", "kind"): {e.value for e in HandoffKind}}
ID_FIELD = {"evidence": "evidence_id", "shelf_task": "task_id", "exception": "exc_id", "allocation": "alloc_id",
            "handoff": "handoff_id", "route_manifest": "manifest_id", "sku_verdict": "sku_id",
            "store_playbook": "store_id", "run": "run_id"}
HARD = {"schema", "reference", "conservation", "capacity", "labor", "deadline", "coverage", "contradiction",
        "decoy"}
DECOY_RE = re.compile(r"red|e\s*127|erythro|eritro", re.I)
MAX_EXAMPLES = 300


class Errs:
    def __init__(self):
        self.items: list[dict] = []
        self.count = Counter()
        self.by_src = defaultdict(Counter)

    def add(self, check: str, rec: dict | None, msg: str, severity: str | None = None, **kw):
        sev = severity or ("hard" if check in HARD else "soft")
        src = (rec or {}).get("src") or ("<data>" if rec is None else "<no src>")
        key = f"{check}:{sev}"
        self.count[key] += 1
        self.by_src[src][key] += 1
        if sum(1 for e in self.items if e["check"] == check) < MAX_EXAMPLES:
            rid = None
            if rec:
                f = ID_FIELD.get(rec.get("type"))
                rid = rec.get(f) if f else None
            self.items.append({"check": check, "severity": sev, "src": src, "type": (rec or {}).get("type"),
                               "id": rid, "line": (rec or {}).get("_line"), "msg": msg, **kw})

    def hard(self):
        return sum(v for k, v in self.count.items() if k.endswith(":hard"))


def rows(p: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def parse_dt(s, tz: str | None):
    if not isinstance(s, str):
        return None
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=ZoneInfo(tz or "America/Los_Angeles"))
    return d


def window(w, tz):
    """[start, end] or {start, end} -> (start_dt, end_dt) or None."""
    if isinstance(w, dict):
        w = [w.get("start"), w.get("end")]
    if not isinstance(w, (list, tuple)) or len(w) != 2:
        return None
    a, b = parse_dt(w[0], tz), parse_dt(w[1], tz)
    if a is None or b is None:
        return None
    return a, b


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan"); ap.add_argument("--labels", default=str(ROOT / "data" / "labels.csv"))
    ap.add_argument("--data", default=str(ROOT / "data")); ap.add_argument("--report")
    ap.add_argument("--offsets"); ap.add_argument("--stores", type=int)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    plan_p = pathlib.Path(a.plan); D = pathlib.Path(a.data)
    name = plan_p.parent.name
    report_p = pathlib.Path(a.report) if a.report else ROOT / "reports" / f"{name}_plan.json"
    E = Errs()

    # ---------- data
    skus = {r["sku_id"]: r for r in rows(D / "skus.jsonl")}
    stores = {r["store_id"]: r for r in rows(D / "stores.jsonl")}
    facings = rows(D / "facings.jsonl")
    assocs = {r["associate_id"]: r for r in rows(D / "associates.jsonl")}
    trucks = {r["truck_id"]: r for r in rows(D / "trucks.jsonl")}
    stock = {(r["dc_id"], r["sku_id"]): r["cases"] for r in rows(D / "dc_stock.jsonl")}
    notes = {r["note_id"]: r for r in rows(D / "notes.jsonl")}
    rules = {r["rule_id"]: r for r in rows(D / "rules.jsonl")}
    labels = {}
    with open(a.labels, newline="") as fh:
        for r in csv.DictReader(fh):
            labels[r["sku_id"]] = r["truth"].strip()
    districts = {s["district"] for s in stores.values()}
    dcs = {s["dc_id"] for s in stores.values()} | {t["dc_id"] for t in trucks.values()}

    # ---------- plan
    recs, n_bad_json = [], 0
    text = plan_p.read_text(encoding="utf-8", errors="replace") if plan_p.exists() else ""
    if not plan_p.exists():
        E.add("schema", None, f"plan file missing: {plan_p}")
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            n_bad_json += 1; E.add("schema", {"_line": i, "src": "<unparseable>"}, f"bad JSON: {e.msg}")
            continue
        if not isinstance(r, dict):
            E.add("schema", {"_line": i}, "record is not an object"); continue
        r["_line"] = i
        recs.append(r)
    by_type = defaultdict(list)
    for r in recs:
        t = r.get("type")
        if t not in PLAN_TYPES:
            E.add("schema", r, f"unknown record type {t!r}"); continue
        miss = [f for f in PLAN_TYPES[t] if f not in r]
        if miss:
            E.add("schema", r, f"{t} missing fields: {', '.join(miss)}")
        for (tt, f), allowed in ENUMS.items():
            if tt == t and f in r and r[f] is not None and r[f] not in allowed:
                E.add("schema", r, f"{t}.{f}={r[f]!r} not in contract enum")
        by_type[t].append(r)
    runs = by_type["run"]
    if len(runs) != 1:
        E.add("schema", runs[1] if len(runs) > 1 else None, f"expected exactly 1 run record, got {len(runs)}")
    run = runs[0] if runs else {}
    scen_id = run.get("scenario_id") or "ca_red3"
    scen_p = D / f"scenario_{scen_id}.json"
    scen = json.loads(scen_p.read_text()) if scen_p.exists() else {}
    deadline_naive = None
    if scen.get("deadline"):
        deadline_naive = datetime.fromisoformat(scen["deadline"]).replace(tzinfo=None)
    else:
        rid = (scen.get("rule_ids") or ["CA_AB418_RED3"])[0]
        if rid in rules:
            deadline_naive = datetime.fromisoformat(rules[rid]["effective"]).replace(tzinfo=None)
    scen_state = scen.get("state", "CA")
    for rid in run.get("rule_ids") or []:
        if rid not in rules:
            E.add("reference", run, f"run.rule_ids {rid} not in rules.jsonl")

    def store_tz(sid):
        return (stores.get(sid) or {}).get("tz") or "America/Los_Angeles"

    def deadline_for(sid):
        return deadline_naive.replace(tzinfo=ZoneInfo(store_tz(sid))) if deadline_naive else None

    # ---------- unique ids
    idx: dict[str, dict] = {}
    for t, f in ID_FIELD.items():
        seen = {}
        for r in by_type[t]:
            v = r.get(f)
            if v is None:
                continue
            if isinstance(v, (list, dict)):
                E.add("schema", r, f"{t}.{f} is not a scalar"); continue
            if v in seen:
                E.add("reference", r, f"duplicate {t}.{f}={v!r} (first at line {seen[v]['_line']})")
            else:
                seen[v] = r
        idx[t] = seen
    ev, tasks, excs, allocs, hos, mans, verdicts, pbs = (idx["evidence"], idx["shelf_task"], idx["exception"],
                                                          idx["allocation"], idx["handoff"], idx["route_manifest"],
                                                          idx["sku_verdict"], idx["store_playbook"])

    # ---------- classification
    labeled = {s: t for s, t in labels.items() if s in skus}
    pred = {s: (verdicts[s].get("verdict") if s in verdicts else None) for s in labeled}
    conf = defaultdict(Counter)
    for s, truth in labeled.items():
        conf[truth][pred[s] or "MISSING"] += 1
    tp = sum(1 for s, t in labeled.items() if t == "PULL" and pred[s] == "PULL")
    fp = sum(1 for s, t in labeled.items() if t != "PULL" and pred[s] == "PULL")
    fn = sum(1 for s, t in labeled.items() if t == "PULL" and pred[s] != "PULL")
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None

    def is_decoy(s):
        k = skus[s]
        return labeled.get(s) == "KEEP" and (DECOY_RE.search(k.get("ingredients", "")) is not None
                                             or not k.get("is_food", True))
    decoys = [s for s in labeled if is_decoy(s)]
    decoys_pulled = [s for s in decoys if pred[s] == "PULL"]
    for s in decoys_pulled:
        E.add("decoy", verdicts[s], f"decoy {s} pulled: {skus[s]['ingredients'][:80]!r}")
    missing_verdicts = [s for s in labeled if pred[s] is None]
    if missing_verdicts:
        E.add("coverage", None, f"{len(missing_verdicts)} labeled SKUs have no sku_verdict",
              examples=missing_verdicts[:20])
    for s, r in verdicts.items():
        if s not in skus:
            E.add("reference", r, f"sku_verdict for unknown sku {s}")
            continue
        if r.get("gtin") is not None and r.get("gtin") != skus[s]["gtin"]:
            E.add("reference", r, f"gtin {r.get('gtin')} != data {skus[s]['gtin']}")
        for rid in r.get("rule_ids") or []:
            if rid not in rules:
                E.add("reference", r, f"rule_id {rid} unknown")
        if r.get("verdict") == "PULL":
            if not r.get("evidence_id"):
                E.add("reference", r, "PULL verdict without evidence_id")
            m = r.get("match")
            if isinstance(m, dict) and isinstance(m.get("start"), int) and isinstance(m.get("end"), int):
                ing = skus[s].get("ingredients", "")
                if m.get("text") is not None and ing[m["start"]:m["end"]] != m["text"]:
                    E.add("reference", r, f"match span [{m['start']}:{m['end']}] != text {m.get('text')!r}",
                          severity="soft")
        if r.get("evidence_id") and r["evidence_id"] not in ev:
            E.add("reference", r, f"evidence_id {r['evidence_id']} missing")
    for eid, r in ev.items():
        if r.get("sku_id") not in skus:
            E.add("reference", r, f"evidence sku {r.get('sku_id')} unknown")
        if r.get("rule_id") not in rules:
            E.add("reference", r, f"evidence rule {r.get('rule_id')} unknown")
        elif r.get("clause_ref") != rules[r["rule_id"]]["clause_ref"]:
            E.add("reference", r, "clause_ref does not match rules.jsonl", severity="soft")

    # ---------- shelf tasks: references, coverage, contradictions
    store_filter = None
    if a.stores:
        store_filter = set(sorted(stores)[:a.stores])
    pull_tasks = defaultdict(list)
    for tid, r in tasks.items():
        sid, sk, act = r.get("store_id"), r.get("sku_id"), r.get("action")
        if sid not in stores:
            E.add("reference", r, f"store {sid} unknown")
        if sk not in skus:
            E.add("reference", r, f"sku {sk} unknown")
        if r.get("evidence_id") and r["evidence_id"] not in ev:
            E.add("reference", r, f"evidence_id {r['evidence_id']} missing")
        if act == "PULL":
            pull_tasks[(sid, sk)].append(r)
            v = pred.get(sk) if sk in labeled else (verdicts.get(sk) or {}).get("verdict")
            if v == "KEEP":
                E.add("contradiction", r, f"PULL task for {sk} whose verdict is KEEP")
            if sk in verdicts and verdicts[sk].get("verdict") != "PULL":
                pass
        if act == "PLACE_SUB":
            if not r.get("sub_sku_id"):
                E.add("reference", r, "PLACE_SUB without sub_sku_id")
            elif r["sub_sku_id"] not in skus:
                E.add("reference", r, f"sub_sku {r['sub_sku_id']} unknown")
            elif labels.get(r["sub_sku_id"]) == "PULL":
                E.add("contradiction", r, f"substitute {r['sub_sku_id']} is itself a PULL SKU")
        if r.get("alloc_id"):
            al = allocs.get(r["alloc_id"])
            if al is None:
                E.add("reference", r, f"alloc_id {r['alloc_id']} missing")
            elif al.get("store_id") != sid or (r.get("sub_sku_id") and al.get("sub_sku_id") != r.get("sub_sku_id")):
                E.add("reference", r, f"alloc {r['alloc_id']} is for {al.get('store_id')}/{al.get('sub_sku_id')}")
        if not isinstance(r.get("qty_units"), int) or (isinstance(r.get("qty_units"), int) and r["qty_units"] < 0):
            E.add("schema", r, f"qty_units {r.get('qty_units')!r} not a non-negative int")
    affected = {s for s, t in labeled.items() if t == "PULL"}
    cov_total = cov_hit = 0
    for f in facings:
        if f["sku_id"] not in affected or (store_filter and f["store_id"] not in store_filter):
            continue
        cov_total += 1
        ts = pull_tasks.get((f["store_id"], f["sku_id"]))
        if ts:
            cov_hit += 1
            if not any(t.get("loc") == f["loc"] for t in ts):
                E.add("coverage", ts[0], f"PULL task loc {ts[0].get('loc')} != facing loc {f['loc']}",
                      severity="soft")
            if sum(t.get("qty_units") or 0 for t in ts if isinstance(t.get("qty_units"), int)) < f["units"]:
                E.add("coverage", ts[0], f"PULL qty below facing units {f['units']} at {f['store_id']}/{f['sku_id']}",
                      severity="soft")
        else:
            E.add("coverage", verdicts.get(f["sku_id"]), f"no PULL task for truth-PULL {f['sku_id']} at {f['store_id']} {f['loc']}")
    hold_total = hold_hit = 0
    hold_tasks = {(r.get("store_id"), r.get("sku_id")) for r in tasks.values() if r.get("action") == "HOLD_VERIFY"}
    for f in facings:
        if labeled.get(f["sku_id"]) == "HOLD_VERIFY" and (not store_filter or f["store_id"] in store_filter):
            hold_total += 1; hold_hit += (f["store_id"], f["sku_id"]) in hold_tasks

    # ---------- exceptions
    for xid, r in excs.items():
        n = notes.get(r.get("note_id"))
        if r.get("note_id") is not None and n is None:
            E.add("reference", r, f"note {r.get('note_id')} unknown")
        elif n and n["store_id"] != r.get("store_id"):
            E.add("reference", r, f"note {n['note_id']} belongs to {n['store_id']}")
        for t in r.get("task_ids") or []:
            if t not in tasks:
                E.add("reference", r, f"task {t} missing")
            elif tasks[t].get("store_id") != r.get("store_id"):
                E.add("reference", r, f"task {t} is at another store")

    # ---------- allocations: conservation
    used = defaultdict(int)
    for r in by_type["allocation"]:
        k = (r.get("dc_id"), r.get("sub_sku_id"))
        q = r.get("qty_cases")
        if not isinstance(q, int) or isinstance(q, bool):
            E.add("conservation", r, f"qty_cases {q!r} is not an integer"); continue
        if q <= 0:
            E.add("conservation", r, f"qty_cases {q} <= 0", severity="soft" if q == 0 else None)
        if k not in stock:
            E.add("conservation", r, f"no DC stock row for {k}")
            continue
        used[k] += q
        bal = stock[k] - used[k]
        if r.get("dc_balance_after") != bal:
            E.add("conservation", r, f"dc_balance_after {r.get('dc_balance_after')} != {bal} for {k}")
        if r.get("store_id") not in stores:
            E.add("reference", r, f"store {r.get('store_id')} unknown")
        elif stores[r["store_id"]]["dc_id"] != r.get("dc_id"):
            E.add("reference", r, f"store {r['store_id']} is served by {stores[r['store_id']]['dc_id']}",
                  severity="soft")
    for k, u in used.items():
        if u > stock[k]:
            E.add("conservation", None, f"allocated {u} > stock {stock[k]} for {k}")

    # ---------- routes: capacity and case coverage
    used_trucks = Counter()
    stop_cases = defaultdict(int)
    for mid, r in mans.items():
        tr = trucks.get(r.get("truck_id"))
        used_trucks[r.get("truck_id")] += 1
        stops = r.get("stops") or []
        if not stops:
            E.add("capacity", r, "empty manifest")
        if tr is None:
            E.add("reference", r, f"truck {r.get('truck_id')} unknown"); continue
        if r.get("dc_id") != tr["dc_id"]:
            E.add("reference", r, f"dc {r.get('dc_id')} != truck dc {tr['dc_id']}")
        cube = sum(float(s.get("cube_ft3") or 0) for s in stops if isinstance(s, dict))
        wt = sum(float(s.get("weight_lb") or 0) for s in stops if isinstance(s, dict))
        if cube > tr["cube_ft3"] + 1e-6:
            E.add("capacity", r, f"cube {cube:.1f} > {tr['cube_ft3']}")
        if wt > tr["weight_lb"] + 1e-6:
            E.add("capacity", r, f"weight {wt:.1f} > {tr['weight_lb']}")
        lim = r.get("limits") or {}
        if isinstance(lim, dict) and (lim.get("cube_ft3") not in (None, tr["cube_ft3"]) or
                                      lim.get("weight_lb") not in (None, tr["weight_lb"])):
            E.add("capacity", r, f"declared limits {lim} differ from trucks.jsonl", severity="soft")
        for s in stops:
            if not isinstance(s, dict):
                E.add("schema", r, "stop is not an object"); continue
            if s.get("store_id") not in stores:
                E.add("reference", r, f"stop store {s.get('store_id')} unknown"); continue
            if stores[s["store_id"]]["dc_id"] != tr["dc_id"]:
                E.add("reference", r, f"stop {s['store_id']} is served by another DC", severity="soft")
            if not isinstance(s.get("cases"), int) or s["cases"] <= 0:
                E.add("capacity", r, f"stop {s['store_id']} cases {s.get('cases')!r} not a positive int")
            else:
                stop_cases[s["store_id"]] += s["cases"]
        dep = parse_dt(r.get("depart"), store_tz(next(iter(stores), None)))
        dl = deadline_for(stops[0]["store_id"] if stops and isinstance(stops[0], dict) else None)
        if dep and dl and dep >= dl:
            E.add("deadline", r, f"depart {r.get('depart')} not before deadline")
    for t, n in used_trucks.items():
        if n > 1:
            E.add("capacity", None, f"truck {t} used by {n} manifests")
    exp_ceil, exp_floor = defaultdict(int), defaultdict(int)     # per task: ceil(units/case_units), floor
    for (sid, sk), ts in pull_tasks.items():
        if sk not in skus:
            continue
        cu = max(1, skus[sk]["case_units"])
        for t in ts:
            u = t.get("qty_units") if isinstance(t.get("qty_units"), int) else 0
            exp_ceil[sid] += max(1, math.ceil(u / cu)) if u else 0
            exp_floor[sid] += u // cu
    man_rec = next(iter(mans.values()), None)
    dsd_stores = {x.get("store_id") for x in excs.values() if x.get("kind") == "DSD_VENDOR_PULL"}
    if mans:
        for sid in set(exp_ceil) | set(stop_cases):
            got, hi, lo = stop_cases.get(sid, 0), exp_ceil.get(sid, 0), exp_floor.get(sid, 0)
            if hi and got == 0 and sid not in dsd_stores:
                E.add("capacity", man_rec, f"store {sid} has pulled cases but is on no stop")
            elif got > hi:
                E.add("capacity", man_rec, f"store {sid}: stop cases {got} > pulled cases {hi} (ceil per task)")
            elif got < lo or (got < hi and sid not in dsd_stores):
                E.add("capacity", man_rec, f"store {sid}: stop cases {got} < pulled cases {hi} (ceil per task)"
                                        + (" [store has DSD vendor-pull exception]" if sid in dsd_stores else ""),
                      severity="soft" if sid in dsd_stores else None)
            elif got < hi:
                E.add("capacity", man_rec, f"store {sid}: {hi - got} pulled cases not on a stop "
                                        f"(DSD vendor-pull exception)", severity="soft")
    elif pull_tasks:
        E.add("capacity", None, "PULL tasks exist but there are no route_manifest records")

    # ---------- labor + deadline
    per_assoc = defaultdict(list)
    floater_windows = defaultdict(list)
    for tid, r in tasks.items():
        sid = r.get("store_id")
        w = window(r.get("window"), store_tz(sid))
        if w is None:
            E.add("schema", r, f"bad window {r.get('window')!r}"); continue
        s0, s1 = w
        if s1 <= s0:
            E.add("labor", r, f"window end <= start {r.get('window')}")
        dl = deadline_for(sid)
        if dl and s1 >= dl:
            E.add("deadline", r, f"window ends {r['window'][1] if isinstance(r['window'], list) else s1} "
                                 f"not before deadline {dl.isoformat()}")
        aid = r.get("associate_id")
        if aid is None:
            E.add("labor", r, "task without associate"); continue
        asc = assocs.get(aid)
        if asc is None:
            E.add("reference", r, f"associate {aid} unknown"); continue
        sh0, sh1 = parse_dt(asc["shift_start"], None), parse_dt(asc["shift_end"], None)
        if s0 < sh0 or s1 > sh1:
            E.add("labor", r, f"window {r.get('window')} outside shift of {aid}")
        if asc["is_floater"]:
            if stores.get(sid, {}).get("district") != asc["district"]:
                E.add("labor", r, f"floater {aid} works outside district {asc['district']}")
            floater_windows[aid].append((s0, s1, sid, r))
        elif asc["store_id"] != sid:
            E.add("labor", r, f"associate {aid} of {asc['store_id']} assigned at {sid}")
        per_assoc[aid].append((s0, s1, r))
    for aid, lst in per_assoc.items():
        lst.sort(key=lambda x: (x[0], x[1]))
        mins = sum((b - a_).total_seconds() / 60 for a_, b, _ in lst)
        asc = assocs[aid]
        shift = (parse_dt(asc["shift_end"], None) - parse_dt(asc["shift_start"], None)).total_seconds() / 60
        if mins > shift + 1e-6:
            E.add("labor", lst[0][2], f"{aid} assigned {mins:.0f} min > shift {shift:.0f} min")
        for (a0, a1, ra), (b0, b1, rb) in zip(lst, lst[1:]):
            if b0 < a1:
                E.add("labor", rb, f"{aid} overlaps {ra.get('task_id')} and {rb.get('task_id')}")
    # one store per floater per window: also count FLOATER handoff windows
    for hid, r in hos.items():
        if r.get("kind") == "FLOATER":
            for fid in r.get("ref_ids") or []:
                if fid in assocs and assocs[fid]["is_floater"]:
                    w = window(r.get("window"), store_tz(r.get("to_id")))
                    if w:
                        floater_windows[fid].append((w[0], w[1], r.get("to_id"), r))
    for fid, lst in floater_windows.items():
        lst.sort(key=lambda x: x[0])
        for i, (a0, a1, sa, ra) in enumerate(lst):
            for b0, b1, sb, rb in lst[i + 1:]:
                if b0 >= a1:
                    break
                if sa != sb:
                    E.add("labor", rb, f"floater {fid} at {sa} and {sb} in overlapping windows")
                    break

    # ---------- handoffs: references, one-sided, deadline
    known = (set(stores) | districts | {f"DISTRICT_{d}" for d in districts} | dcs | set(assocs) | set(trucks)
             | set(mans) | set(allocs) | set(tasks) | set(excs) | set(ev))
    floater_task_stores = defaultdict(set)
    for aid, lst in floater_windows.items():
        for _, _, sid, r in lst:
            if r.get("type") == "shelf_task":
                floater_task_stores[aid].add(sid)
    floater_handoff = defaultdict(set)
    for hid, r in hos.items():
        for f_ in ("from_id", "to_id"):
            if r.get(f_) is not None and r.get(f_) not in known:
                E.add("contradiction", r, f"handoff {f_} {r.get(f_)!r} refers to nothing")
        for x in r.get("ref_ids") or []:
            if x not in known:
                E.add("contradiction", r, f"handoff ref {x!r} refers to nothing")
        w = window(r.get("window"), store_tz(r.get("to_id") if r.get("to_id") in stores else r.get("from_id")))
        if w is None:
            E.add("schema", r, f"bad window {r.get('window')!r}")
        else:
            sid = r.get("to_id") if r.get("to_id") in stores else r.get("from_id")
            dl = deadline_for(sid if sid in stores else None)
            if dl and w[1] >= dl:
                E.add("deadline", r, f"handoff window ends {w[1].isoformat()} not before deadline")
        k = r.get("kind")
        if k == "FLOATER":
            for fid in r.get("ref_ids") or []:
                if fid in assocs:
                    floater_handoff[fid].add(r.get("to_id"))
                    if assocs[fid]["is_floater"] and r.get("to_id") not in floater_task_stores.get(fid, set()):
                        E.add("contradiction", r, f"one-sided FLOATER handoff: {fid} has no tasks at {r.get('to_id')}")
        elif k == "SUB_TRANSFER":
            if not any(x in allocs for x in r.get("ref_ids") or []):
                E.add("contradiction", r, "SUB_TRANSFER references no allocation")
        elif k == "RETURN_CONSOLIDATION":
            refs = [x for x in r.get("ref_ids") or [] if x in mans]
            if not refs:
                E.add("contradiction", r, "RETURN_CONSOLIDATION references no manifest")
            for m in refs:
                if r.get("from_id") in stores and r["from_id"] not in {s.get("store_id") for s in mans[m].get("stops") or []
                                                                       if isinstance(s, dict)}:
                    E.add("contradiction", r, f"store {r['from_id']} not a stop on {m}")
    for fid, sts in floater_task_stores.items():
        for sid in sts - floater_handoff.get(fid, set()):
            E.add("contradiction", None, f"one-sided: floater {fid} has tasks at {sid} but no FLOATER handoff")

    # ---------- playbooks
    for sid, r in pbs.items():
        if sid not in stores:
            E.add("reference", r, f"playbook store {sid} unknown"); continue
        if r.get("format") and r["format"] != stores[sid]["format"]:
            E.add("reference", r, f"format {r['format']} != data {stores[sid]['format']}")
        dl = deadline_for(sid)
        pdl = parse_dt(r.get("deadline"), store_tz(sid))
        if dl and pdl and pdl != dl:
            E.add("deadline", r, f"playbook deadline {r.get('deadline')} != scenario {dl.isoformat()}", severity="soft")
        for w_ in r.get("windows") or []:
            w = window(w_, store_tz(sid))
            if w is None:
                E.add("schema", r, f"bad window {w_!r}")
            elif dl and w[1] >= dl:
                E.add("deadline", r, f"playbook window ends {w[1].isoformat()} not before deadline")
        st_tasks = [t for t in tasks.values() if t.get("store_id") == sid]
        actual = Counter(t.get("action") for t in st_tasks)
        counts = r.get("counts") or {}
        if isinstance(counts, dict):
            for k, v in counts.items():
                key = str(k).upper().replace("_TASKS", "").replace("TASKS", "TOTAL").rstrip("S") \
                    if str(k).upper() not in actual and str(k).upper() not in {e.value for e in Action} else str(k).upper()
                key = {"HOLD": "HOLD_VERIFY", "SUB": "PLACE_SUB", "TAG": "TAG_FLASH", "TOTAL": "TOTAL"}.get(key, key)
                exp = len(st_tasks) if key == "TOTAL" else (actual.get(key, 0) if key in {e.value for e in Action}
                                                             else None)
                if exp is not None and isinstance(v, int) and v != exp:
                    E.add("contradiction", r, f"playbook counts[{k}]={v} but {exp} {key} tasks at {sid}")
        a_ids = set(r.get("associate_ids") or [])
        for x in a_ids:
            if x not in assocs:
                E.add("reference", r, f"associate {x} unknown")
        for t in st_tasks:
            if t.get("associate_id") and t["associate_id"] not in a_ids:
                E.add("contradiction", r, f"task {t.get('task_id')} associate {t['associate_id']} not in playbook",
                      severity="soft")
                break
        exc_ids = set(r.get("exception_ids") or [])
        for x in exc_ids:
            if x not in excs:
                E.add("reference", r, f"exception {x} missing")
        for xid, x in excs.items():
            if x.get("store_id") == sid and xid not in exc_ids:
                E.add("contradiction", r, f"exception {xid} for {sid} not listed in playbook")
        m_ids = set(r.get("manifest_ids") or [])
        for x in m_ids:
            if x not in mans:
                E.add("reference", r, f"manifest {x} missing")
            elif sid not in {s.get("store_id") for s in mans[x].get("stops") or [] if isinstance(s, dict)}:
                E.add("contradiction", r, f"manifest {x} has no stop at {sid}")
        for mid, m in mans.items():
            if sid in {s.get("store_id") for s in m.get("stops") or [] if isinstance(s, dict)} and mid not in m_ids:
                E.add("contradiction", r, f"manifest {mid} stops at {sid} but is not in its playbook")
    stores_with_tasks = {t.get("store_id") for t in tasks.values()}
    for sid in stores_with_tasks - set(pbs):
        if sid in stores:
            E.add("coverage", None, f"store {sid} has tasks but no store_playbook")

    # ---------- events.jsonl (optional, soft)
    ev_p = plan_p.parent / "events.jsonl"
    ev_stats = None
    if ev_p.exists():
        bad = unknown_task = 0; kinds = Counter(); n = 0
        for line in ev_p.read_text().splitlines():
            if not line.strip():
                continue
            n += 1
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                bad += 1; continue
            kinds[e.get("kind")] += 1
            if e.get("task_id") and e["task_id"] not in tasks:
                unknown_task += 1
            t = parse_dt(e.get("t"), store_tz(e.get("store_id")))
            dl = deadline_for(e.get("store_id"))
            if t and dl and t >= dl:
                E.add("deadline", {"type": "event", "src": "events.jsonl"}, f"event at {e.get('t')} after deadline")
        ev_stats = {"events": n, "bad_json": bad, "unknown_task_refs": unknown_task, "kinds": dict(kinds)}
        if bad or unknown_task:
            E.add("reference", {"type": "event", "src": "events.jsonl"},
                  f"events.jsonl: {bad} bad lines, {unknown_task} unknown task refs", severity="soft")

    # ---------- src -> token range
    src_tok = {}
    off_p = pathlib.Path(a.offsets) if a.offsets else ROOT / "gen" / name / "offsets.jsonl"
    if off_p.exists():
        for line in off_p.read_text().splitlines():
            try:
                o = json.loads(line); src_tok[o["path"]] = [o.get("start_tok"), o.get("end_tok")]
            except (json.JSONDecodeError, KeyError):
                pass

    by_check = defaultdict(lambda: {"hard": 0, "soft": 0})
    for k, v in E.count.items():
        c, sev = k.split(":"); by_check[c][sev] += v
    report = {
        "plan": str(plan_p), "scenario": scen_id, "state": scen_state,
        "deadline_local": deadline_naive.isoformat() if deadline_naive else None,
        "records": {t: len(v) for t, v in by_type.items()}, "bad_json_lines": n_bad_json,
        "hard_errors": E.hard(), "by_check": dict(by_check),
        "classification": {"labeled": len(labeled), "tp": tp, "fp": fp, "fn": fn,
                           "precision": round(precision, 4) if precision is not None else None,
                           "recall": round(recall, 4) if recall is not None else None,
                           "confusion": {t: dict(c) for t, c in conf.items()},
                           "decoys": len(decoys), "decoys_pulled": len(decoys_pulled),
                           "decoys_pulled_ids": decoys_pulled, "missing_verdicts": len(missing_verdicts),
                           "false_pulls": [s for s, t in labeled.items() if t != "PULL" and pred[s] == "PULL"][:50],
                           "missed_pulls": [s for s, t in labeled.items() if t == "PULL" and pred[s] != "PULL"][:50]},
        "coverage": {"pull_facings": cov_total, "pull_facings_tasked": cov_hit,
                     "rate": round(cov_hit / cov_total, 4) if cov_total else None,
                     "hold_facings": hold_total, "hold_facings_tasked": hold_hit},
        "events": ev_stats,
        "by_src": {s: {"counts": dict(c), "hard": sum(v for k, v in c.items() if k.endswith(":hard")),
                       "tok_range": src_tok.get(s)} for s, c in sorted(E.by_src.items())},
        "errors": E.items,
    }
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text(json.dumps(report, indent=2, default=str) + "\n")

    if not a.quiet:
        c = report["classification"]
        print(f"{plan_p}: {len(recs)} records {dict(sorted(report['records'].items()))}")
        print(f"  HARD ERRORS: {E.hard()}   " + "  ".join(f"{k}={v['hard']}" + (f"(+{v['soft']} soft)" if v['soft'] else "")
                                                for k, v in sorted(by_check.items())))
        print(f"  PULL precision {c['precision']} recall {c['recall']} (tp {tp} fp {fp} fn {fn}); "
              f"decoys pulled {c['decoys_pulled']}/{c['decoys']}; missing verdicts {c['missing_verdicts']}")
        hv = c["confusion"].get("HOLD_VERIFY", {})
        print(f"  HOLD_VERIFY truth -> {dict(hv)}")
        cv = report["coverage"]
        print(f"  coverage {cv['pull_facings_tasked']}/{cv['pull_facings']} PULL facings tasked; "
              f"HOLD {cv['hold_facings_tasked']}/{cv['hold_facings']}")
        for s, info in report["by_src"].items():
            if info["hard"] or info["counts"]:
                tr = f" tok {info['tok_range'][0]}-{info['tok_range'][1]}" if info["tok_range"] else ""
                print(f"  src {s}{tr}: {info['hard']} hard  {info['counts']}")
        shown = Counter()
        for e in E.items:
            if e["severity"] == "hard" and shown[e["check"]] < 3:
                shown[e["check"]] += 1
                print(f"    [{e['check']}] {e['src']} {e['type'] or ''} {e['id'] or ''}: {e['msg']}")
        print(f"  report {report_p}")
    return 0 if E.hard() == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
