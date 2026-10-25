"""Edge case tests for recallstorm.allocate.stock."""
import pytest
from contract import Allocation, DcStock
from recallstorm.allocate.stock import conservation_check, reserve_stock, stock_after, stock_ledger
from recallstorm.core.errors import AllocationError


def test_allocate_stock_edge():
    with pytest.raises(AllocationError):
        stock_after(5, 10)
    with pytest.raises(AllocationError):
        stock_ledger([DcStock("DC1", "S1", -1)])
    ledger = stock_ledger([DcStock("DC1", "S1", 3)])
    g, b = reserve_stock(ledger, "DC1", "S1", 10)
    assert g == 3 and b == 0
    bad_alloc = Allocation("ALC-1", "DC1", "S1", "WM1", 5, 0)
    assert conservation_check([DcStock("DC1", "S1", 3)], [bad_alloc]) is False
