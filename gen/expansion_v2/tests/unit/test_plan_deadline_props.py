"""Property tests for recallstorm.plan.deadline."""
from datetime import datetime, timedelta
import random
from recallstorm.plan.deadline import deadline_violations, enforce_deadline


def test_enforce_deadline_eliminates_all_violations():
    rng = random.Random(42)
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    recs = []
    for i in range(20):
        s = dl + timedelta(minutes=rng.randint(-200, 200))
        e = s + timedelta(minutes=rng.randint(10, 120))
        recs.append({"type": "shelf_task", "task_id": f"T{i}", "window": [s.isoformat(), e.isoformat()]})
    fixed = enforce_deadline(recs, dl)
    assert deadline_violations(fixed, dl) == []
