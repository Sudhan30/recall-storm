"""Unit tests for recallstorm.plan.tasks."""
from datetime import datetime
from contract import Allocation, Associate, DecidedBy, Facing, Location, SkuDecision, Store, StoreFormat, Verdict
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


def test_build_shelf_tasks():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    s_start = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    s_end = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assoc = Associate("WM1-A01", "WM1", "D01", False, s_start, s_end)
    f1 = Facing("WM1", "S1", Location("A01", 1, 1, 1), 10)
    f2 = Facing("WM1", "S2", Location("A01", 1, 2, 1), 8)
    f3 = Facing("WM1", "S3", Location("A01", 1, 3, 1), 6)

    decs = {
        "S1": SkuDecision("S1", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, "r"),
        "S2": SkuDecision("S2", Verdict.PULL, "RED3", "Red 3", 0, 5, ("R1",), DecidedBy.RULE, "r"),
        "S3": SkuDecision("S3", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("R1",), DecidedBy.RULE, "r"),
    }
    ev = {
        "S1": {"evidence_id": "EVD-1"},
        "S2": {"evidence_id": "EVD-2"},
        "S3": {"evidence_id": "EVD-3"},
    }
    alloc = Allocation("ALC-1", "DC1", "SUB1", "WM1", 1, 4)

    tb = TaskBuilder(st, dl)
    assert tb.store == st
    win = task_window(s_start, 10, dl)
    assert pull_task("WM1", f1, "WM1-A01", win, 1, "EVD-1")["action"] == "PULL"
    assert hold_verify_task("WM1", f3, "WM1-A01", win, 2, "EVD-3")["action"] == "HOLD_VERIFY"
    assert place_sub_task("WM1", f1, "SUB1", "ALC-1", 10, "WM1-A01", win, 3, "EVD-1")["action"] == "PLACE_SUB"
    assert tag_flash_task("WM1", f2, "WM1-A01", win, 4, "EVD-2")["action"] == "TAG_FLASH"

    tasks = build_shelf_tasks(
        st,
        [f1, f2, f3],
        decs,
        ev,
        {("WM1", "SUB1"): alloc},
        {"S1": "SUB1"},
        [assoc],
        dl,
    )
    actions = [t["action"] for t in tasks]
    assert actions == ["PULL", "PLACE_SUB", "PULL", "TAG_FLASH", "HOLD_VERIFY"]
    reseq = task_sequence(tasks)
    assert [t["seq"] for t in reseq] == [1, 2, 3, 4, 5]
    assert task_to_record(tasks[0])["type"] == "shelf_task"
