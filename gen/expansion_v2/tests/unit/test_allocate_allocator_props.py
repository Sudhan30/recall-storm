"""Property tests for recallstorm.allocate.allocator."""
import random
from contract import DcStock, Store, StoreFormat
from recallstorm.allocate.allocator import allocate_substitutes, never_exceeds_stock


def test_allocate_substitutes_conservation_and_determinism_props():
    rng = random.Random(42)
    stores = [
        Store(f"WM{i:04d}", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", f"DC{i % 3}", "America/Los_Angeles")
        for i in range(15)
    ]
    for _ in range(30):
        stock = [
            DcStock(f"DC{d}", f"SUB{k}", rng.randint(0, 25))
            for d in range(3)
            for k in range(4)
        ]
        demand = {
            (st.store_id, f"SUB{rng.randint(0, 3)}"): rng.randint(1, 10)
            for st in stores
        }
        a1 = allocate_substitutes(demand, stock, stores)
        a2 = allocate_substitutes(demand, stock, list(reversed(stores)))
        assert a1 == a2
        assert never_exceeds_stock(stock, a1)
        for alloc in a1:
            assert isinstance(alloc.qty_cases, int) and alloc.qty_cases > 0
            assert alloc.dc_balance_after >= 0
