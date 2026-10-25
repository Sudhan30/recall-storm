"""Assemble complete, referentially valid plan.jsonl records."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

from contract import Classifier, DataPack, Verdict
from recallstorm.adjudicate.evidence import build_evidence
from recallstorm.allocate.allocator import allocate_substitutes, allocation_records
from recallstorm.allocate.demand import demand_from_facings
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.ids import make_run_id
from recallstorm.core.jsonl import validate_record, write_jsonl
from recallstorm.plan.deadline import enforce_deadline
from recallstorm.plan.exceptions_plan import exception_records
from recallstorm.plan.handoffs import build_handoffs
from recallstorm.plan.playbook import build_playbook
from recallstorm.plan.tasks import build_shelf_tasks
from recallstorm.rules.engine import decision_to_record, evaluate_sku


@dataclass
class PlanAssembler:
    """Top-level assembler for plan.jsonl."""

    pack: DataPack
    scenario: dict


def run_record(scenario_id: str, as_of: str, rule_ids: list[str]) -> dict:
    """Create the initial 'run' record for plan.jsonl."""
    return {
        "type": "run",
        "run_id": make_run_id(scenario_id, as_of),
        "scenario_id": scenario_id,
        "generator": "recallstorm-1.0.0",
        "as_of": as_of,
        "rule_ids": list(rule_ids),
        "src": "recallstorm/plan/assemble.py",
    }


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
    """Concatenate all nine PLAN_TYPES record lists in canonical order."""
    return (
        [run_rec]
        + evidences
        + verdicts
        + allocations
        + manifests
        + tasks
        + exceptions
        + handoffs
        + playbooks
    )


def assemble_plan(
    pack: DataPack,
    scenario: dict,
    manifests: list[dict] | None = None,
    classifier: Classifier | None = None,
) -> list[dict]:
    """Evaluate rules, allocate substitutes, build tasks/exceptions/playbooks/handoffs, and return all plan.jsonl records."""
    scenario_id = str(scenario.get("scenario_id", "ca_red3"))
    state = str(scenario.get("state", "CA"))
    rule_ids_filter = set(scenario.get("rule_ids") or [r.rule_id for r in pack.rules])
    active_rules = [r for r in pack.rules if r.rule_id in rule_ids_filter] or list(pack.rules)
    rule_map = {r.rule_id: r for r in active_rules}

    as_of_str = str(scenario.get("as_of") or iso_with_offset(pack.as_of))
    deadline_str = str(scenario.get("deadline", "2027-01-01T00:00:00-08:00"))
    deadline_dt = datetime.fromisoformat(deadline_str)

    # Evaluate at the compliance deadline so rules taking effect at deadline (e.g. 2027-01-01T00:00) trigger pre-deadline pulls
    eval_dt = deadline_dt

    sku_map = {s.sku_id: s for s in pack.skus}
    decisions = {}
    verdict_recs: list[dict] = []
    evidence_recs: list[dict] = []
    evidence_by_sku: dict[str, str] = {}

    for sku in sorted(pack.skus, key=lambda x: x.sku_id):
        dec = evaluate_sku(sku, active_rules, state, eval_dt, classifier=classifier)
        decisions[sku.sku_id] = dec
        ev_id = None
        if dec.verdict in {Verdict.PULL, Verdict.HOLD_VERIFY} and dec.rule_ids:
            primary_rule = rule_map.get(dec.rule_ids[0], active_rules[0])
            ev = build_evidence(sku, dec, primary_rule)
            evidence_recs.append(ev)
            ev_id = ev["evidence_id"]
            evidence_by_sku[sku.sku_id] = ev_id
        verdict_recs.append(decision_to_record(sku, dec, active_rules, evidence_id=ev_id))

    # Substitute demand & allocation
    demand = demand_from_facings(pack.facings, decisions, pack.substitutes, sku_map, pack.dc_stock)
    allocs = allocate_substitutes(demand, pack.dc_stock, pack.stores)
    alloc_recs = allocation_records(allocs)

    # Shelf tasks per store
    all_tasks: list[dict] = []
    tasks_by_store: dict[str, list[dict]] = {}
    for st in sorted(pack.stores, key=lambda x: x.store_id):
        st_tasks = build_shelf_tasks(
            st,
            pack.facings,
            decisions,
            evidence_by_sku,
            allocs,
            sku_map,
            pack.associates,
            deadline_dt,
        )
        tasks_by_store[st.store_id] = st_tasks
        all_tasks.extend(st_tasks)

    exc_recs = exception_records(pack.notes, tasks_by_store)
    mnf_recs = list(manifests or [])

    win_s = deadline_dt - timedelta(hours=5)
    win_e = deadline_dt - timedelta(hours=2)
    hnd_win = [iso_with_offset(win_s), iso_with_offset(win_e)]
    hnd_recs = build_handoffs(allocs, mnf_recs, [], hnd_win)

    playbooks: list[dict] = []
    for st in sorted(pack.stores, key=lambda x: x.store_id):
        playbooks.append(build_playbook(st, all_tasks, exc_recs, mnf_recs, deadline_dt))

    run_rec = run_record(scenario_id, as_of_str, [r.rule_id for r in active_rules])
    combined = plan_records(
        run_rec,
        verdict_recs,
        evidence_recs,
        playbooks,
        all_tasks,
        exc_recs,
        alloc_recs,
        hnd_recs,
        mnf_recs,
    )
    return enforce_deadline(combined, deadline_dt)


def validate_plan_refs(records: list[dict]) -> list[str]:
    """Validate schema and cross-record ID references across all records in plan.jsonl."""
    issues: list[str] = []
    ev_ids = {r["evidence_id"] for r in records if r.get("type") == "evidence" and "evidence_id" in r}
    alloc_ids = {r["alloc_id"] for r in records if r.get("type") == "allocation" and "alloc_id" in r}
    task_ids = {r["task_id"] for r in records if r.get("type") == "shelf_task" and "task_id" in r}
    exc_ids = {r["exc_id"] for r in records if r.get("type") == "exception" and "exc_id" in r}
    mnf_ids = {r["manifest_id"] for r in records if r.get("type") == "route_manifest" and "manifest_id" in r}

    for r in records:
        issues.extend(validate_record(r))
        rtype = r.get("type")
        if rtype == "sku_verdict" and r.get("evidence_id"):
            if r["evidence_id"] not in ev_ids:
                issues.append(f"sku_verdict {r.get('sku_id')} references missing evidence_id {r['evidence_id']}")
        elif rtype == "shelf_task":
            if r.get("evidence_id") and r["evidence_id"] not in ev_ids:
                issues.append(f"shelf_task {r.get('task_id')} references missing evidence_id {r['evidence_id']}")
            if r.get("alloc_id") and r["alloc_id"] not in alloc_ids:
                issues.append(f"shelf_task {r.get('task_id')} references missing alloc_id {r['alloc_id']}")
        elif rtype == "exception":
            for tid in r.get("task_ids", []):
                if tid not in task_ids:
                    issues.append(f"exception {r.get('exc_id')} references missing task_id {tid}")
        elif rtype == "store_playbook":
            for eid in r.get("exception_ids", []):
                if eid not in exc_ids:
                    issues.append(f"store_playbook {r.get('store_id')} references missing exc_id {eid}")
            for mid in r.get("manifest_ids", []):
                if mid not in mnf_ids:
                    issues.append(f"store_playbook {r.get('store_id')} references missing manifest_id {mid}")
    return issues


def plan_to_jsonl(records: list[dict], out_path: str) -> int:
    """Write plan records to out_path as JSONL."""
    return write_jsonl(out_path, records)


def plan_stats(records: list[dict]) -> dict[str, int]:
    """Return record counts by PLAN_TYPES key."""
    counts: dict[str, int] = {}
    for r in records:
        t = str(r.get("type", "unknown"))
        counts[t] = counts.get(t, 0) + 1
    return counts


def plan_hash(records: list[dict]) -> str:
    """Compute a deterministic SHA-256 digest of plan records."""
    raw = json.dumps(records, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def merge_plans(p1: list[dict], p2: list[dict]) -> list[dict]:
    """Merge two plan record lists preserving unique records."""
    seen: set[str] = set()
    out: list[dict] = []
    for r in p1 + p2:
        s = json.dumps(r, sort_keys=True)
        if s not in seen:
            seen.add(s)
            out.append(r)
    return out
