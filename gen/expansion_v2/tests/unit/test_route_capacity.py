"""Unit tests for recallstorm.route.capacity."""
from datetime import datetime
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


def test_route_capacity():
    t = Truck("DC1-T0", "DC1", 3400.0, 40000.0, datetime(2026, 12, 31, 8, 0))
    st = Stop("WM1", 10, 400.0, 5000.0)
    mnf = RouteManifest("MNF-1", "DC1-T0", "DC1", (st,), t.depart)

    assert truck_capacity(t) == (3400.0, 40000.0)
    assert remaining_cube(t, [st]) == 3000.0
    assert remaining_weight(t, [st]) == 35000.0
    assert capacity_check(t, [st]) is True
    assert overload_report([mnf], {"DC1-T0": t}) == []
    assert utilization_by_dc([mnf], {"DC1-T0": t})["DC1"]["cube_ft3"] == 400.0
    assert capacity_to_record(t)["cube_ft3"] == 3400.0
    assert capacity_summary([mnf], [t])["overload_count"] == 0
    assert CapacityModel().default_cube_ft3 == 3400.0
