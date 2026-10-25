"""Property tests for recallstorm.plan.playbook."""
from datetime import datetime
from contract import Store, StoreFormat
from recallstorm.core.jsonl import validate_record
from recallstorm.plan.playbook import build_playbook


def test_all_playbooks_valid_schema():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    for fmt in StoreFormat:
        st = Store(f"ST_{fmt.value}", fmt, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
        pb = build_playbook(st, [], [], [], dl)
        assert validate_record(pb, "store_playbook") == []
