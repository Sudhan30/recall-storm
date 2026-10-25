"""Human-readable explanations for tasks, stores, SKUs, allocations, and routes."""
from __future__ import annotations

from dataclasses import dataclass

from contract import Allocation, RouteManifest, SkuDecision


@dataclass
class Explainer:
    """Narrative generator for Recall Storm execution plans."""

    records: list[dict]

    def summary_text(self) -> str:
        return plan_narrative(self.records)


def explain_task(task: dict) -> str:
    """Explain a shelf_task record."""
    return (
        f"Task {task.get('task_id')}: {task.get('action')} {task.get('qty_units')} units of "
        f"{task.get('sku_id')} at store {task.get('store_id')} by {task.get('associate_id')} "
        f"during {task.get('window')}."
    )


def explain_store(playbook: dict) -> str:
    """Explain a store_playbook record."""
    return (
        f"Store {playbook.get('store_id')} ({playbook.get('format')}): "
        f"counts={playbook.get('counts')} before deadline {playbook.get('deadline')}."
    )


def explain_sku(verdict_rec: dict, ev_rec: dict | None = None) -> str:
    """Explain a sku_verdict record and optional evidence record."""
    base = f"SKU {verdict_rec.get('sku_id')} -> {verdict_rec.get('verdict')} (rules={verdict_rec.get('rule_ids')})"
    if ev_rec:
        base += f" | Evidence {ev_rec.get('evidence_id')}: {ev_rec.get('rationale')}"
    return base


def explain_allocation(alloc: Allocation | dict) -> str:
    """Explain a substitute Allocation."""
    if isinstance(alloc, Allocation):
        return f"Allocation {alloc.alloc_id}: {alloc.qty_cases} cases of {alloc.sub_sku_id} from {alloc.dc_id} to {alloc.store_id} (bal={alloc.dc_balance_after})"
    return f"Allocation {alloc.get('alloc_id')}: {alloc.get('qty_cases')} cases of {alloc.get('sub_sku_id')} from {alloc.get('dc_id')} to {alloc.get('store_id')}"


def explain_route(manifest: RouteManifest | dict) -> str:
    """Explain a RouteManifest."""
    if isinstance(manifest, RouteManifest):
        return f"Manifest {manifest.manifest_id}: truck {manifest.truck_id} from {manifest.dc_id} with {len(manifest.stops)} stops"
    return f"Manifest {manifest.get('manifest_id')}: truck {manifest.get('truck_id')} from {manifest.get('dc_id')} with {len(manifest.get('stops', []))} stops"


def why_hold(dec: SkuDecision) -> str:
    """Explain why a SKU received a HOLD_VERIFY verdict."""
    return f"SKU {dec.sku_id} held for verification: {dec.rationale}"


def why_keep(dec: SkuDecision) -> str:
    """Explain why a SKU received a KEEP verdict."""
    return f"SKU {dec.sku_id} kept on shelf: {dec.rationale}"


def plan_narrative(records: list[dict]) -> str:
    """Generate a concise multi-line narrative summarizing plan.jsonl records."""
    by_type: dict[str, int] = {}
    for r in records:
        t = str(r.get("type", "unknown"))
        by_type[t] = by_type.get(t, 0) + 1
    parts = [f"{k}={v}" for k, v in sorted(by_type.items())]
    return "Plan Summary: " + ", ".join(parts)
