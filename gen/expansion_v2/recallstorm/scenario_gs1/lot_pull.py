"""Generate lot-specific shelf pull and verification tasks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from contract import Action, Facing, Store
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.ids import make_evidence_id, make_task_id
from recallstorm.gs1.lots import recall_lot_filter


@dataclass
class LotPuller:
    """Lot-specific shelf pull planner."""

    target_lots: list[str]


def lots_on_shelf(sku_id: str, shelf_lots: dict[str, list[str]]) -> list[str]:
    """Return lot codes present on shelf for sku_id."""
    return list(shelf_lots.get(sku_id, []))


def lot_task_window(as_of: datetime, deadline: datetime) -> list[str]:
    """Return a task execution window strictly before deadline."""
    s = as_of + timedelta(hours=1)
    e = min(deadline - timedelta(hours=1), s + timedelta(minutes=30))
    if e <= s:
        s = deadline - timedelta(hours=2)
        e = deadline - timedelta(minutes=30)
    return [iso_with_offset(s), iso_with_offset(e)]


def lot_evidence(sku_id: str, lot: str, recall_id: str) -> dict:
    """Build an evidence record for a recalled lot code."""
    return {
        "type": "evidence",
        "evidence_id": make_evidence_id(sku_id, recall_id),
        "sku_id": sku_id,
        "rule_id": recall_id,
        "clause_ref": f"GS1 AI(10) Lot {lot}",
        "source_span": {"start": 0, "end": len(lot), "text": lot},
        "rationale": f"Lot {lot} matches recall {recall_id}.",
        "src": "recallstorm/scenario_gs1/lot_pull.py",
    }


def lot_verify_task(
    store_id: str, facing: Facing, associate_id: str, window: list[str], seq: int = 0
) -> dict:
    """Build a HOLD_VERIFY shelf_task to inspect lot codes at facing."""
    return {
        "type": "shelf_task",
        "task_id": make_task_id(store_id, facing.sku_id, Action.HOLD_VERIFY.value, seq),
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.HOLD_VERIFY.value,
        "loc": {"aisle": facing.loc.aisle, "bay": facing.loc.bay, "shelf": facing.loc.shelf, "pos": facing.loc.pos},
        "qty_units": facing.units,
        "associate_id": associate_id,
        "window": list(window),
        "seq": seq,
        "evidence_id": make_evidence_id(facing.sku_id, "LOT_CHECK"),
        "sub_sku_id": None,
        "alloc_id": None,
        "src": "recallstorm/scenario_gs1/lot_pull.py",
    }


def lot_pull_tasks(
    store: Store,
    facings: list[Facing],
    target_lots: list[str],
    shelf_lots: dict[str, list[str]],
    associate_id: str,
    window: list[str],
) -> list[dict]:
    """Generate PULL tasks when shelf lots match target_lots, or HOLD_VERIFY when shelf lots are unknown."""
    tasks: list[dict] = []
    seq = 1
    for f in facings:
        if f.store_id != store.store_id:
            continue
        present = lots_on_shelf(f.sku_id, shelf_lots)
        if not present:
            tasks.append(lot_verify_task(store.store_id, f, associate_id, window, seq))
            seq += 1
            continue
        matched = recall_lot_filter(present, target_lots)
        if matched:
            tasks.append(
                {
                    "type": "shelf_task",
                    "task_id": make_task_id(store.store_id, f.sku_id, Action.PULL.value, seq),
                    "store_id": store.store_id,
                    "sku_id": f.sku_id,
                    "action": Action.PULL.value,
                    "loc": {"aisle": f.loc.aisle, "bay": f.loc.bay, "shelf": f.loc.shelf, "pos": f.loc.pos},
                    "qty_units": f.units,
                    "associate_id": associate_id,
                    "window": list(window),
                    "seq": seq,
                    "evidence_id": make_evidence_id(f.sku_id, matched[0]),
                    "sub_sku_id": None,
                    "alloc_id": None,
                    "src": "recallstorm/scenario_gs1/lot_pull.py",
                }
            )
            seq += 1
    return tasks


def lot_quarantine(store_id: str, sku_id: str, lot: str, units: int) -> dict:
    """Build a backroom quarantine record for pulled lot units."""
    return {"store_id": store_id, "sku_id": sku_id, "lot": lot, "units": units, "status": "QUARANTINED"}


def lot_pull_counts(tasks: list[dict]) -> dict[str, int]:
    """Count PULL vs HOLD_VERIFY lot tasks."""
    return {
        "PULL": sum(1 for t in tasks if t.get("action") == "PULL"),
        "HOLD_VERIFY": sum(1 for t in tasks if t.get("action") == "HOLD_VERIFY"),
    }


def lot_report(tasks: list[dict]) -> dict:
    """Summarize lot pull tasks."""
    return {"total_tasks": len(tasks), "counts": lot_pull_counts(tasks)}
