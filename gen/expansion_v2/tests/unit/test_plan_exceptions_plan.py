"""Unit tests for recallstorm.plan.exceptions_plan."""
from contract import StoreNote
from recallstorm.core.jsonl import validate_record
from recallstorm.plan.exceptions_plan import (
    ExceptionPlanner,
    dsd_exception_task,
    endcap_exception_task,
    exception_records,
    exception_tasks,
    planogram_exception_task,
    topstock_exception_task,
    totes_exception_task,
    unclear_label_task,
)


def test_plan_exceptions():
    n = StoreNote("N0000", "SAMS4735", "Endcap 16 holds a vendor display.")
    for fn in (
        dsd_exception_task,
        endcap_exception_task,
        topstock_exception_task,
        totes_exception_task,
        planogram_exception_task,
        unclear_label_task,
    ):
        rec = fn(n, ["TSK-1"])
        assert validate_record(rec, "exception") == []

    excs, tasks = exception_tasks([n], [{"task_id": "TSK-1", "store_id": "SAMS4735"}])
    assert len(excs) == 1 and excs[0]["task_ids"] == ["TSK-1"]
    assert len(exception_records([n], {"SAMS4735": tasks})) == 1
    assert len(ExceptionPlanner([n]).notes) == 1
