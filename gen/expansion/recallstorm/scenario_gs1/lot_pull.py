"""Lot-specific shelf pull, verification, quarantine, and evidence records."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import Action, Facing
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.ids import make_evidence_id, make_task_id
from recallstorm.core.jsonl import record_with_src
from recallstorm.gs1.lots import lot_matches_recall, normalize_lot


@dataclass(frozen=True)
class LotPuller:
    """Executes lot-specific shelf pulls and quarantine tracking."""

    target_lots: tuple[str, ...]


def lots_on_shelf(facing: Facing, lot_inventory: dict[tuple[str, str], list[str]] | None = None) -> list[str]:
    """Return lot codes present at a store/SKU facing."""
    if lot_inventory and (facing.store_id, facing.sku_id) in lot_inventory:
        return [normalize_lot(l) for l in lot_inventory[(facing.store_id, facing.sku_id)]]
    return []


def lot_task_window(as_of: datetime | str, deadline: datetime | str) -> list[str]:
    """Compute a valid lot inspection/pull window strictly before deadline."""
    s = datetime.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    dl = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
    end = min(dl - timedelta(hours=2), s + timedelta(hours=4))
    if end <= s:
        end = dl - timedelta(minutes=5)
    return [iso_with_offset(s), iso_with_offset(end)]


def lot_evidence(sku_id: str, lot: str, recall_id: str = "F-0100-2026") -> dict:
    """Create a validated 'evidence' record for a GS1 lot recall match."""
    rule_id = f"OPENFDA_{recall_id}"
    norm = normalize_lot(lot)
    payload = {
        "evidence_id": make_evidence_id(sku_id, rule_id),
        "sku_id": sku_id,
        "rule_id": rule_id,
        "clause_ref": f"openFDA Enforcement {recall_id} (AI 10 Lot {norm})",
        "source_span": [0, len(norm)],
        "rationale": f"Lot code {norm} on {sku_id} matches recall {recall_id}.",
    }
    return record_with_src(payload, "evidence", "recallstorm/scenario_gs1/lot_pull.py")


def lot_verify_task(
    store_id: str,
    facing: Facing,
    target_lots: list[str],
    associate_id: str,
    window: list[str],
    seq: int = 1,
    recall_id: str = "F-0100-2026",
) -> dict:
    """Create a HOLD_VERIFY shelf_task to inspect lot codes on shelf."""
    rule_id = f"OPENFDA_{recall_id}"
    payload = {
        "task_id": make_task_id(store_id, facing.sku_id, Action.HOLD_VERIFY, seq),
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.HOLD_VERIFY.value,
        "loc": {"aisle": facing.loc.aisle, "bay": facing.loc.bay, "shelf": facing.loc.shelf, "pos": facing.loc.pos},
        "qty_units": facing.units,
        "associate_id": associate_id,
        "window": list(window),
        "seq": seq,
        "evidence_id": make_evidence_id(facing.sku_id, rule_id),
        "sub_sku_id": None,
        "alloc_id": None,
    }
    return record_with_src(payload, "shelf_task", "recallstorm/scenario_gs1/lot_pull.py")


def lot_pull_tasks(
    store_id: str,
    facings: list[Facing],
    target_sku_ids: set[str],
    target_lots: list[str],
    associate_id: str,
    window: list[str],
    lot_inventory: dict[tuple[str, str], list[str]] | None = None,
    recall_id: str = "F-0100-2026",
) -> list[dict]:
    """Generate PULL or HOLD_VERIFY tasks for facings matching target_sku_ids and target_lots."""
    rule_id = f"OPENFDA_{recall_id}"
    out: list[dict] = []
    seq = 0
    for f in facings:
        if f.store_id != store_id or f.sku_id not in target_sku_ids:
            continue
        seq += 1
        shelf_lots = lots_on_shelf(f, lot_inventory)
        if shelf_lots and not any(lot_matches_recall(l, target_lots) for l in shelf_lots):
            continue
        payload = {
            "task_id": make_task_id(store_id, f.sku_id, Action.PULL, seq),
            "store_id": store_id,
            "sku_id": f.sku_id,
            "action": Action.PULL.value,
            "loc": {"aisle": f.loc.aisle, "bay": f.loc.bay, "shelf": f.loc.shelf, "pos": f.loc.pos},
            "qty_units": f.units,
            "associate_id": associate_id,
            "window": list(window),
            "seq": seq,
            "evidence_id": make_evidence_id(f.sku_id, rule_id),
            "sub_sku_id": None,
            "alloc_id": None,
        }
        out.append(record_with_src(payload, "shelf_task", "recallstorm/scenario_gs1/lot_pull.py"))
    return out


def lot_quarantine(store_id: str, sku_id: str, lot: str, units: int) -> dict:
    """Create a backroom quarantine record for pulled lot units."""
    if units <= 0:
        raise ValueError("units must be positive")
    return {"store_id": store_id, "sku_id": sku_id, "lot": normalize_lot(lot), "units": units}


def lot_pull_counts(tasks: list[dict]) -> dict[str, int]:
    """Count total lot tasks and pulled units."""
    return {
        "task_count": len(tasks),
        "total_units": sum(int(t.get("qty_units", 0)) for t in tasks),
    }


def lot_report(tasks: list[dict]) -> dict:
    """Summarize lot pull tasks across stores."""
    stores = sorted({str(t["store_id"]) for t in tasks if "store_id" in t})
    return {**lot_pull_counts(tasks), "stores": stores}
