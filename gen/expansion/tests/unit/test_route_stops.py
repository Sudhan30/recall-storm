"""Unit tests for recallstorm.route.stops."""
from datetime import datetime, timezone
from contract import RouteManifest, Stop, Store, StoreFormat
from recallstorm.route.stops import (
    RoutePlanner,
    merge_stops,
    nearest_neighbor_order,
    order_stops,
    route_distance,
    stop_eta,
    stop_to_record,
    stops_for_truck,
    stops_summary,
)


def test_stops_ordering():
    rp = RoutePlanner("DC1")
    assert rp.dc_id == "DC1"
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    st2 = Store("WM2", StoreFormat.SUPERCENTER, "CA", "LA", 34.1, -118.1, "D01", "DC1", "America/Los_Angeles")
    s1a = Stop("WM1", 2, 3.0, 10.0)
    s1b = Stop("WM1", 3, 4.5, 15.0)
    s2 = Stop("WM2", 4, 6.0, 20.0)

    merged = merge_stops([s2, s1a, s1b])
    assert len(merged) == 2 and merged[0].cases == 5
    nn = nearest_neighbor_order([s2, s1a, s1b], {"WM1": st1, "WM2": st2})
    ordered = order_stops(nn, {"WM1": st1, "WM2": st2})
    assert len(ordered) == 2
    assert route_distance(ordered, {"WM1": st1, "WM2": st2}) > 0.0
    dt = datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc)
    assert stop_eta(dt, 0) > dt
    mnf = RouteManifest("MNF-1", "T0", "DC1", ordered, dt)
    assert stops_for_truck(mnf) == ordered
    assert stop_to_record(s2)["store_id"] == "WM2"
    assert stops_summary(ordered)["total_cases"] == 9
