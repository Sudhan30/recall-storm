"""Edge case tests for recallstorm.sim.events."""
import pytest
from recallstorm.sim.events import event_to_record


def test_sim_events_edge():
    with pytest.raises(ValueError):
        event_to_record({"t": "2026-12-30", "store_id": "W", "associate_id": "A", "kind": "BAD", "loc": {}, "task_id": "T"})
