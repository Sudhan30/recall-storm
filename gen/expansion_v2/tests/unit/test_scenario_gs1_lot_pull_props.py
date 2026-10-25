"""Property tests for recallstorm.scenario_gs1.lot_pull."""
from contract import Facing, Location, Store, StoreFormat
from recallstorm.core.jsonl import validate_record
from recallstorm.scenario_gs1.lot_pull import lot_pull_tasks


def test_lot_pull_tasks_valid_schema_props():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    facings = [Facing("WM1", f"S{i}", Location("A01", i + 1, 1, 1), 5) for i in range(10)]
    tasks = lot_pull_tasks(
        st,
        facings,
        ["L26*"],
        {"S0": ["L2601"]},
        "A1",
        ["2026-12-30T22:00:00-08:00", "2026-12-30T22:10:00-08:00"],
    )
    for t in tasks:
        assert validate_record(t, "shelf_task") == []
