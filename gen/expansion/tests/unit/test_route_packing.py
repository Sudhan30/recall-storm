"""Unit tests for recallstorm.route.packing."""
from datetime import datetime, timezone
from contract import Sku, Store, StoreFormat, Truck
from recallstorm.route.packing import (
    PackingResult,
    first_fit_decreasing,
    fits_truck,
    manifest_to_record,
    pack_returns,
    pack_truck,
    packing_summary,
    split_stop,
    truck_utilization,
)


def test_pack_returns_and_bin_packing():
    dt = datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc)
    sk1 = Sku("S1", "00012345678905", "Candy", "B", "candy", "RED 3", True, False, 12, 2.0, 10.0)
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    st2 = Store("WM2", StoreFormat.SUPERCENTER, "CA", "LA", 34.1, -118.1, "D01", "DC1", "America/Los_Angeles")
    t0 = Truck("DC1-T0", "DC1", 3400.0, 40000.0, dt)
    t1 = Truck("DC1-T1", "DC1", 3400.0, 40000.0, dt)

    pulled = {("WM1", "S1"): 10, ("WM2", "S1"): 5}
    manifests = pack_returns(pulled, [sk1], [t0, t1], [st1, st2])
    assert len(manifests) == 1
    assert sum(s.cases for s in manifests[0].stops) == 15
    assert fits_truck(100.0, 1000.0, 20.0, 100.0, 3400.0, 40000.0) is True
    assert truck_utilization(manifests[0], t0) > 0.0

    rec = manifest_to_record(manifests[0], t0)
    assert rec["type"] == "route_manifest"
    assert packing_summary(manifests)["total_cases"] == 15
    pr = PackingResult(tuple(manifests), 15)
    assert pr.total_cases == 15

    sp, rem = split_stop("WM1", 10, 2.0, 10.0, 10.0, 1000.0)
    assert sp is not None and sp.cases == 5 and rem == 5
    packed, left = pack_truck(t0, [{"store_id": "WM1", "cases": 5, "cube_ft3": 10.0, "weight_lb": 50.0}])
    assert len(packed) == 1 and left == []
    assert len(first_fit_decreasing([{"store_id": "WM1", "cases": 5, "cube_ft3": 10.0, "weight_lb": 50.0}], [t0])) == 1
