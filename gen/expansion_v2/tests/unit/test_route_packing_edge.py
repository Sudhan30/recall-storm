"""Edge case tests for recallstorm.route.packing."""
from datetime import datetime
import pytest
from contract import Sku, Store, StoreFormat, Truck
from recallstorm.core.errors import RoutingError
from recallstorm.route.packing import pack_returns


def test_pack_returns_splits_across_trucks_and_detects_overflow():
    dep = datetime.fromisoformat("2026-12-31T08:00:00-08:00")
    sku = Sku("S1", "00012345678905", "Heavy", "B", "c", "I", True, False, 6, 100.0, 1000.0)
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    t0 = Truck("DC1-T0", "DC1", 500.0, 5000.0, dep)
    t1 = Truck("DC1-T1", "DC1", 500.0, 5000.0, dep)

    # 8 cases = 800 ft3 -> splits 5 cases on T0 and 3 cases on T1
    mnfs = pack_returns({("WM1", "S1"): 8}, [sku], [t0, t1], [st])
    assert len(mnfs) == 2
    assert sum(sum(s.cases for s in m.stops) for m in mnfs) == 8

    # 20 cases = 2000 ft3 > total fleet 1000 ft3 -> RoutingError
    with pytest.raises(RoutingError):
        pack_returns({("WM1", "S1"): 20}, [sku], [t0, t1], [st])
