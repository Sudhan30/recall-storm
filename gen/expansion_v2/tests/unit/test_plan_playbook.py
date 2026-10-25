"""Unit tests for recallstorm.plan.playbook."""
from datetime import datetime
from contract import Store, StoreFormat
from recallstorm.core.jsonl import validate_record
from recallstorm.plan.playbook import (
    PlaybookBuilder,
    build_playbook,
    playbook_counts,
    playbook_deadline,
    playbook_exceptions,
    playbook_manifests,
    playbook_summary,
    playbook_to_record,
    playbook_windows,
)


def test_plan_playbook():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    tasks = [
        {
            "task_id": "T1",
            "store_id": "WM1",
            "action": "PULL",
            "qty_units": 10,
            "associate_id": "WM1-A01",
            "window": ["2026-12-30T22:00:00-08:00", "2026-12-30T22:15:00-08:00"],
        }
    ]
    excs = [{"exc_id": "EXC-WM1-N1", "store_id": "WM1"}]
    mnfs = [{"manifest_id": "MNF-1", "stops": [{"store_id": "WM1", "cases": 1}]}]

    pb = build_playbook(st, tasks, excs, mnfs, dl)
    assert validate_record(pb, "store_playbook") == []
    assert playbook_counts(tasks)["PULL"] == 1
    assert len(playbook_windows(tasks, dl)) == 1
    assert playbook_deadline(st, dl).endswith("-08:00")
    assert playbook_exceptions(excs, "WM1") == ["EXC-WM1-N1"]
    assert playbook_manifests(mnfs, "WM1") == ["MNF-1"]
    assert playbook_to_record(pb)["type"] == "store_playbook"
    assert playbook_summary([pb])["total_tasks"] == 1
    assert PlaybookBuilder(st).store == st
