"""Property tests for recallstorm.allocate.priority."""
from contract import Store, StoreFormat
from recallstorm.allocate.priority import rank_stores


def test_rank_stores_order_invariance():
    stores = [
        Store(f"WM{i:04d}", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
        for i in range(20)
    ]
    assert rank_stores(stores) == rank_stores(list(reversed(stores)))
