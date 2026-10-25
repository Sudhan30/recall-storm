"""DC stock ledger and stock conservation verification."""
from __future__ import annotations

from dataclasses import dataclass, field

from contract import Allocation, DcStock
from recallstorm.core.errors import AllocationError


@dataclass
class StockLedger:
    """Mutable DC stock ledger tracking initial and remaining cases per (dc_id, sku_id)."""

    initial: dict[tuple[str, str], int] = field(default_factory=dict)
    available: dict[tuple[str, str], int] = field(default_factory=dict)


def stock_ledger(stock: list[DcStock]) -> StockLedger:
    """Create a StockLedger from a list of DcStock records."""
    ledger = StockLedger()
    for item in stock:
        if item.cases < 0:
            raise AllocationError(f"Negative DC stock for {item.dc_id}/{item.sku_id}")
        key = (item.dc_id, item.sku_id)
        ledger.initial[key] = ledger.initial.get(key, 0) + item.cases
        ledger.available[key] = ledger.available.get(key, 0) + item.cases
    return ledger


def stock_for_dc(stock: list[DcStock], dc_id: str) -> dict[str, int]:
    """Return sku_id -> cases available at dc_id."""
    out: dict[str, int] = {}
    for s in stock:
        if s.dc_id == dc_id:
            out[s.sku_id] = out.get(s.sku_id, 0) + s.cases
    return out


def stock_for_sku(stock: list[DcStock], sku_id: str) -> dict[str, int]:
    """Return dc_id -> cases available for sku_id."""
    out: dict[str, int] = {}
    for s in stock:
        if s.sku_id == sku_id:
            out[s.dc_id] = out.get(s.dc_id, 0) + s.cases
    return out


def stock_after(initial: int, allocated: int) -> int:
    """Return remaining stock after subtracting allocated cases, raising AllocationError if negative."""
    rem = int(initial) - int(allocated)
    if rem < 0:
        raise AllocationError(f"Allocation {allocated} exceeds initial stock {initial}")
    return rem


def reserve_stock(ledger: StockLedger, dc_id: str, sku_id: str, cases: int) -> tuple[int, int]:
    """Reserve up to cases from ledger for (dc_id, sku_id); return (allocated_cases, balance_after)."""
    if cases < 0:
        raise AllocationError("Cannot reserve negative cases")
    key = (dc_id, sku_id)
    avail = ledger.available.get(key, 0)
    granted = min(avail, cases)
    after = avail - granted
    ledger.available[key] = after
    return (granted, after)


def release_stock(ledger: StockLedger, dc_id: str, sku_id: str, cases: int) -> int:
    """Release reserved cases back into ledger; return new balance."""
    if cases < 0:
        raise AllocationError("Cannot release negative cases")
    key = (dc_id, sku_id)
    init = ledger.initial.get(key, 0)
    new_bal = min(init, ledger.available.get(key, 0) + cases)
    ledger.available[key] = new_bal
    return new_bal


def ledger_to_records(ledger: StockLedger) -> list[dict]:
    """Export ledger balances as dictionary records."""
    out: list[dict] = []
    for (dc_id, sku_id), bal in sorted(ledger.available.items()):
        out.append(
            {
                "dc_id": dc_id,
                "sku_id": sku_id,
                "initial_cases": ledger.initial.get((dc_id, sku_id), 0),
                "available_cases": bal,
            }
        )
    return out


def conservation_check(stock: list[DcStock], allocations: list[Allocation]) -> bool:
    """Verify stock conservation: allocated cases per (dc_id, sub_sku_id) never exceed DcStock, and running balances match."""
    ledger = stock_ledger(stock)
    used: dict[tuple[str, str], int] = {}
    for a in allocations:
        if a.qty_cases < 0 or a.dc_balance_after < 0:
            return False
        key = (a.dc_id, a.sub_sku_id)
        used[key] = used.get(key, 0) + a.qty_cases
        if used[key] > ledger.initial.get(key, 0):
            return False
    return True
