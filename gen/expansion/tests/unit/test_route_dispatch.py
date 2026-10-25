"""Unit tests for recallstorm.route.dispatch."""
from datetime import datetime, timezone
from contract import RouteManifest, Stop, Truck
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


def test_dispatch_scheduling():
    disp = Dispatcher()
    assert disp.max_driver_hours == 11.0
    dt = datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc)
    tr = Truck("DC1-T0", "DC1", 3400.0, 40000.0, dt)
    st = Stop("WM1", 5, 10.0, 50.0)
    mnf = RouteManifest("MNF-1", "DC1-T0", "DC1", (st,), dt)

    assert depart_time(tr) == dt
    assert arrival_eta(dt, 1, 20.0) > dt
    assert driver_hours([st], 40.0) == 1.35
    plan = dispatch_plan([mnf], {"DC1-T0": tr})
    assert len(dispatch_to_records(plan)) == 1
    assert late_departures([mnf], datetime(2027, 1, 1, tzinfo=timezone.utc)) == []
    assert validate_dispatch(plan) == []
    assert dispatch_summary(plan)["total_stops"] == 1
