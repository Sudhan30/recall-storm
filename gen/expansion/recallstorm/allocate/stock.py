"""Distribution Center (DC) stock ledger and strict stock conservation checks."""
from __future__ import annotations

from dataclasses import dataclass, field
from contract import Allocation, DcStock
from recallstorm.core.errors import AllocationError


@dataclass
class StockLedger:
    """Mutable DC stock ledger mapping (dc_id, sku_id) -> available integer cases."""

    initial: dict[tuple[str, str], int] = field(default_factory=dict)
    available: dict[tuple[str, str], int] = field(default_factory=dict)


def stock_ledger(stock: list[DcStock]) -> StockLedger:
    """Build a StockLedger from a list of DcStock records."""
    init: dict[tuple[str, str], int] = {}
    for d in stock:
        if d.cases < 0:
            raise AllocationError(f"Negative initial DC stock for {d.dc_id}/{d.sku_id}")
        key = (d.dc_id, d.sku_id)
        init[key] = init.get(key, 0) + int(d.cases)
    return StockLedger(initial=dict(init), available=dict(init))


def stock_for_dc(stock: list[DcStock], dc_id: str) -> dict[str, int]:
    """Return sku_id -> cases for a specific DC."""
    out: dict[str, int] = {}
    for d in stock:
        if d.dc_id == dc_id:
            out[d.sku_id] = out.get(d.sku_id, 0) + d.cases
    return out


def stock_for_sku(stock: list[DcStock], dc_id: str, sku_id: str) -> int:
    """Return available cases for (dc_id, sku_id)."""
    return sum(d.cases for d in stock if d.dc_id == dc_id and d.sku_id == sku_id)


def reserve_stock(ledger: StockLedger, dc_id: str, sku_id: str, cases: int) -> int:
    """Deduct `cases` from ledger for (dc_id, sku_id) and return remaining balance."""
    if cases < 0:
        raise AllocationError("Cannot reserve negative cases")
    key = (dc_id, sku_id)
    avail = ledger.available.get(key, 0)
    if cases > avail:
        raise AllocationError(f"Insufficient stock at {dc_id}/{sku_id}: wanted {cases}, have {avail}")
    ledger.available[key] = avail - cases
    return ledger.available[key]


def release_stock(ledger: StockLedger, dc_id: str, sku_id: str, cases: int) -> int:
    """Return `cases` back to ledger for (dc_id, sku_id), capped at initial stock."""
    if cases < 0:
        raise AllocationError("Cannot release negative cases")
    key = (dc_id, sku_id)
    init = ledger.initial.get(key, 0)
    ledger.available[key] = min(init, ledger.available.get(key, 0) + cases)
    return ledger.available[key]


def stock_after(stock: list[DcStock], allocations: list[Allocation]) -> dict[tuple[str, str], int]:
    """Compute remaining (dc_id, sku_id) stock after applying allocations."""
    ledger = stock_ledger(stock)
    for a in allocations:
        reserve_stock(ledger, a.dc_id, a.sub_sku_id, a.qty_cases)
    return dict(ledger.available)


def ledger_to_records(ledger: StockLedger) -> list[dict]:
    """Export ledger balances as a list of dicts."""
    return [
        {"dc_id": dc, "sku_id": sk, "initial": ledger.initial[(dc, sk)], "available": avail}
        for (dc, sk), avail in sorted(ledger.available.items())
    ]


def conservation_check(stock: list[DcStock], allocations: list[Allocation]) -> bool:
    """Verify that allocations never exceed initial DC stock and dc_balance_after is exact."""
    ledger = stock_ledger(stock)
    for a in allocations:
        if a.qty_cases <= 0:
            return False
        key = (a.dc_id, a.sub_sku_id)
        avail = ledger.available.get(key, 0)
        if a.qty_cases > avail:
            return False
        new_bal = avail - a.qty_cases
        if a.dc_balance_after != new_bal:
            return False
        ledger.available[key] = new_bal
    return True
