"""Edge tests for recallstorm.allocate.stock."""
import pytest
from contract import Allocation, DcStock
from recallstorm.allocate.stock import (
    conservation_check,
    reserve_stock,
    stock_ledger,
)
from recallstorm.core.errors import AllocationError


def test_stock_edge():
    st = [DcStock("DC1", "SUB1", 3)]
    ledger = stock_ledger(st)
    with pytest.raises(AllocationError):
        reserve_stock(ledger, "DC1", "SUB1", 5)
    with pytest.raises(AllocationError):
        stock_ledger([DcStock("DC1", "SUB1", -1)])
    bad_alloc = Allocation("ALC-1", "DC1", "SUB1", "WM1", 4, 0)
    assert conservation_check(st, [bad_alloc]) is False
