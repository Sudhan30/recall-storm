"""Property tests for recallstorm.plan.tasks."""
from datetime import datetime, timedelta
import random
from recallstorm.plan.tasks import task_window


def test_task_window_always_strictly_before_deadline():
    rng = random.Random(42)
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    for _ in range(30):
        start = dl - timedelta(minutes=rng.randint(-60, 500))
        dur = rng.uniform(1.0, 60.0)
        w = task_window(start, dur, dl)
        assert datetime.fromisoformat(w[0]) < datetime.fromisoformat(w[1]) < dl
