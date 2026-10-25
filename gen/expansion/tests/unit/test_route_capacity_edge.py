"""Edge tests for recallstorm.route.capacity."""
from datetime import datetime, timezone
import pytest
from contract import RouteManifest, Stop, Truck
from recallstorm.route.capacity import (
    capacity_check,
    overload_report,
    truck_capacity,
)


def test_capacity_edge():
    dt = datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc)
    tr = Truck("DC1-T0", "DC1", 100.0, 1000.0, dt)
    over_stop = Stop("WM1", 50, 200.0, 500.0)
    assert capacity_check(tr, [over_stop]) is False
    mnf = RouteManifest("MNF-1", "DC1-T0", "DC1", (over_stop,), dt)
    assert overload_report([mnf], {"DC1-T0": tr}) != []
    with pytest.raises(TypeError):
        truck_capacity("not_truck")  # type: ignore[arg-type]
