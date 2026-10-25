"""Verification of all plan invariants: schema, refs, stock conservation, truck capacity, labor, deadlines, and contradictions."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from contract import Action, DataPack, Verdict
from recallstorm.core.clock import is_before_deadline, window_overlaps
from recallstorm.plan.assemble import validate_plan_refs


@dataclass(frozen=True)
class CheckReport:
    """Aggregated invariant check report."""

    passed: bool
    issues: dict[str, list[str]]


def check_refs(records: list[dict]) -> list[str]:
    """Check PLAN_TYPES schema and cross-record referential integrity."""
    return validate_plan_refs(records)


def check_conservation(records: list[dict], pack: DataPack) -> list[str]:
    """Check that substitute allocations never exceed initial DC stock and dc_balance_after is accurate."""
    avail: dict[tuple[str, str], int] = {}
    for d in pack.dc_stock:
        avail[(d.dc_id, d.sku_id)] = avail.get((d.dc_id, d.sku_id), 0) + d.cases

    issues: list[str] = []
    for r in records:
        if r.get("type") != "allocation":
            continue
        key = (str(r["dc_id"]), str(r["sub_sku_id"]))
        qty = int(r["qty_cases"])
        cur = avail.get(key, 0)
        if qty <= 0 or qty > cur:
            issues.append(f"Allocation {r.get('alloc_id')} qty {qty} exceeds available {cur} at {key}")
        new_bal = cur - qty
        if int(r["dc_balance_after"]) != new_bal:
            issues.append(f"Allocation {r.get('alloc_id')} balance_after {r.get('dc_balance_after')} != {new_bal}")
        avail[key] = new_bal
    return issues


def check_capacity(records: list[dict], pack: DataPack) -> list[str]:
    """Check that every route_manifest respects its truck's cube and weight limits."""
    trucks_by_id = {t.truck_id: t for t in pack.trucks}
    issues: list[str] = []
    for r in records:
        if r.get("type") != "route_manifest":
            continue
        tid = str(r["truck_id"])
        tr = trucks_by_id.get(tid)
        if tr is None:
            issues.append(f"Manifest {r.get('manifest_id')} references unknown truck {tid}")
            continue
        stops = r.get("stops", [])
        tot_cube = sum(float(s["cube_ft3"]) for s in stops)
        tot_wt = sum(float(s["weight_lb"]) for s in stops)
        if tot_cube > tr.cube_ft3 + 1e-6 or tot_wt > tr.weight_lb + 1e-6:
            issues.append(f"Manifest {r.get('manifest_id')} exceeds truck {tid} capacity")
    return issues


def check_labor(records: list[dict], pack: DataPack) -> list[str]:
    """Check that every shelf_task has a valid associate and floaters never work two stores in overlapping windows."""
    valid_assocs = {a.associate_id for a in pack.associates}
    floater_ids = {a.associate_id for a in pack.associates if a.is_floater}
    issues: list[str] = []
    floater_spans: dict[str, list[tuple[str, datetime, datetime]]] = {}

    for r in records:
        if r.get("type") != "shelf_task":
            continue
        aid = str(r.get("associate_id", ""))
        if valid_assocs and aid not in valid_assocs:
            issues.append(f"Task {r.get('task_id')} assigned to unknown associate {aid}")
        if aid in floater_ids and len(r.get("window", [])) == 2:
            s = datetime.fromisoformat(r["window"][0])
            e = datetime.fromisoformat(r["window"][1])
            floater_spans.setdefault(aid, []).append((str(r["store_id"]), s, e))

    for aid, spans in floater_spans.items():
        for i in range(len(spans)):
            for j in range(i + 1, len(spans)):
                st1, s1, e1 = spans[i]
                st2, s2, e2 = spans[j]
                if st1 != st2 and window_overlaps((s1, e1), (s2, e2)):
                    issues.append(f"Floater {aid} assigned to {st1} and {st2} in overlapping windows")
    return issues


def check_deadline(records: list[dict], deadline_iso: str) -> list[str]:
    """Verify that every task, playbook, and handoff window ends strictly before deadline_iso."""
    issues: list[str] = []
    for r in records:
        rtype = r.get("type")
        if rtype in ("shelf_task", "handoff"):
            w = r.get("window", [])
            if len(w) != 2 or not is_before_deadline(w[1], deadline_iso):
                issues.append(f"{rtype} {r} window {w} does not end before {deadline_iso}")
        elif rtype == "store_playbook":
            for w in r.get("windows", []):
                if len(w) != 2 or not is_before_deadline(w[1], deadline_iso):
                    issues.append(f"store_playbook {r.get('store_id')} window {w} does not end before {deadline_iso}")
    return issues


def check_contradictions(records: list[dict]) -> list[str]:
    """Check for contradictory verdicts or PULL tasks on KEEP SKUs."""
    verdicts: dict[str, str] = {}
    issues: list[str] = []
    for r in records:
        if r.get("type") == "sku_verdict":
            sk = str(r["sku_id"])
            v = str(r["verdict"])
            if sk in verdicts and verdicts[sk] != v:
                issues.append(f"Contradictory verdicts for {sk}: {verdicts[sk]} vs {v}")
            verdicts[sk] = v

    for r in records:
        if r.get("type") == "shelf_task":
            sk = str(r["sku_id"])
            act = str(r["action"])
            v = verdicts.get(sk)
            if v == Verdict.KEEP.value and act in (Action.PULL.value, Action.HOLD_VERIFY.value):
                issues.append(f"Task {r.get('task_id')} performs {act} on KEEP SKU {sk}")
    return issues


def run_all_checks(records: list[dict], pack: DataPack, deadline_iso: str) -> CheckReport:
    """Run all six invariant checks and return a CheckReport."""
    grouped = {
        "refs": check_refs(records),
        "conservation": check_conservation(records, pack),
        "capacity": check_capacity(records, pack),
        "labor": check_labor(records, pack),
        "deadline": check_deadline(records, deadline_iso),
        "contradictions": check_contradictions(records),
    }
    passed = all(len(v) == 0 for v in grouped.values())
    return CheckReport(passed=passed, issues=grouped)


def checks_to_json(report: CheckReport) -> str:
    """Serialize a CheckReport to JSON."""
    return json.dumps({"passed": report.passed, "issues": report.issues}, indent=2, sort_keys=True)
