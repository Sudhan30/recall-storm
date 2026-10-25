"""Property tests for recallstorm.allocate.stock."""
import random
from contract import DcStock
from recallstorm.allocate.stock import reserve_stock, stock_ledger


def test_reserve_stock_conservation_props():
    rng = random.Random(42)
    init = 50
    ledger = stock_ledger([DcStock("DC1", "S1", init)])
    total_granted = 0
    for _ in range(20):
        req = rng.randint(1, 10)
        g, bal = reserve_stock(ledger, "DC1", "S1", req)
        total_granted += g
        assert total_granted + bal == init
        assert bal >= 0
