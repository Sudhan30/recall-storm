"""Property tests for recallstorm.comms.associate_briefings."""
from recallstorm.comms.associate_briefings import track_unbriefed_scheduled_associates


def test_unbriefed_associates_subset_props():
    sched = [f"A{i}" for i in range(20)]
    briefed = {f"A{i}" for i in range(0, 20, 2)}
    unbriefed = track_unbriefed_scheduled_associates(sched, briefed)
    assert len(unbriefed) + len(briefed) == 20
