"""Unit tests for recallstorm.plan.handoffs."""
from contract import Allocation
from recallstorm.core.jsonl import validate_record
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


def test_plan_handoffs():
    win = ["2026-12-31T02:00:00-08:00", "2026-12-31T04:00:00-08:00"]
    alloc = Allocation("ALC-1", "DC1", "SUB1", "WM1", 2, 3)
    mnf = {"manifest_id": "MNF-1", "dc_id": "DC1", "stops": [{"store_id": "WM1", "cases": 4}]}
    flt = {"associate_id": "FLT-1", "store_id": "WM1", "window": win, "task_ids": ["TSK-1"]}

    h1 = floater_handoff("FLT-1", "WM1", win, ["TSK-1"], 0)
    h2 = sub_transfer_handoff(alloc, win, 0)
    h3 = return_consolidation("WM1", "DC1", win, 4, "MNF-1", 0)
    for h in (h1, h2, h3):
        assert validate_record(h, "handoff") == []

    all_h = build_handoffs([alloc], [mnf], [flt], win)
    assert len(all_h) == 3
    assert handoff_to_record(h1)["type"] == "handoff"
    assert len(pair_handoffs(all_h)["SUB_TRANSFER"]) == 1
    assert len(handoff_windows(all_h)) == 3
    assert handoff_summary(all_h)["RETURN_CONSOLIDATION"] == 1
    assert HandoffBuilder(win).default_window == win
