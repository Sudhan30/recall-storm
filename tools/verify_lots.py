"""OURS. Lot-level verifier for the fda_lots scenario (real openFDA notices, simulated shelf lots).

Usage: python tools/verify_lots.py out/<name>/plan.jsonl [--labels data/labels_fda.csv] [--data data/]
                                   [--scenario data/scenario_fda_lots.json] [--name <name>] [--report reports/<name>_lots.json]

A shelf_task is mapped to a shelf lot (data/lots.jsonl) by
  1. an optional "lot" field on the task (normalized: uppercase, leading LOT/BATCH dropped, non-alnum dropped)
     matched against the lots of that (store, sku), else
  2. its loc: each simulated lot sits at its own (store, aisle, bay, shelf, pos) -- contract.Facing has no lot
     field, so loc is how a contract-shaped plan says which lot it means.
A task that maps to no shelf lot is a reference error.

Checks (hard = counts toward the exit code):
  schema      record type in contract.PLAN_TYPES, required fields, Action enum            (hard)
  reference   unknown store/sku/associate/evidence_id, task mapping to no shelf lot, dup ids (hard)
  overpull    PULL task on a truth-KEEP lot ("non-recalled lots pulled", must be 0)       (hard)
  coverage    every truth-PULL (store, lot) has a PULL task                               (hard)
  deadline    every task window ends before the scenario deadline                         (hard)
  labor       window inside the associate's shift, associate belongs to the store (or is a
              floater of its district), no overlapping windows per associate, minutes <= shift (hard)
  hold        truth-HOLD_VERIFY lots with no PULL/HOLD_VERIFY task                         (soft)
  qty         PULL qty_units below the lot's shelf units                                   (soft)
Reported: lot-level PULL precision / recall (lots and units), confusion truth x action.
Helpers (Errs, rows, parse_dt, window) are imported from tools/verify_plan.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "data"))
from contract import PLAN_TYPES, Action  # noqa: E402
from verify_plan import Errs, rows, parse_dt, window  # noqa: E402
from build_fda_lots import norm_lot  # noqa: E402

ACTIONS = {a.value for a in Action}


def loc_key(loc) -> tuple | None:
    if not isinstance(loc, dict):
        return None
    try:
        return (str(loc["aisle"]), int(loc["bay"]), int(loc["shelf"]), int(loc["pos"]))
    except (KeyError, TypeError, ValueError):
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan"); ap.add_argument("--labels", default=str(ROOT / "data" / "labels_fda.csv"))
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--scenario", default=str(ROOT / "data" / "scenario_fda_lots.json"))
    ap.add_argument("--name"); ap.add_argument("--report"); ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    plan_p = pathlib.Path(a.plan); D = pathlib.Path(a.data)
    name = a.name or plan_p.parent.name
    report_p = pathlib.Path(a.report) if a.report else ROOT / "reports" / f"{name}_lots.json"
    E = Errs()

    scen = json.loads(pathlib.Path(a.scenario).read_text())
    stores = {r["store_id"]: r for r in rows(D / "stores.jsonl")}
    skus = {r["sku_id"]: r for r in rows(D / "skus_fda.jsonl")}
    assocs = {r["associate_id"]: r for r in rows(D / "associates.jsonl")}
    lots = rows(D / "lots.jsonl")
    truth = {}
    with open(a.labels, newline="") as fh:
        for r in csv.DictReader(fh):
            truth[(r["store_id"], r["sku_id"], norm_lot(r["lot"]))] = r
    by_loc = {(x["store_id"], loc_key(x["loc"])): x for x in lots}
    by_lot = {(x["store_id"], x["sku_id"], norm_lot(x["lot"])): x for x in lots}

    def tz(sid):
        return (stores.get(sid) or {}).get("tz") or "America/Los_Angeles"
    deadline = parse_dt(scen["deadline"], None)
    as_of = parse_dt(scen["as_of"], None)

    # ---------- plan
    recs, text = [], (plan_p.read_text(encoding="utf-8", errors="replace") if plan_p.exists() else "")
    if not plan_p.exists():
        E.add("schema", None, f"plan file missing: {plan_p}")
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            E.add("schema", {"_line": i, "src": "<unparseable>"}, f"bad JSON: {e.msg}"); continue
        if not isinstance(r, dict):
            E.add("schema", {"_line": i}, "record is not an object"); continue
        r["_line"] = i; recs.append(r)
    types = Counter(r.get("type") for r in recs)
    for r in recs:
        t = r.get("type")
        if t not in PLAN_TYPES:
            E.add("schema", r, f"unknown record type {t!r}"); continue
        miss = [f for f in PLAN_TYPES[t] if f not in r]
        if miss:
            E.add("schema", r, f"{t} missing fields: {', '.join(miss)}")
    tasks = [r for r in recs if r.get("type") == "shelf_task"]
    seen_ids = {}
    for r in tasks:
        tid = r.get("task_id")
        if tid in seen_ids:
            E.add("reference", r, f"duplicate task_id {tid!r} (first at line {seen_ids[tid]})")
        else:
            seen_ids[tid] = r["_line"]

    ev_ids = {r.get("evidence_id") for r in recs if r.get("type") == "evidence"}
    for r in tasks:
        if r.get("evidence_id") and r["evidence_id"] not in ev_ids:
            E.add("reference", r, f"evidence_id {r['evidence_id']} missing")

    # ---------- map tasks to lots
    acts = defaultdict(set)          # lot key -> actions
    pulled_qty = defaultdict(int)
    for r in tasks:
        sid, sk, act = r.get("store_id"), r.get("sku_id"), r.get("action")
        if act not in ACTIONS:
            E.add("schema", r, f"action {act!r} not in contract enum")
        if sid not in stores:
            E.add("reference", r, f"store {sid} unknown"); continue
        if sk not in skus:
            E.add("reference", r, f"sku {sk} unknown")
        key = None
        if r.get("lot"):
            k = (sid, sk, norm_lot(str(r["lot"])))
            key = k if k in by_lot else None
            if key is None:
                E.add("reference", r, f"task lot {r['lot']!r} is not on the shelf at {sid}/{sk}")
                continue
        else:
            x = by_loc.get((sid, loc_key(r.get("loc"))))
            if x is None or x["sku_id"] != sk:
                E.add("reference", r, f"task loc {r.get('loc')} at {sid} holds no lot of {sk}")
                continue
            key = (sid, sk, norm_lot(x["lot"]))
        acts[key].add(act)
        if act == "PULL" and isinstance(r.get("qty_units"), int):
            pulled_qty[key] += r["qty_units"]
        lab = truth.get(key)
        if act == "PULL" and lab and lab["truth"] == "KEEP":
            E.add("overpull", r, f"non-recalled lot {lab['lot']!r} of {sk} pulled at {sid} "
                                 f"(recall {lab['recall_number']}, best_by {lab['best_by']})", severity="hard")

    # ---------- scoring
    units = {k: by_lot[k]["units"] for k in by_lot}
    conf = defaultdict(Counter)
    tp = fp = fn = 0; tpu = fpu = fnu = 0
    for k, lab in truth.items():
        a_ = acts.get(k, set())
        pa = "PULL" if "PULL" in a_ else ("HOLD_VERIFY" if "HOLD_VERIFY" in a_ else ("OTHER" if a_ else "NONE"))
        conf[lab["truth"]][pa] += 1
        u = units.get(k, 0)
        if lab["truth"] == "PULL":
            if pa == "PULL":
                tp += 1; tpu += u
                if pulled_qty[k] < u:
                    E.add("qty", None, f"PULL qty {pulled_qty[k]} < shelf units {u} for {k}", severity="soft")
            else:
                fn += 1; fnu += u
                E.add("coverage", None, f"truth-PULL lot {lab['lot']!r} of {k[1]} at {k[0]} has no PULL task "
                                        f"(recall {lab['recall_number']}, basis {lab['basis']})", severity="hard")
        elif pa == "PULL":
            fp += 1; fpu += u
        if lab["truth"] == "HOLD_VERIFY" and pa == "NONE":
            E.add("hold", None, f"ambiguous lot {lab['lot']!r} of {k[1]} at {k[0]} not held or pulled", severity="soft")
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    keep_pulled = conf["KEEP"]["PULL"]

    # ---------- deadline + labor
    per_assoc = defaultdict(list)
    for r in tasks:
        sid = r.get("store_id")
        w = window(r.get("window"), tz(sid))
        if w is None:
            E.add("schema", r, f"bad window {r.get('window')!r}"); continue
        s0, s1 = w
        if s1 <= s0:
            E.add("labor", r, f"window end <= start {r.get('window')}", severity="hard")
        if deadline and s1 >= deadline:
            E.add("deadline", r, f"window ends {s1.isoformat()} not before deadline {deadline.isoformat()}", severity="hard")
        if as_of and s0 < as_of:
            E.add("deadline", r, f"window starts {s0.isoformat()} before as_of", severity="soft")
        aid = r.get("associate_id")
        if aid is None:
            E.add("labor", r, "task without associate", severity="hard"); continue
        asc = assocs.get(aid)
        if asc is None:
            E.add("reference", r, f"associate {aid} unknown"); continue
        sh0, sh1 = parse_dt(asc["shift_start"], None), parse_dt(asc["shift_end"], None)
        if s0 < sh0 or s1 > sh1:
            E.add("labor", r, f"window {r.get('window')} outside shift of {aid}", severity="hard")
        if asc["is_floater"]:
            if (stores.get(sid) or {}).get("district") != asc["district"]:
                E.add("labor", r, f"floater {aid} outside district {asc['district']}", severity="hard")
        elif asc["store_id"] != sid:
            E.add("labor", r, f"associate {aid} of {asc['store_id']} assigned at {sid}", severity="hard")
        per_assoc[aid].append((s0, s1, r))
    for aid, lst in per_assoc.items():
        lst.sort(key=lambda x: (x[0], x[1]))
        asc = assocs[aid]
        shift = (parse_dt(asc["shift_end"], None) - parse_dt(asc["shift_start"], None)).total_seconds() / 60
        mins = sum((b - a0).total_seconds() / 60 for a0, b, _ in lst)
        if mins > shift + 1e-6:
            E.add("labor", lst[0][2], f"{aid} assigned {mins:.0f} min > shift {shift:.0f} min", severity="hard")
        for (a0, a1, ra), (b0, b1, rb) in zip(lst, lst[1:]):
            if b0 < a1:
                E.add("labor", rb, f"{aid} overlaps {ra.get('task_id')} and {rb.get('task_id')}", severity="hard")

    by_check = defaultdict(lambda: {"hard": 0, "soft": 0})
    for k, v in E.count.items():
        c, sev = k.split(":"); by_check[c][sev] += v
    cov_total = sum(1 for l in truth.values() if l["truth"] == "PULL")
    report = {
        "plan": str(plan_p), "scenario": scen.get("scenario_id"), "deadline": scen.get("deadline"),
        "records": dict(types), "shelf_tasks": len(tasks), "hard_errors": E.hard(), "by_check": dict(by_check),
        "lots": {"labeled": len(truth), "truth": dict(Counter(l["truth"] for l in truth.values())),
                 "tp": tp, "fp": fp, "fn": fn,
                 "precision": round(prec, 4) if prec is not None else None,
                 "recall": round(rec, 4) if rec is not None else None,
                 "units": {"tp": tpu, "fp": fpu, "fn": fnu},
                 "non_recalled_lots_pulled": keep_pulled,
                 "hold_lots_pulled": conf["HOLD_VERIFY"]["PULL"],
                 "confusion": {t: dict(c) for t, c in conf.items()}},
        "coverage": {"pull_lots": cov_total, "pull_lots_tasked": tp,
                     "rate": round(tp / cov_total, 4) if cov_total else None},
        "by_src": {s: dict(c) for s, c in sorted(E.by_src.items())},
        "errors": E.items,
    }
    report_p.parent.mkdir(parents=True, exist_ok=True)
    report_p.write_text(json.dumps(report, indent=2, default=str) + "\n")
    if not a.quiet:
        L = report["lots"]
        print(f"{plan_p}: {len(recs)} records, {len(tasks)} shelf_tasks")
        print(f"  HARD ERRORS: {E.hard()}   " + "  ".join(f"{k}={v['hard']}" + (f"(+{v['soft']} soft)" if v['soft'] else "")
                                                for k, v in sorted(by_check.items())))
        print(f"  lot PULL precision {L['precision']} recall {L['recall']} (tp {tp} fp {fp} fn {fn}); "
              f"non-recalled lots pulled {keep_pulled}; HOLD lots pulled {L['hold_lots_pulled']}")
        print(f"  confusion {L['confusion']}")
        shown = Counter()
        for e in E.items:
            if e["severity"] == "hard" and shown[e["check"]] < 3:
                shown[e["check"]] += 1
                print(f"    [{e['check']}] {e['src']} {e['id'] or ''}: {e['msg']}")
        print(f"  report {report_p}")
    return 0 if E.hard() == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
