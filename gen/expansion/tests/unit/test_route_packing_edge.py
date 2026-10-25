"""Edge tests for recallstorm.route.packing."""
from datetime import datetime, timezone
import pytest
from contract import Sku, Store, StoreFormat, Truck
from recallstorm.core.errors import RoutingError
from recallstorm.route.packing import (
    first_fit_decreasing,
    pack_returns,
    split_stop,
)


def test_packing_edge():
    dt = datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc)
    sk1 = Sku("S1", "00012345678905", "Candy", "B", "candy", "RED 3", True, False, 12, 2.0, 10.0)
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    small_truck = Truck("DC1-T0", "DC1", 5.0, 50.0, dt)

    assert pack_returns({}, [sk1], [small_truck], [st1]) == []
    assert split_stop("WM1", 0, 2.0, 10.0, 100.0, 100.0) == (None, 0)
    with pytest.raises(RoutingError):
        pack_returns({("WM1", "S1"): 100}, [sk1], [small_truck], [st1])
    with pytest.raises(RoutingError):
        first_fit_decreasing([{"store_id": "WM1", "cases": 5, "cube_ft3": 10.0, "weight_lb": 50.0}], [])
