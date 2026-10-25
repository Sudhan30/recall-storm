"""Edge tests for recallstorm.plan.playbook."""
from datetime import datetime
from contract import Store, StoreFormat
from recallstorm.plan.playbook import build_playbook


def test_playbook_empty_tasks():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    pb = build_playbook(st, [], [], [], dl, fallback_associate_ids=["WM1-A01"])
    assert pb["associate_ids"] == ["WM1-A01"]
    assert pb["counts"]["total_tasks"] == 0
