"""Edge case tests for recallstorm.route.capacity."""
from datetime import datetime
from contract import RouteManifest, Stop, Truck
from recallstorm.route.capacity import capacity_check, overload_report


def test_route_capacity_edge():
    t = Truck("DC1-T0", "DC1", 100.0, 1000.0, datetime(2026, 12, 31, 8, 0))
    heavy = Stop("WM1", 50, 200.0, 500.0)
    assert capacity_check(t, [heavy]) is False
    mnf = RouteManifest("M1", "DC1-T0", "DC1", (heavy,), t.depart)
    assert len(overload_report([mnf], {"DC1-T0": t})) == 1
