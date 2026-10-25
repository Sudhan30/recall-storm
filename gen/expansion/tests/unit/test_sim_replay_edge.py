"""Edge tests for recallstorm.sim.replay."""
from recallstorm.sim.replay import (
    detect_late_events,
    event_times,
    replay_tasks,
)


def test_replay_edge():
    assert event_times("2026-12-30T22:00:00-08:00", "2026-12-30T22:05:00-08:00", 0) == []
    assert replay_tasks([]) == []
    late_ev = [{"t": "2027-01-01T00:00:00-08:00", "task_id": "T1"}]
    assert len(detect_late_events(late_ev, "2027-01-01T00:00:00-08:00")) == 1
