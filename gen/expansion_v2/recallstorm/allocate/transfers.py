"""Build DC-to-store substitute transfer handoffs and shipments."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from contract import Allocation, HandoffKind, Sku, Truck
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.ids import make_handoff_id


@dataclass
class TransferPlan:
    """Collection of substitute transfer handoff records."""

    handoffs: list[dict] = field(default_factory=list)


def dc_to_store_windows(as_of: datetime, deadline: datetime) -> tuple[str, str]:
    """Return a [start_iso, end_iso] transfer window strictly before deadline."""
    start = as_of + timedelta(hours=1)
    end = min(deadline - timedelta(hours=2), start + timedelta(hours=4))
    if end <= start:
        start = deadline - timedelta(hours=2)
        end = deadline - timedelta(minutes=30)
    return (iso_with_offset(start), iso_with_offset(end))


def transfer_handoff(alloc: Allocation, window: tuple[str, str]) -> dict:
    """Build a plan.jsonl 'handoff' record of kind SUB_TRANSFER for an Allocation."""
    return {
        "type": "handoff",
        "handoff_id": make_handoff_id(HandoffKind.SUB_TRANSFER.value, alloc.dc_id, alloc.store_id, 0),
        "kind": HandoffKind.SUB_TRANSFER.value,
        "from_id": alloc.dc_id,
        "to_id": alloc.store_id,
        "window": [window[0], window[1]],
        "qty": alloc.qty_cases,
        "ref_ids": [alloc.alloc_id],
        "src": "recallstorm/allocate/transfers.py",
    }


def sub_transfers(allocations: list[Allocation], window: tuple[str, str]) -> list[dict]:
    """Build SUB_TRANSFER handoff records for a list of Allocations."""
    out: list[dict] = []
    for idx, a in enumerate(allocations):
        rec = transfer_handoff(a, window)
        rec["handoff_id"] = make_handoff_id(HandoffKind.SUB_TRANSFER.value, a.dc_id, a.store_id, idx)
        out.append(rec)
    return out


def transfer_cube(allocations: list[Allocation], skus: dict[str, Sku]) -> float:
    """Compute total cubic feet across substitute allocations."""
    total = 0.0
    for a in allocations:
        sku = skus.get(a.sub_sku_id)
        unit_cube = sku.case_cube_ft3 if sku else 1.5
        total += a.qty_cases * unit_cube
    return round(total, 2)


def transfer_weight(allocations: list[Allocation], skus: dict[str, Sku]) -> float:
    """Compute total weight in pounds across substitute allocations."""
    total = 0.0
    for a in allocations:
        sku = skus.get(a.sub_sku_id)
        unit_wt = sku.case_weight_lb if sku else 10.0
        total += a.qty_cases * unit_wt
    return round(total, 2)


def transfers_by_truck(allocations: list[Allocation], trucks: list[Truck]) -> dict[str, list[Allocation]]:
    """Assign allocations to the first available truck at each DC."""
    dc_trucks: dict[str, str] = {}
    for t in sorted(trucks, key=lambda x: x.truck_id):
        dc_trucks.setdefault(t.dc_id, t.truck_id)
    out: dict[str, list[Allocation]] = {}
    for a in allocations:
        tid = dc_trucks.get(a.dc_id, f"{a.dc_id}-T0")
        out.setdefault(tid, []).append(a)
    return out


def validate_transfers(transfers: list[dict]) -> list[str]:
    """Validate SUB_TRANSFER handoff records."""
    issues: list[str] = []
    for t in transfers:
        if t.get("kind") != HandoffKind.SUB_TRANSFER.value:
            issues.append(f"Invalid transfer kind: {t.get('kind')}")
        if int(t.get("qty", 0)) <= 0:
            issues.append(f"Non-positive transfer qty on {t.get('handoff_id')}")
    return issues


def transfer_summary(allocations: list[Allocation]) -> dict:
    """Summarize substitute transfers."""
    return {
        "transfer_count": len(allocations),
        "total_cases": sum(a.qty_cases for a in allocations),
    }
