"""Edge tests for recallstorm.labor.assign."""
from datetime import datetime
import pytest
from recallstorm.labor.assign import (
    assign_floaters,
    assignment_conflicts,
    greedy_assign,
)
from contract import Store, StoreFormat


def test_assign_edge():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert greedy_assign([], [], dl) == []
    assert assign_floaters([], [], st, dl) == []
    with pytest.raises(ValueError):
        greedy_assign([{"task_id": "T1"}], [], dl)
    assert assignment_conflicts([{"task_id": "T1", "window": ["2027-01-01T01:00:00-08:00", "2027-01-01T02:00:00-08:00"]}], dl) != []
