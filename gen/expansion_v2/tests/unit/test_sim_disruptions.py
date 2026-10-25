"""Unit tests for recallstorm.sim.disruptions."""
from contract import Store, StoreFormat
from recallstorm.sim.disruptions import (
    Disruption,
    DisruptionSet,
    absent_associate,
    disruption_report,
    inject_disruption,
    replan_after_disruption,
    seed_disruptions,
    stockout_event,
    truck_delay,
)


def test_sim_disruptions():
    d_abs = absent_associate("WM1-A01", "WM1")
    d_trk = truck_delay("DC1-T0", 45)
    d_stk = stockout_event("DC1", "SUB1")
    assert isinstance(d_abs, Disruption) and d_stk.kind == "STOCKOUT"

    recs = [
        {"type": "shelf_task", "task_id": "T1", "associate_id": "WM1-A01"},
        {"type": "route_manifest", "truck_id": "DC1-T0", "depart": "2026-12-31T08:00:00-08:00"},
    ]
    delayed = inject_disruption(recs, d_trk)
    assert "08:45:00" in delayed[1]["depart"]
    replanned = replan_after_disruption(recs, d_abs, "WM1-A02")
    assert replanned[0]["associate_id"] == "WM1-A02"

    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    seeded = seed_disruptions([st], seed=42)
    assert len(seeded) == 1
    assert disruption_report(seeded)["count"] == 1
    assert len(DisruptionSet(seeded).items) == 1
