"""Property tests for recallstorm.route.dispatch."""
from datetime import datetime
from contract import RouteManifest, Stop, Truck
from recallstorm.core.jsonl import validate_record
from recallstorm.route.dispatch import dispatch_to_records


def test_dispatch_to_records_schema_props():
    dep = datetime.fromisoformat("2026-12-31T08:00:00-08:00")
    t = Truck("DC1-T0", "DC1", 3400.0, 40000.0, dep)
    mnfs = [RouteManifest(f"MNF-{i}", "DC1-T0", "DC1", (Stop(f"WM{i}", 2, 4.0, 20.0),), dep) for i in range(10)]
    for r in dispatch_to_records(mnfs, {"DC1-T0": t}):
        assert validate_record(r, "route_manifest") == []
