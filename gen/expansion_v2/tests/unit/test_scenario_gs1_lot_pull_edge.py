"""Edge case tests for recallstorm.scenario_gs1.lot_pull."""
from contract import Facing, Location, Store, StoreFormat
from recallstorm.scenario_gs1.lot_pull import lot_pull_tasks


def test_scenario_gs1_lot_pull_edge():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    # Unaffected lot on shelf -> no task needed
    tasks = lot_pull_tasks(st, [f1], ["L26*"], {"S1": ["SAFE99"]}, "A1", ["2026-12-30T22:00:00-08:00", "2026-12-30T22:10:00-08:00"])
    assert tasks == []
