"""Unit tests for recallstorm.plan.handoffs."""
from datetime import datetime, timezone
from contract import Allocation, RouteManifest, Stop
from recallstorm.plan.handoffs import (
    HandoffBuilder,
    build_handoffs,
    floater_handoff,
    handoff_summary,
    handoff_to_record,
    handoff_windows,
    pair_handoffs,
    return_consolidation,
    sub_transfer_handoff,
)


def test_handoff_generation():
    win = ("2026-12-31T06:00:00-08:00", "2026-12-31T12:00:00-08:00")
    hb = HandoffBuilder(win)
    assert hb.default_window == win

    h_flt = floater_handoff("FLT-1", "WM1", win, ["TSK-1"], 0)
    h_sub = sub_transfer_handoff("DC1", "WM1", win, 2, "ALC-1", 0)
    h_ret = return_consolidation("WM1", "DC1", win, 3, "MNF-1", 0)
    assert h_flt["kind"] == "FLOATER"
    assert h_sub["kind"] == "SUB_TRANSFER"
    assert h_ret["kind"] == "RETURN_CONSOLIDATION"

    alloc = Allocation("ALC-1", "DC1", "SUB1", "WM1", 2, 1)
    mnf = RouteManifest("MNF-1", "T0", "DC1", (Stop("WM1", 3, 4.5, 15.0),), datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc))
    all_h = build_handoffs([alloc], [mnf], [{"associate_id": "FLT-1", "store_id": "WM1", "window": list(win), "task_ids": ["TSK-1"]}], win)
    assert len(all_h) == 3
    assert handoff_to_record(all_h[0])["type"] == "handoff"
    assert len(pair_handoffs(all_h)) == 3
    assert len(handoff_windows(all_h)) == 3
    assert handoff_summary(all_h)["total_handoffs"] == 3
