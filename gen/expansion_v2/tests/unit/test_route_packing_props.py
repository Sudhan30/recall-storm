"""Property tests for recallstorm.route.packing."""
from datetime import datetime
import random
from contract import Sku, Store, StoreFormat, Truck
from recallstorm.route.capacity import capacity_check
from recallstorm.route.packing import pack_returns


def test_pack_returns_conservation_and_capacity_props():
    rng = random.Random(42)
    dep = datetime.fromisoformat("2026-12-31T08:00:00-08:00")
    skus = [Sku(f"S{i}", "00012345678905", "N", "B", "c", "I", True, False, 12, 2.0, 15.0) for i in range(5)]
    stores = [
        Store(f"WM{i:03d}", StoreFormat.SUPERCENTER, "CA", "LA", 34.0 + i * 0.05, -118.0, "D01", f"DC{i % 2}", "America/Los_Angeles")
        for i in range(12)
    ]
    trucks = [
        Truck(f"DC{d}-T{t}", f"DC{d}", 3400.0, 40000.0, dep)
        for d in range(2)
        for t in range(4)
    ]
    t_map = {t.truck_id: t for t in trucks}

    for _ in range(25):
        pulled = {(st.store_id, f"S{rng.randint(0, 4)}"): rng.randint(1, 20) for st in stores}
        expected_total = sum(pulled.values())
        mnfs = pack_returns(pulled, skus, trucks, stores)
        packed_total = sum(sum(s.cases for s in m.stops) for m in mnfs)
        assert packed_total == expected_total
        for m in mnfs:
            assert capacity_check(t_map[m.truck_id], m.stops)
