"""OURS. Baseline D plan builder: verdicts -> shelf tasks -> allocation -> routes -> schedule -> plan.jsonl."""
from __future__ import annotations

import json
import math
import pathlib
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from contract import Action, ExceptionKind, HandoffKind, Verdict, load_datapack

from . import allocate, route, rules, sim
from ._src import src_of

SRC = src_of(__file__)
TASK_MIN = {Action.PULL: 3, Action.HOLD_VERIFY: 2, Action.PLACE_SUB: 3}

NOTE_KINDS = [  # first keyword hit wins
    (re.compile(r"\bDSD\b|vendor-pulled", re.I), ExceptionKind.DSD_VENDOR_PULL,
     "vendor pulls DSD items; do not pack them for DC return"),
    (re.compile(r"endcap|display", re.I), ExceptionKind.ENDCAP_DISPLAY,
     "sweep the display by hand for affected items"),
    (re.compile(r"topstock|overflow", re.I), ExceptionKind.TOPSTOCK,
     "check topstock overflow cases for affected items"),
    (re.compile(r"pickup|totes", re.I), ExceptionKind.PICKUP_TOTES,
     "open staged pickup totes and remove affected items"),
    (re.compile(r"planogram|remodel|moved", re.I), ExceptionKind.NOT_ON_PLANOGRAM,
     "locations off planogram; search the moved area by hand"),
    (re.compile(r"smudged|label|illegible|by hand", re.I), ExceptionKind.UNCLEAR_LABEL,
     "verify ingredients by hand; hold unclear items"),
]


def _iso(d: datetime) -> str:
    return d.isoformat()


def _loc(loc) -> dict:
    return {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos}


