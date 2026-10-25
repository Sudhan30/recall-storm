"""Unit tests for recallstorm.route.packing."""
from datetime import datetime
from contract import Sku, Store, StoreFormat, Truck
from recallstorm.core.jsonl import validate_record
from recallstorm.route.capacity import capacity_check
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


def test_pack_returns_basic():
    dep = datetime.fromisoformat("2026-12-31T08:00:00-08:00")
    sku = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "baking", "RED 3", True, False, 6, 2.0, 20.0)
    s1 = Store("WM1563", StoreFormat.SUPERCENTER, "CA", "Lancaster", 34.6, -118.1, "D06", "DC_CENTRAL", "America/Los_Angeles")
    s2 = Store("WM1574", StoreFormat.SUPERCENTER, "CA", "Bakersfield", 35.2, -119.0, "D06", "DC_CENTRAL", "America/Los_Angeles")
    t0 = Truck("DC_CENTRAL-T0", "DC_CENTRAL", 3400.0, 40000.0, dep)

    pulled = {("WM1563", "FDC1034191"): 10, ("WM1574", "FDC1034191"): 15}
    mnfs = pack_returns(pulled, [sku], [t0], [s1, s2])
    assert len(mnfs) == 1
    assert sum(s.cases for s in mnfs[0].stops) == 25
    assert capacity_check(t0, mnfs[0].stops) is True

    rec = manifest_to_record(mnfs[0], t0)
    assert validate_record(rec, "route_manifest") == []
    assert fits_truck(t0, 100.0, 1000.0, 50.0, 500.0) is True
    part, rem = split_stop("WM1", 10, 2.0, 20.0, 10.0, 500.0)
    assert part is not None and part.cases == 5 and rem == 5
    loaded, left = pack_truck(t0, [("WM1", 5, 10.0, 100.0)])
    assert len(loaded) == 1 and left == []
    assert "DC_CENTRAL-T0" in first_fit_decreasing([("WM1", 5, 10.0, 100.0)], [t0])
    assert truck_utilization(mnfs[0], t0)["cube_ratio"] > 0.0
    assert packing_summary(mnfs)["total_cases"] == 25
    assert len(PackingResult(mnfs).manifests) == 1
