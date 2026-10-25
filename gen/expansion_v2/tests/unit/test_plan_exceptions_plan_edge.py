"""Edge case tests for recallstorm.plan.exceptions_plan."""
from contract import StoreNote
from recallstorm.plan.exceptions_plan import exception_records


def test_plan_exceptions_edge():
    n = StoreNote("N1", "WM1", "Topstock overflow")
    recs = exception_records([n], {})
    assert recs[0]["task_ids"] == []
