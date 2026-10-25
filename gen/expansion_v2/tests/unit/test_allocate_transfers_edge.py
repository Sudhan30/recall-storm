"""Edge case tests for recallstorm.allocate.transfers."""
from recallstorm.allocate.transfers import validate_transfers


def test_allocate_transfers_edge():
    bad = [{"handoff_id": "H1", "kind": "BAD", "qty": 0}]
    assert len(validate_transfers(bad)) == 2
