"""Unit tests for recallstorm.route.dispatch."""
from datetime import datetime
from contract import RouteManifest, Stop, Truck
from recallstorm.core.jsonl import validate_record
from recallstorm.route.dispatch import (
    Dispatcher,
    arrival_eta,
    depart_time,
    dispatch_plan,
    dispatch_summary,
    dispatch_to_records,
    driver_hours,
    late_departures,
    validate_dispatch,
)


def test_route_dispatch():
    dep = datetime.fromisoformat("2026-12-31T08:00:00-08:00")
    t = Truck("DC1-T0", "DC1", 3400.0, 40000.0, dep)
    mnf = RouteManifest("MNF-1", "DC1-T0", "DC1", (Stop("WM1", 5, 10.0, 50.0),), dep)

    assert depart_time(t) == dep
    assert arrival_eta(dep, 1) > dep
    assert driver_hours(2, 65.0) == 1.8
    assert len(dispatch_plan([mnf], {"DC1-T0": t})) == 1
    recs = dispatch_to_records([mnf], {"DC1-T0": t})
    assert validate_record(recs[0], "route_manifest") == []
    assert late_departures([mnf], datetime.fromisoformat("2027-01-01T00:00:00-08:00")) == []
    assert validate_dispatch([mnf], {"DC1-T0": t}) == []
    assert dispatch_summary([mnf])["total_stops"] == 1
    assert Dispatcher({"DC1-T0": t}).trucks["DC1-T0"] == t
