"""DC-to-store substitute transfer handoff builder and volume/weight metrics."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import Allocation, HandoffKind, Sku, Truck
from recallstorm.core.ids import make_handoff_id
from recallstorm.core.jsonl import record_with_src


@dataclass(frozen=True)
class TransferPlan:
    """Substitute transfer handoffs and totals."""

    handoffs: tuple[dict, ...]
    total_cases: int


def dc_to_store_windows(as_of: datetime | str, deadline: datetime | str) -> tuple[str, str]:
    """Compute a valid DC-to-store transfer window strictly before deadline."""
    s = datetime.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    dl = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
    w_start = s + timedelta(hours=2)
    w_end = min(dl - timedelta(hours=2), w_start + timedelta(hours=4))
    if w_end <= w_start:
        w_start = s
        w_end = dl - timedelta(minutes=5)
    return w_start.isoformat(timespec="seconds"), w_end.isoformat(timespec="seconds")


def transfer_handoff(alloc: Allocation, window: tuple[str, str] | list[str], seq: int = 0) -> dict:
    """Create a validated 'handoff' record of kind SUB_TRANSFER for an Allocation."""
    if not isinstance(alloc, Allocation):
        raise TypeError("alloc must be an Allocation")
    hid = make_handoff_id(HandoffKind.SUB_TRANSFER, alloc.dc_id, alloc.store_id, seq)
    payload = {
        "handoff_id": hid,
        "kind": HandoffKind.SUB_TRANSFER.value,
        "from_id": alloc.dc_id,
        "to_id": alloc.store_id,
        "window": [str(window[0]), str(window[1])],
        "qty": alloc.qty_cases,
        "ref_ids": [alloc.alloc_id],
    }
    return record_with_src(payload, "handoff", "recallstorm/allocate/transfers.py")


def sub_transfers(allocations: list[Allocation], window: tuple[str, str] | list[str]) -> list[dict]:
    """Build SUB_TRANSFER handoff records for a list of Allocations."""
    return [transfer_handoff(a, window, idx) for idx, a in enumerate(allocations)]


def transfer_cube(allocations: list[Allocation], skus_by_id: dict[str, Sku]) -> float:
    """Compute total cubic feet of allocated substitute cases."""
    total = 0.0
    for a in allocations:
        sku = skus_by_id.get(a.sub_sku_id)
        cube = sku.case_cube_ft3 if sku else 1.5
        total += a.qty_cases * cube
    return round(total, 2)


def transfer_weight(allocations: list[Allocation], skus_by_id: dict[str, Sku]) -> float:
    """Compute total weight in pounds of allocated substitute cases."""
    total = 0.0
    for a in allocations:
        sku = skus_by_id.get(a.sub_sku_id)
        wt = sku.case_weight_lb if sku else 10.0
        total += a.qty_cases * wt
    return round(total, 2)


def transfers_by_truck(allocations: list[Allocation], trucks: list[Truck]) -> dict[str, list[Allocation]]:
    """Map each DC's primary truck_id to the allocations originating from that DC."""
    first_truck_by_dc: dict[str, str] = {}
    for t in sorted(trucks, key=lambda x: x.truck_id):
        first_truck_by_dc.setdefault(t.dc_id, t.truck_id)
    out: dict[str, list[Allocation]] = {}
    for a in allocations:
        tid = first_truck_by_dc.get(a.dc_id, f"{a.dc_id}-T0")
        out.setdefault(tid, []).append(a)
    return out


def validate_transfers(handoffs: list[dict], allocations: list[Allocation]) -> list[str]:
    """Validate that every SUB_TRANSFER handoff references a valid alloc_id."""
    valid_ids = {a.alloc_id for a in allocations}
    issues: list[str] = []
    for h in handoffs:
        if h.get("kind") == HandoffKind.SUB_TRANSFER.value:
            for ref in h.get("ref_ids", []):
                if ref not in valid_ids:
                    issues.append(f"Handoff {h.get('handoff_id')} references unknown alloc_id {ref}")
    return issues


def transfer_summary(allocations: list[Allocation]) -> dict:
    """Summarize total substitute transfer allocations."""
    return {
        "allocation_count": len(allocations),
        "total_cases": sum(a.qty_cases for a in allocations),
        "stores_served": len({a.store_id for a in allocations}),
    }
