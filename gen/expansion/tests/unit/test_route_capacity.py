"""Unit tests for recallstorm.route.capacity."""
from datetime import datetime, timezone
from contract import RouteManifest, Stop, Truck
from recallstorm.route.capacity import (
    CapacityModel,
    capacity_check,
    capacity_summary,
    capacity_to_record,
    overload_report,
    remaining_cube,
    remaining_weight,
    truck_capacity,
    utilization_by_dc,
)


def test_capacity_functions():
    cm = CapacityModel()
    assert cm.cube_ft3 == 3400.0
    dt = datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc)
    tr = Truck("DC1-T0", "DC1", 3400.0, 40000.0, dt)
    st = Stop("WM1", 10, 340.0, 4000.0)

    assert truck_capacity(tr) == (3400.0, 40000.0)
    assert remaining_cube(tr, [st]) == 3060.0
    assert remaining_weight(tr, [st]) == 36000.0
    assert capacity_check(tr, [st]) is True
    mnf = RouteManifest("MNF-1", "DC1-T0", "DC1", (st,), dt)
    assert overload_report([mnf], {"DC1-T0": tr}) == []
    assert utilization_by_dc([mnf], {"DC1-T0": tr}) == {"DC1": 0.1}
    assert capacity_to_record(tr)["cube_ft3"] == 3400.0
    assert capacity_summary([tr])["truck_count"] == 1
