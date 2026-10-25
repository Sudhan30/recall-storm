"""Edge case tests for recallstorm.plan.playbook."""
from datetime import datetime
from contract import Store, StoreFormat
from recallstorm.plan.playbook import build_playbook


def test_plan_playbook_empty_tasks():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    pb = build_playbook(st, [], [], [], dl)
    assert pb["counts"]["tasks"] == 0
    assert datetime.fromisoformat(pb["windows"][0][1]) < dl
