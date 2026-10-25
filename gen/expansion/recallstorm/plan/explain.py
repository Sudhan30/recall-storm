"""Human-readable explanations for tasks, playbooks, verdicts, allocations, and routes."""
from __future__ import annotations

from dataclasses import dataclass
from contract import SkuDecision


@dataclass(frozen=True)
class Explainer:
    """Builds narrative summaries for plan records."""

    scenario_id: str = "ca_red3"


def why_hold(decision: SkuDecision) -> str:
    """Explain why a SKU received HOLD_VERIFY."""
    return f"SKU {decision.sku_id} placed on HOLD_VERIFY: {decision.rationale}"


def why_keep(decision: SkuDecision) -> str:
    """Explain why a SKU received KEEP."""
    return f"SKU {decision.sku_id} cleared as KEEP: {decision.rationale}"


def explain_sku(verdict_rec: dict, evidence_rec: dict | None = None) -> str:
    """Explain a sku_verdict record and its optional evidence record."""
    sku_id = verdict_rec.get("sku_id", "UNKNOWN")
    verdict = verdict_rec.get("verdict", "KEEP")
    if evidence_rec:
        return (
            f"SKU {sku_id} -> {verdict} under {evidence_rec.get('rule_id')} "
            f"({evidence_rec.get('clause_ref')}): {evidence_rec.get('rationale')}"
        )
    return f"SKU {sku_id} -> {verdict} (decided by {verdict_rec.get('decided_by', 'RULE')})"


def explain_task(task: dict) -> str:
    """Explain a shelf_task record."""
    loc = task.get("loc", {})
    loc_str = f"{loc.get('aisle')}-B{loc.get('bay')}-S{loc.get('shelf')}-P{loc.get('pos')}"
    return (
        f"Task {task.get('task_id')}: {task.get('action')} {task.get('qty_units')} units "
        f"of {task.get('sku_id')} at {task.get('store_id')} ({loc_str}) by {task.get('associate_id')}"
    )


def explain_store(playbook: dict) -> str:
    """Explain a store_playbook record."""
    return (
        f"Store {playbook.get('store_id')} ({playbook.get('format')}): "
        f"deadline {playbook.get('deadline')}, counts={playbook.get('counts')}"
    )


def explain_allocation(alloc_rec: dict) -> str:
    """Explain an allocation record."""
    return (
        f"Allocation {alloc_rec.get('alloc_id')}: {alloc_rec.get('dc_id')} -> "
        f"{alloc_rec.get('store_id')} ({alloc_rec.get('qty_cases')} cases of {alloc_rec.get('sub_sku_id')}, "
        f"balance after={alloc_rec.get('dc_balance_after')})"
    )


def explain_route(manifest_rec: dict) -> str:
    """Explain a route_manifest record."""
    stops = manifest_rec.get("stops", [])
    return (
        f"Manifest {manifest_rec.get('manifest_id')} on truck {manifest_rec.get('truck_id')} "
        f"from {manifest_rec.get('dc_id')}: {len(stops)} stops departing {manifest_rec.get('depart')}"
    )


def plan_narrative(records: list[dict]) -> str:
    """Generate a multi-line executive narrative of an entire plan.jsonl record list."""
    by_type: dict[str, int] = {}
    for r in records:
        t = str(r.get("type", "unknown"))
        by_type[t] = by_type.get(t, 0) + 1
    lines = ["Recall Storm Execution Plan Summary:"]
    for k in sorted(by_type):
        lines.append(f"- {k}: {by_type[k]}")
    return "\n".join(lines)
