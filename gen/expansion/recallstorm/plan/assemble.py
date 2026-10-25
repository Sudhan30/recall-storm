"""End-to-end recall plan assembly, referential integrity validation, and JSONL output."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from contract import (
    Action,
    Allocation,
    DataPack,
    ExceptionKind,
    RouteManifest,
    SkuDecision,
    Verdict,
)
from recallstorm.adjudicate.evidence import link_evidence
from recallstorm.allocate.allocator import allocate_substitutes, allocation_records
from recallstorm.allocate.demand import demand_from_facings, substitute_for_sku
from recallstorm.core.clock import is_before_deadline, iso_with_offset
from recallstorm.core.ids import make_run_id
from recallstorm.core.jsonl import record_with_src, stable_dumps, validate_record, write_jsonl
from recallstorm.plan.deadline import enforce_deadline
from recallstorm.plan.exceptions_plan import exception_records
from recallstorm.plan.handoffs import build_handoffs
from recallstorm.plan.playbook import build_playbook
from recallstorm.plan.tasks import build_shelf_tasks
from recallstorm.rules.engine import decision_to_record, evaluate_sku
from recallstorm.store.exceptions import exception_kind_for_text


@dataclass(frozen=True)
class PlanAssembler:
    """Orchestrates end-to-end plan.jsonl generation from a DataPack and scenario."""

    scenario_id: str
    state: str
    rule_ids: tuple[str, ...]
    as_of: datetime
    deadline: datetime


def run_record(
    scenario_id: str,
    as_of: datetime | str,
    rule_ids: list[str] | tuple[str, ...],
    generator: str = "recallstorm/1.0",
) -> dict:
    """Create a validated 'run' plan.jsonl record."""
    as_of_iso = as_of.isoformat(timespec="seconds") if isinstance(as_of, datetime) else str(as_of)
    payload = {
        "run_id": make_run_id(scenario_id, as_of_iso),
        "scenario_id": scenario_id,
        "generator": generator,
        "as_of": as_of_iso,
        "rule_ids": list(rule_ids),
    }
    return record_with_src(payload, "run", "recallstorm/plan/assemble.py")


def plan_records(
    run_rec: dict,
    verdicts: list[dict],
    evidences: list[dict],
    playbooks: list[dict],
    tasks: list[dict],
    exceptions: list[dict],
    allocations: list[dict],
    handoffs: list[dict],
    manifests: list[dict],
) -> list[dict]:
    """Combine all nine PLAN_TYPES record groups in canonical deterministic order."""
    return (
        [run_rec]
        + verdicts
        + evidences
        + playbooks
        + tasks
        + exceptions
        + allocations
        + handoffs
        + manifests
    )


def assemble_plan(
    pack: DataPack,
    scenario: dict | None = None,
    manifest_packer=None,
) -> list[dict]:
    """Assemble a complete, referentially valid plan.jsonl record list for a DataPack and scenario."""
    scen = scenario or {}
    scenario_id = str(scen.get("scenario_id", "ca_red3"))
    state = str(scen.get("state", "CA"))
    as_of_str = str(scen.get("as_of", pack.as_of.isoformat()))
    deadline_str = str(scen.get("deadline", "2027-01-01T00:00:00-08:00"))
    as_of_dt = datetime.fromisoformat(as_of_str)
    deadline_dt = datetime.fromisoformat(deadline_str)

    wanted_rule_ids = set(scen.get("rule_ids", [r.rule_id for r in pack.rules]))
    active_rules = [r for r in pack.rules if r.rule_id in wanted_rule_ids] or list(pack.rules)
    rule_ids = [r.rule_id for r in active_rules]

    # Evaluate SKUs at the scenario compliance deadline so rules taking effect at deadline trigger PULL
    eval_dt = deadline_dt
    skus_sorted = sorted(pack.skus, key=lambda s: s.sku_id)
    skus_by_id = {s.sku_id: s for s in skus_sorted}
    rules_by_id = {r.rule_id: r for r in active_rules}
    stores_sorted = sorted(pack.stores, key=lambda s: s.store_id)
    stores_by_id = {s.store_id: s for s in stores_sorted}

    decisions: dict[str, SkuDecision] = {}
    for sku in skus_sorted:
        decisions[sku.sku_id] = evaluate_sku(sku, active_rules, state, eval_dt)

    evidences_by_sku = link_evidence(decisions, rules_by_id, skus_by_id)
    evidence_recs = [evidences_by_sku[k] for k in sorted(evidences_by_sku)]

    verdict_recs: list[dict] = []
    for sku in skus_sorted:
        dec = decisions[sku.sku_id]
        ev_id = evidences_by_sku[sku.sku_id]["evidence_id"] if sku.sku_id in evidences_by_sku else None
        verdict_recs.append(decision_to_record(dec, sku, active_rules, ev_id))

    # Substitute demand & allocation
    stock_map: dict[tuple[str, str], int] = {}
    for d in pack.dc_stock:
        stock_map[(d.dc_id, d.sku_id)] = stock_map.get((d.dc_id, d.sku_id), 0) + d.cases

    demand = demand_from_facings(
        pack.facings,
        decisions,
        pack.substitutes,
        skus_by_id,
        pack.dc_stock,
        stores_by_id,
    )
    allocations = allocate_substitutes(demand, pack.dc_stock, stores_sorted)
    alloc_recs = allocation_records(allocations)
    alloc_by_store_sub: dict[tuple[str, str], Allocation] = {
        (a.store_id, a.sub_sku_id): a for a in allocations
    }

    # Build shelf tasks per store
    all_tasks: list[dict] = []
    tasks_by_store: dict[str, list[dict]] = {}
    floater_ids = {a.associate_id for a in pack.associates if a.is_floater}
    floater_dispatches: list[dict] = []

    for store in stores_sorted:
        sub_for_pulled: dict[str, str] = {}
        for sku_id in pack.substitutes:
            sub_id = substitute_for_sku(sku_id, pack.substitutes, store.dc_id, stock_map)
            if sub_id:
                sub_for_pulled[sku_id] = sub_id
        st_tasks = build_shelf_tasks(
            store,
            pack.facings,
            decisions,
            evidences_by_sku,
            alloc_by_store_sub,
            sub_for_pulled,
            pack.associates,
            deadline_dt,
        )
        tasks_by_store[store.store_id] = st_tasks
        all_tasks.extend(st_tasks)
        for aid in sorted({t["associate_id"] for t in st_tasks if t["associate_id"] in floater_ids}):
            flt_tids = [t["task_id"] for t in st_tasks if t["associate_id"] == aid]
            flt_win = st_tasks[0]["window"]
            floater_dispatches.append(
                {
                    "associate_id": aid,
                    "store_id": store.store_id,
                    "window": flt_win,
                    "task_ids": flt_tids,
                }
            )

    exc_recs = exception_records(pack.notes, tasks_by_store)

    # Identify DSD vendor-pull stores so DSD items are not packed for DC return if excluded
    dsd_stores = {
        n.store_id for n in pack.notes
        if exception_kind_for_text(n.text) == ExceptionKind.DSD_VENDOR_PULL
    }

    # Compute pulled cases per (store_id, sku_id) for return manifests
    import math
    pulled_units: dict[tuple[str, str], int] = {}
    for t in all_tasks:
        if t["action"] == Action.PULL.value:
            key = (t["store_id"], t["sku_id"])
            pulled_units[key] = pulled_units.get(key, 0) + int(t["qty_units"])

    pulled_cases: dict[tuple[str, str], int] = {}
    for (st_id, sk_id), units in sorted(pulled_units.items()):
        if st_id in dsd_stores and "frito" in skus_by_id[sk_id].brand.lower():
            continue
        cu = max(1, skus_by_id[sk_id].case_units)
        pulled_cases[(st_id, sk_id)] = max(1, math.ceil(units / cu))

    manifests: list[RouteManifest] = []
    manifest_recs: list[dict] = []
    if manifest_packer is not None:
        manifests, manifest_recs = manifest_packer(pulled_cases, skus_sorted, pack.trucks, stores_sorted)

    # Build handoffs with pre-deadline windows
    h_start = iso_with_offset(deadline_dt - timedelta(hours=16))
    h_end = iso_with_offset(deadline_dt - timedelta(hours=4))
    handoff_recs = build_handoffs(allocations, manifests, floater_dispatches, [h_start, h_end])

    # Build store playbooks
    playbook_recs: list[dict] = []
    def_win = [iso_with_offset(deadline_dt - timedelta(hours=24)), iso_with_offset(deadline_dt - timedelta(hours=12))]
    for store in stores_sorted:
        st_assocs = [a.associate_id for a in pack.associates if a.store_id == store.store_id]
        if not st_assocs:
            st_assocs = [a.associate_id for a in pack.associates if a.district == store.district][:1]
        playbook_recs.append(
            build_playbook(
                store,
                tasks_by_store.get(store.store_id, []),
                exc_recs,
                manifests,
                deadline_dt,
                def_win,
                st_assocs,
            )
        )

    r_rec = run_record(scenario_id, as_of_dt, rule_ids)
    combined = plan_records(
        r_rec,
        verdict_recs,
        evidence_recs,
        playbook_recs,
        all_tasks,
        exc_recs,
        alloc_recs,
        handoff_recs,
        manifest_recs,
    )
    return enforce_deadline(combined, deadline_dt)


def validate_plan_refs(records: list[dict]) -> list[str]:
    """Validate schema and cross-record ID references across a plan.jsonl record list."""
    issues: list[str] = []
    ev_ids = {r["evidence_id"] for r in records if r.get("type") == "evidence" and "evidence_id" in r}
    alloc_ids = {r["alloc_id"] for r in records if r.get("type") == "allocation" and "alloc_id" in r}
    task_ids = {r["task_id"] for r in records if r.get("type") == "shelf_task" and "task_id" in r}
    exc_ids = {r["exc_id"] for r in records if r.get("type") == "exception" and "exc_id" in r}
    mnf_ids = {r["manifest_id"] for r in records if r.get("type") == "route_manifest" and "manifest_id" in r}

    for r in records:
        issues.extend(validate_record(r))
        rtype = r.get("type")
        if rtype == "sku_verdict" and r.get("verdict") != Verdict.KEEP.value:
            if r.get("evidence_id") not in ev_ids:
                issues.append(f"sku_verdict {r.get('sku_id')} references missing evidence_id {r.get('evidence_id')}")
        elif rtype == "shelf_task":
            if r.get("evidence_id") not in ev_ids:
                issues.append(f"shelf_task {r.get('task_id')} references missing evidence_id {r.get('evidence_id')}")
            if r.get("action") == Action.PLACE_SUB.value and r.get("alloc_id") not in alloc_ids:
                issues.append(f"PLACE_SUB task {r.get('task_id')} references missing alloc_id {r.get('alloc_id')}")
        elif rtype == "exception":
            for tid in r.get("task_ids", []):
                if tid not in task_ids:
                    issues.append(f"exception {r.get('exc_id')} references missing task_id {tid}")
        elif rtype == "store_playbook":
            dl = r.get("deadline")
            for w in r.get("windows", []):
                if dl and not is_before_deadline(w[1], dl):
                    issues.append(f"store_playbook {r.get('store_id')} window {w} not before deadline {dl}")
            for xid in r.get("exception_ids", []):
                if xid not in exc_ids:
                    issues.append(f"store_playbook {r.get('store_id')} references missing exc_id {xid}")
            for mid in r.get("manifest_ids", []):
                if mid not in mnf_ids:
                    issues.append(f"store_playbook {r.get('store_id')} references missing manifest_id {mid}")
    return issues


def plan_to_jsonl(records: list[dict], path: str | Path) -> int:
    """Write plan records to a JSONL file and return count written."""
    return write_jsonl(path, records)


def plan_stats(records: list[dict]) -> dict[str, int]:
    """Count plan records by type."""
    counts: dict[str, int] = {}
    for r in records:
        k = str(r.get("type", "unknown"))
        counts[k] = counts.get(k, 0) + 1
    counts["total"] = len(records)
    return counts


def plan_hash(records: list[dict]) -> str:
    """Compute a deterministic SHA-256 hash over a list of plan records."""
    h = hashlib.sha256()
    for r in records:
        h.update((stable_dumps(r) + "\n").encode("utf-8"))
    return h.hexdigest()[:16]


def merge_plans(p1: list[dict], p2: list[dict]) -> list[dict]:
    """Merge two plan record lists, avoiding duplicate identical records."""
    seen: set[str] = set()
    out: list[dict] = []
    for r in p1 + p2:
        s = stable_dumps(r)
        if s not in seen:
            seen.add(s)
            out.append(r)
    return out
