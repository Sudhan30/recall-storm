"""Unit tests for recallstorm.allocate.stock."""
from contract import Allocation, DcStock
from recallstorm.allocate.stock import (
    StockLedger,
    conservation_check,
    ledger_to_records,
    release_stock,
    reserve_stock,
    stock_after,
    stock_for_dc,
    stock_for_sku,
    stock_ledger,
)


def test_allocate_stock():
    st = [DcStock("DC_NORTH", "SUB1", 10), DcStock("DC_SOUTH", "SUB1", 6)]
    ledger = stock_ledger(st)
    assert isinstance(ledger, StockLedger)
    assert stock_for_dc(st, "DC_NORTH") == {"SUB1": 10}
    assert stock_for_sku(st, "SUB1")["DC_SOUTH"] == 6
    assert stock_after(10, 4) == 6
    granted, bal = reserve_stock(ledger, "DC_NORTH", "SUB1", 4)
    assert granted == 4 and bal == 6
    assert release_stock(ledger, "DC_NORTH", "SUB1", 2) == 8
    assert len(ledger_to_records(ledger)) == 2
    alloc = Allocation("ALC-1", "DC_NORTH", "SUB1", "WM1", 4, 6)
    assert conservation_check(st, [alloc]) is True
