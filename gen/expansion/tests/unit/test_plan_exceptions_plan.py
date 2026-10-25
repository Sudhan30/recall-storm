"""Unit tests for recallstorm.plan.exceptions_plan."""
from contract import StoreNote
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


def test_exceptions_planner():
    n_endcap = StoreNote("N1", "WM1", "Endcap 16 holds a vendor display.")
    n_unclear = StoreNote("N2", "WM1", "Labels are smudged from a printer fault.")
    tasks = [
        {"task_id": "TSK-1", "action": "PULL"},
        {"task_id": "TSK-2", "action": "HOLD_VERIFY"},
    ]
    assert dsd_exception_task(n_endcap, tasks) == ["TSK-1"]
    assert endcap_exception_task(n_endcap, tasks) == ["TSK-1"]
    assert topstock_exception_task(n_endcap, tasks) == ["TSK-1"]
    assert totes_exception_task(n_endcap, tasks) == ["TSK-1"]
    assert planogram_exception_task(n_endcap, tasks) == ["TSK-1"]
    assert unclear_label_task(n_unclear, tasks) == ["TSK-2"]
    assert exception_tasks(n_endcap, tasks) == ["TSK-1"]

    recs = exception_records([n_endcap, n_unclear], {"WM1": tasks})
    assert len(recs) == 2
    assert recs[0]["type"] == "exception"
    ep = ExceptionPlanner((n_endcap,))
    assert len(ep.notes) == 1
