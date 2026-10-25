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


def test_stock_ledger_and_conservation():
    st = [DcStock("DC_NORTH", "SUB1", 10), DcStock("DC_SOUTH", "SUB2", 5)]
    ledger = stock_ledger(st)
    assert isinstance(ledger, StockLedger)
    assert stock_for_dc(st, "DC_NORTH") == {"SUB1": 10}
    assert stock_for_sku(st, "DC_NORTH", "SUB1") == 10
    assert reserve_stock(ledger, "DC_NORTH", "SUB1", 4) == 6
    assert release_stock(ledger, "DC_NORTH", "SUB1", 2) == 8
    assert len(ledger_to_records(ledger)) == 2

    alloc = Allocation("ALC-1", "DC_NORTH", "SUB1", "WM1", 4, 6)
    assert conservation_check(st, [alloc]) is True
    assert stock_after(st, [alloc])[("DC_NORTH", "SUB1")] == 6
