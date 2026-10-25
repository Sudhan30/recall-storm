"""Unit tests for recallstorm.labor.estimates."""
from contract import Action
from recallstorm.labor.estimates import (
    EstimateModel,
    estimate_playbook,
    minutes_by_action,
    place_minutes,
    pull_minutes,
    store_minutes,
    tag_minutes,
    task_minutes,
    walk_minutes,
)


def test_labor_estimates():
    assert pull_minutes(10) == 3.0
    assert place_minutes(10) == 3.2
    assert tag_minutes(2) == 2.0
    assert walk_minutes(72.0, 1.2) == 1.0
    assert task_minutes(Action.HOLD_VERIFY, 5) == 3.0
    tasks = [{"action": "PULL", "qty_units": 10}, {"action": "TAG_FLASH", "qty_units": 1}]
    assert minutes_by_action(tasks)["PULL"] == 3.0
    assert store_minutes(tasks) == 4.0
    assert estimate_playbook(tasks)["total"] == 4.0
    assert EstimateModel().tag_mins == 1.0
