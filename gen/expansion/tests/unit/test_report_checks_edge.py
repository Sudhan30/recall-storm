"""Edge tests for recallstorm.report.checks."""
from recallstorm.report.checks import (
    check_contradictions,
    check_deadline,
)


def test_checks_detect_violations():
    contradictory = [
        {"type": "sku_verdict", "sku_id": "S1", "verdict": "KEEP"},
        {"type": "shelf_task", "task_id": "T1", "sku_id": "S1", "action": "PULL"},
    ]
    assert check_contradictions(contradictory) != []

    late = [
        {"type": "shelf_task", "window": ["2027-01-01T00:00:00-08:00", "2027-01-01T01:00:00-08:00"]},
    ]
    assert check_deadline(late, "2027-01-01T00:00:00-08:00") != []
