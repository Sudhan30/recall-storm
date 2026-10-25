"""Unit tests for recallstorm.plan.tasks."""
from datetime import datetime
from contract import Allocation, Associate, DecidedBy, Facing, Location, Sku, SkuDecision, Store, StoreFormat, Verdict
from recallstorm.core.jsonl import validate_record
from recallstorm.plan.tasks import (
    TaskBuilder,
    build_shelf_tasks,
    hold_verify_task,
    place_sub_task,
    pull_task,
    tag_flash_task,
    task_sequence,
    task_to_record,
    task_window,
)


def test_plan_tasks():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    f2 = Facing("WM1", "S2", Location("A01", 2, 1, 1), 6)
    decs = {
        "S1": SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, ""),
        "S2": SkuDecision("S2", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("R1",), DecidedBy.RULE, ""),
    }
    ev_map = {"S1": "EVD-S1-R1", "S2": "EVD-S2-R1"}
    alloc = Allocation("ALC-1", "DC1", "SUB1", "WM1", 1, 4)
    skus = {"SUB1": Sku("SUB1", "00012345678905", "Sub", "B", "c", "I", True, False, 12, 1.0, 5.0)}
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    assoc = Associate("WM1-A01", "WM1", "D01", False, t0, t1)

    tasks = build_shelf_tasks(st, [f1, f2], decs, ev_map, [alloc], skus, [assoc], dl)
    # S1 generates PULL, TAG_FLASH, PLACE_SUB; S2 generates HOLD_VERIFY -> 4 tasks
    assert len(tasks) == 4
    for t in tasks:
        assert validate_record(t, "shelf_task") == []
    reseq = task_sequence(tasks)
    assert [t["seq"] for t in reseq] == [1, 2, 3, 4]
    assert task_to_record(tasks[0])["type"] == "shelf_task"
    assert TaskBuilder(st).store == st
