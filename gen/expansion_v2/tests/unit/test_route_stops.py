"""Unit tests for recallstorm.route.stops."""
from datetime import datetime
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


def test_route_stops():
    s1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    s2 = Store("WM2", StoreFormat.SUPERCENTER, "CA", "LA", 34.1, -118.1, "D01", "DC1", "America/Los_Angeles")
    st1 = Stop("WM1", 5, 10.0, 50.0)
    st1_b = Stop("WM1", 3, 6.0, 30.0)
    st2 = Stop("WM2", 4, 8.0, 40.0)

    merged = merge_stops([st1, st1_b, st2])
    assert len(merged) == 2 and merged[0].cases == 8
    nn = nearest_neighbor_order([st2, st1], {"WM1": s1, "WM2": s2})
    assert [x.store_id for x in nn] == ["WM1", "WM2"]
    ordered = order_stops([st2, st1], {"WM1": s1, "WM2": s2})
    assert len(ordered) == 2
    assert route_distance(ordered, {"WM1": s1, "WM2": s2}) > 0.0
    dep = datetime(2026, 12, 31, 8, 0)
    assert stop_eta(dep, 0, 30) == datetime(2026, 12, 31, 8, 30)
    mnf = RouteManifest("M1", "T1", "DC1", ordered, dep)
    assert stops_for_truck(mnf) == ordered
    assert stop_to_record(st1)["store_id"] == "WM1"
    assert stops_summary(ordered)["total_cases"] == 9
    assert RoutePlanner({"WM1": s1}).stores["WM1"] == s1
