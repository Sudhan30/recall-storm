"""Invariant checks for referential integrity, stock conservation, truck capacity, labor, and deadlines."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json

from contract import Associate, DataPack, DcStock
from recallstorm.plan.assemble import validate_plan_refs
from recallstorm.plan.deadline import deadline_violations


@dataclass
class CheckReport:
    """Comprehensive D1-D6 invariant check report."""

    passed: bool
    issues: dict[str, list[str]] = field(default_factory=dict)


def check_refs(records: list[dict]) -> list[str]:
    """Verify schema and cross-record ID references across records."""
    return validate_plan_refs(records)


def check_conservation(records: list[dict], stock: list[DcStock] | None = None) -> list[str]:
    """Verify that substitute allocations never have negative balances or exceed initial DC stock."""
    issues: list[str] = []
    init_map: dict[tuple[str, str], int] = {}
    if stock:
        for s in stock:
            k = (s.dc_id, s.sku_id)
            init_map[k] = init_map.get(k, 0) + s.cases

    used: dict[tuple[str, str], int] = {}
    for r in records:
        if r.get("type") == "allocation":
            qty = int(r.get("qty_cases", 0))
            bal = int(r.get("dc_balance_after", 0))
            if qty <= 0:
                issues.append(f"Allocation {r.get('alloc_id')} has non-positive qty_cases={qty}")
            if bal < 0:
                issues.append(f"Allocation {r.get('alloc_id')} has negative dc_balance_after={bal}")
            key = (str(r.get("dc_id")), str(r.get("sub_sku_id")))
            used[key] = used.get(key, 0) + qty
            if stock and used[key] > init_map.get(key, 0):
                issues.append(f"Allocations for {key} ({used[key]}) exceed DC stock ({init_map.get(key, 0)})")
    return issues


def check_capacity(records: list[dict]) -> list[str]:
    """Verify that no route_manifest exceeds its truck's cube or weight limits."""
    issues: list[str] = []
    for r in records:
        if r.get("type") == "route_manifest":
            limits = r.get("limits") or {}
            max_c = float(limits.get("cube_ft3", 3400.0))
            max_w = float(limits.get("weight_lb", 40000.0))
            stops = r.get("stops") or []
            tot_c = sum(float(s.get("cube_ft3", 0.0)) for s in stops)
            tot_w = sum(float(s.get("weight_lb", 0.0)) for s in stops)
            if tot_c > max_c + 1e-4:
                issues.append(f"Manifest {r.get('manifest_id')} cube {tot_c} > limit {max_c}")
            if tot_w > max_w + 1e-4:
                issues.append(f"Manifest {r.get('manifest_id')} weight {tot_w} > limit {max_w}")
    return issues


def check_labor(records: list[dict], associates: list[Associate] | None = None) -> list[str]:
    """Verify that every shelf_task has an assigned associate and valid window."""
    issues: list[str] = []
    for r in records:
        if r.get("type") == "shelf_task":
            if not r.get("associate_id"):
                issues.append(f"Task {r.get('task_id')} missing associate_id")
            win = r.get("window") or []
            if len(win) != 2 or win[1] < win[0]:
                issues.append(f"Task {r.get('task_id')} has invalid window {win}")
    return issues


def check_deadline(records: list[dict], deadline_iso: str | None = None) -> list[str]:
    """Verify that every task and playbook window ends strictly before the scenario deadline."""
    dl_str = deadline_iso
    if not dl_str:
        pb = next((r for r in records if r.get("type") == "store_playbook"), None)
        dl_str = pb["deadline"] if pb and "deadline" in pb else "2027-01-01T00:00:00-08:00"
    dl = datetime.fromisoformat(str(dl_str))
    return deadline_violations(records, dl)


def check_contradictions(records: list[dict]) -> list[str]:
    """Check for contradictory SKU verdicts or KEEP SKUs scheduled for PULL."""
    issues: list[str] = []
    verdicts: dict[str, str] = {}
    for r in records:
        if r.get("type") == "sku_verdict":
            sid = str(r.get("sku_id"))
            v = str(r.get("verdict"))
            if sid in verdicts and verdicts[sid] != v:
                issues.append(f"Contradictory verdicts for {sid}: {verdicts[sid]} vs {v}")
            verdicts[sid] = v
    for r in records:
        if r.get("type") == "shelf_task" and r.get("action") == "PULL":
            sid = str(r.get("sku_id"))
            if verdicts.get(sid) == "KEEP":
                issues.append(f"Task {r.get('task_id')} pulls SKU {sid} whose verdict is KEEP")
    return issues


def run_all_checks(
    records: list[dict], pack: DataPack | None = None, deadline_iso: str | None = None
) -> CheckReport:
    """Run all six invariant checks on plan.jsonl records."""
    issues = {
        "refs": check_refs(records),
        "conservation": check_conservation(records, pack.dc_stock if pack else None),
        "capacity": check_capacity(records),
        "labor": check_labor(records, pack.associates if pack else None),
        "deadline": check_deadline(records, deadline_iso),
        "contradictions": check_contradictions(records),
    }
    passed = all(len(v) == 0 for v in issues.values())
    return CheckReport(passed=passed, issues=issues)


def checks_to_json(report: CheckReport) -> str:
    """Serialize CheckReport to JSON."""
    return json.dumps({"passed": report.passed, "issues": report.issues}, indent=2, sort_keys=True)
