"""Edge tests for recallstorm.sim.events."""
import pytest
from recallstorm.sim.events import event_to_record


def test_events_edge():
    with pytest.raises(ValueError):
        event_to_record({"t": "2026", "store_id": "WM1", "associate_id": "A1", "kind": "BAD", "loc": {}, "task_id": "T1"})
    with pytest.raises(TypeError):
        event_to_record("not_event")  # type: ignore[arg-type]
