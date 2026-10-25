"""Property tests for recallstorm.plan.handoffs."""
from contract import Allocation, HandoffKind
from recallstorm.core.jsonl import validate_record
from recallstorm.plan.handoffs import sub_transfer_handoff


def test_sub_transfer_handoff_schema_props():
    win = ["2026-12-31T01:00:00-08:00", "2026-12-31T02:00:00-08:00"]
    for i in range(15):
        a = Allocation(f"ALC-{i}", "DC1", "SUB1", f"WM{i}", i + 1, 10)
        h = sub_transfer_handoff(a, win, i)
        assert validate_record(h, "handoff") == []
        assert h["kind"] == HandoffKind.SUB_TRANSFER.value