def build(scenario_id: str, data_dir: str, classifier=None, generator: str = "baseline_d"):
    pack = load_datapack(data_dir)
    scen = json.loads((pathlib.Path(data_dir) / f"scenario_{scenario_id}.json").read_text())
    state = scen.get("state", "CA")
    deadline = datetime.fromisoformat(scen["deadline"])
    as_of = datetime.fromisoformat(scen["as_of"])
    rule_by_id = {r.rule_id: r for r in pack.rules}
    sku_by_id = {s.sku_id: s for s in pack.skus}
    out: list[dict] = []

    out.append({"type": "run", "run_id": f"{generator}-{scenario_id}", "scenario_id": scenario_id,
                "generator": generator, "as_of": _iso(as_of), "rule_ids": list(scen.get("rule_ids", [])),
                "src": SRC})

    # ---- verdicts (evaluated at the deadline instant: what must be off the shelf by then)
    decisions = {}
    for s in sorted(pack.skus, key=lambda s: s.sku_id):
        d = rules.evaluate_sku(s, pack.rules, state, deadline, classifier)
        decisions[s.sku_id] = d
        v = Verdict(getattr(d.verdict, "value", d.verdict))
        eid = None
        if v in (Verdict.PULL, Verdict.HOLD_VERIFY) and d.rule_ids:
            eid = f"EV-{s.sku_id}"
            r0 = rule_by_id[d.rule_ids[0]]
            out.append({"type": "evidence", "evidence_id": eid, "sku_id": s.sku_id, "rule_id": r0.rule_id,
                        "clause_ref": r0.clause_ref,
                        "source_span": {"start": 0, "end": len(r0.source_text), "text": r0.source_text},
                        "rationale": d.rationale, "src": rules.SRC})
        match = None
        if d.match_start is not None:
            match = {"text": d.match_text, "start": d.match_start, "end": d.match_end}
        out.append({"type": "sku_verdict", "sku_id": s.sku_id, "gtin": s.gtin, "verdict": v.value,
                    "additive": d.additive, "match": match, "rule_ids": list(d.rule_ids),
                    "jurisdictions": sorted({j for rid in d.rule_ids for j in rule_by_id[rid].jurisdictions}),
                    "decided_by": getattr(d.decided_by, "value", d.decided_by), "evidence_id": eid,
                    "src": rules.SRC})
    verdict = {k: Verdict(getattr(d.verdict, "value", d.verdict)) for k, d in decisions.items()}

    # ---- shelf work per store
    stores = sorted(pack.stores, key=lambda s: s.store_id)
    facings_by_store = defaultdict(list)
    for f in pack.facings:
        facings_by_store[f.store_id].append(f)
    raw_tasks = defaultdict(list)     # store -> [(action, facing)]
    pulled_cases: dict[tuple[str, str], int] = defaultdict(int)
    demand: dict[tuple[str, str], int] = defaultdict(int)
    sub_facing: dict[tuple[str, str], object] = {}
    for st in stores:
        for f in sorted(facings_by_store[st.store_id],
                        key=lambda f: (f.loc.aisle, f.loc.bay, f.loc.shelf, f.loc.pos, f.sku_id)):
            v = verdict.get(f.sku_id)
            if v == Verdict.PULL:
                raw_tasks[st.store_id].append((Action.PULL, f))
                sk = sku_by_id[f.sku_id]
                pulled_cases[(st.store_id, f.sku_id)] += max(1, math.ceil(f.units / max(1, sk.case_units)))
                subs = [x for x in pack.substitutes.get(f.sku_id, [])
                        if x in sku_by_id and verdict.get(x) == Verdict.KEEP]
                if subs:
                    sub = subs[0]
                    demand[(st.store_id, sub)] += max(1, math.ceil(f.units / max(1, sku_by_id[sub].case_units)))
                    sub_facing.setdefault((st.store_id, sub), f)
            elif v == Verdict.HOLD_VERIFY:
                raw_tasks[st.store_id].append((Action.HOLD_VERIFY, f))

    allocs = allocate.allocate_substitutes(dict(demand), pack.dc_stock, pack.stores)
    for a in allocs:
        out.append({"type": "allocation", "alloc_id": a.alloc_id, "dc_id": a.dc_id, "sub_sku_id": a.sub_sku_id,
                    "store_id": a.store_id, "qty_cases": a.qty_cases, "dc_balance_after": a.dc_balance_after,
                    "src": allocate.SRC})
    allocs_by_store = defaultdict(list)
    for a in allocs:
        allocs_by_store[a.store_id].append(a)

    manifests = route.pack_returns(dict(pulled_cases), pack.skus, pack.trucks, pack.stores)
    man_by_store = defaultdict(list)
    for m in manifests:
        tr = next(t for t in pack.trucks if t.truck_id == m.truck_id)
        out.append({"type": "route_manifest", "manifest_id": m.manifest_id, "truck_id": m.truck_id,
                    "dc_id": m.dc_id,
                    "stops": [{"store_id": s.store_id, "cases": s.cases, "cube_ft3": s.cube_ft3,
                               "weight_lb": s.weight_lb} for s in m.stops],
                    "limits": {"cube_ft3": tr.cube_ft3, "weight_lb": tr.weight_lb},
                    "depart": _iso(m.depart), "src": route.SRC})
        for s in m.stops:
            man_by_store[s.store_id].append(m)

    # ---- labor: sequential cursor per associate, round-robin; floaters only if the store runs out of shift
    assoc_by_store = defaultdict(list)
    floaters_by_district = defaultdict(list)
    for a in sorted(pack.associates, key=lambda a: a.associate_id):
        if a.is_floater:
            floaters_by_district[a.district].append(a)
        elif a.store_id:
            assoc_by_store[a.store_id].append(a)
    cursor = {a.associate_id: a.shift_start for a in pack.associates}

    def latest_end(a):
        return min(a.shift_end, deadline - timedelta(minutes=1))

    tasks_out, events_tasks = [], []
    playbooks, exceptions_out, handoffs = [], [], []
    for st in stores:
        sid = st.store_id
        work = list(raw_tasks[sid])
        sub_by_alloc = []
        for a in sorted(allocs_by_store[sid], key=lambda a: a.alloc_id):
            sub_by_alloc.append((Action.PLACE_SUB, sub_facing[(sid, a.sub_sku_id)], a))
        items = [(act, f, None) for act, f in work] + sub_by_alloc
        if not items and not any(n.store_id == sid for n in pack.notes):
            continue
        staff = assoc_by_store[sid]
        rr = 0
        store_tasks = []
        floater_use = defaultdict(list)
        for seq, (act, f, alloc) in enumerate(items, 1):
            dur = timedelta(minutes=TASK_MIN[act])
            chosen = None
            for k in range(len(staff)):
                a = staff[(rr + k) % len(staff)]
                if cursor[a.associate_id] + dur <= latest_end(a):
                    chosen = a; rr = (rr + k + 1) % len(staff); break
            if chosen is None:
                for a in floaters_by_district[st.district]:
                    if cursor[a.associate_id] + dur <= latest_end(a):
                        chosen = a; break
            if chosen is None:
                raise RuntimeError(f"not enough labor at {sid}")
            t0 = cursor[chosen.associate_id]; t1 = t0 + dur
            cursor[chosen.associate_id] = t1
            if chosen.is_floater:
                floater_use[chosen.associate_id].append((t0, t1))
            tid = f"T-{sid}-{seq:05d}"
            sku = sku_by_id[f.sku_id]
            rec = {"type": "shelf_task", "task_id": tid, "store_id": sid, "sku_id": f.sku_id,
                   "action": act.value, "loc": _loc(f.loc),
                   "qty_units": f.units if act != Action.PLACE_SUB else alloc.qty_cases * sku_by_id[alloc.sub_sku_id].case_units,
                   "associate_id": chosen.associate_id, "window": [_iso(t0), _iso(t1)], "seq": seq,
                   "evidence_id": f"EV-{f.sku_id}" if act != Action.PLACE_SUB or verdict[f.sku_id] != Verdict.KEEP else None,
                   "sub_sku_id": alloc.sub_sku_id if alloc else None, "alloc_id": alloc.alloc_id if alloc else None,
                   "src": SRC}
            store_tasks.append(rec)
            del sku
        tasks_out.extend(store_tasks)

        exc_ids = []
        for n in sorted((n for n in pack.notes if n.store_id == sid), key=lambda n: n.note_id):
            for rx, kind, res in NOTE_KINDS:
                if rx.search(n.text):
                    xid = f"X-{n.note_id}"
                    linked = [t["task_id"] for t in store_tasks if kind == ExceptionKind.UNCLEAR_LABEL
                              and t["action"] == Action.HOLD_VERIFY.value]
                    exceptions_out.append({"type": "exception", "exc_id": xid, "store_id": sid, "kind": kind.value,
                                           "note_id": n.note_id, "resolution": res, "task_ids": linked, "src": SRC})
                    exc_ids.append(xid)
                    break

        for fid, ws in sorted(floater_use.items()):
            handoffs.append({"type": "handoff", "handoff_id": f"H-FL-{fid}-{sid}", "kind": HandoffKind.FLOATER.value,
                             "from_id": f"DISTRICT_{st.district}", "to_id": sid,
                             "window": [_iso(min(w[0] for w in ws)), _iso(max(w[1] for w in ws))],
                             "qty": len(ws), "ref_ids": [fid], "src": SRC})
        for a in sorted(allocs_by_store[sid], key=lambda a: a.alloc_id):
            tr = [t for t in pack.trucks if t.dc_id == a.dc_id]
            dep = min(t.depart for t in tr) if tr else deadline - timedelta(hours=12)
            handoffs.append({"type": "handoff", "handoff_id": f"H-SUB-{a.alloc_id}", "kind": HandoffKind.SUB_TRANSFER.value,
                             "from_id": a.dc_id, "to_id": sid, "window": [_iso(dep), _iso(dep + timedelta(hours=6))],
                             "qty": a.qty_cases, "ref_ids": [a.alloc_id], "src": SRC})
        for m in man_by_store[sid]:
            cases = sum(s.cases for s in m.stops if s.store_id == sid)
            handoffs.append({"type": "handoff", "handoff_id": f"H-RET-{m.manifest_id}-{sid}",
                             "kind": HandoffKind.RETURN_CONSOLIDATION.value, "from_id": sid, "to_id": m.dc_id,
                             "window": [_iso(m.depart - timedelta(hours=2)), _iso(m.depart)],
                             "qty": cases, "ref_ids": [m.manifest_id], "src": SRC})

        cnt = Counter(t["action"] for t in store_tasks)
        windows = ([[min(t["window"][0] for t in store_tasks), max(t["window"][1] for t in store_tasks)]]
                   if store_tasks else [])
        playbooks.append({"type": "store_playbook", "store_id": sid, "format": st.format.value,
                          "deadline": _iso(deadline), "windows": windows,
                          "counts": {**{a.value: cnt.get(a.value, 0) for a in Action}, "TOTAL": len(store_tasks)},
                          "associate_ids": sorted({t["associate_id"] for t in store_tasks}),
                          "exception_ids": exc_ids, "manifest_ids": sorted({m.manifest_id for m in man_by_store[sid]}),
                          "src": SRC})

    out.extend(playbooks); out.extend(tasks_out); out.extend(exceptions_out); out.extend(handoffs)
    return out, tasks_out, decisions


def run(scenario_id: str, data_dir: str, out_dir: str, classifier=None, generator: str = "baseline_d") -> dict:
    t0 = time.time()
    recs, tasks, decisions = build(scenario_id, data_dir, classifier, generator)
    o = pathlib.Path(out_dir); o.mkdir(parents=True, exist_ok=True)
    with open(o / "plan.jsonl", "w") as fh:
        for r in recs:
            fh.write(json.dumps(r, default=str) + "\n")
    n_ev = sim.write_events(tasks, o / "events.jsonl")
    vc = Counter(getattr(d.verdict, "value", d.verdict) for d in decisions.values())
    return {"records": len(recs), "tasks": len(tasks), "events": n_ev, "verdicts": dict(vc),
            "seconds": round(time.time() - t0, 2)}
