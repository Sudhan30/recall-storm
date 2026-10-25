"""Property tests for recallstorm.sim.metrics."""
from recallstorm.sim.metrics import completion_curve


def test_completion_curve_strictly_increasing():
    evs = [
        {"t": f"2026-12-30T22:{i:02d}:00-08:00", "store_id": "WM1", "associate_id": "A1", "kind": "DONE", "loc": {}, "task_id": f"T{i}"}
        for i in range(1, 20)
    ]
    curve = completion_curve(evs)
    counts = [c for _, c in curve]
    assert counts == list(range(1, 20))
