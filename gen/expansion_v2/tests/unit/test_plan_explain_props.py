"""Property tests for recallstorm.plan.explain."""
from recallstorm.plan.explain import plan_narrative


def test_plan_narrative_determinism():
    recs = [{"type": "shelf_task"}, {"type": "run"}, {"type": "evidence"}]
    assert plan_narrative(recs) == plan_narrative(list(reversed(recs)))
