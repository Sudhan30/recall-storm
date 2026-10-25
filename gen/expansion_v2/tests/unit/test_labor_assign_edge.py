"""Edge case tests for recallstorm.labor.assign."""
from datetime import datetime
from recallstorm.labor.assign import assign_tasks, assignment_conflicts, greedy_assign


def test_labor_assign_edge():
    assert greedy_assign([], []) == []
    deadline = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    unassigned = assign_tasks([{"task_id": "T1", "store_id": "WM1", "action": "PULL", "qty_units": 5}], [], deadline)
    assert len(assignment_conflicts(unassigned)) == 1
