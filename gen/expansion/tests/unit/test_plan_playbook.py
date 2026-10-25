"""Unit tests for recallstorm.plan.playbook."""
from datetime import datetime
from contract import RouteManifest, Stop, Store, StoreFormat
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


def test_playbook_generation():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    pb_builder = PlaybookBuilder(dl)
    assert pb_builder.deadline == dl

    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    tasks = [
        {
            "task_id": "TSK-1",
            "store_id": "WM1",
            "action": "PULL",
            "associate_id": "WM1-A01",
            "window": ["2026-12-30T22:00:00-08:00", "2026-12-30T22:10:00-08:00"],
        }
    ]
    excs = [{"exc_id": "EXC-1", "store_id": "WM1"}]
    mnf = RouteManifest("MNF-1", "T0", "DC1", (Stop("WM1", 2, 3.0, 10.0),), dl)

    assert playbook_counts(tasks)["PULL"] == 1
    assert len(playbook_windows(tasks, ["a", "b"])) == 1
    assert playbook_deadline(dl).startswith("2027-01-01")
    assert playbook_exceptions(excs, "WM1") == ["EXC-1"]
    assert playbook_manifests([mnf], "WM1") == ["MNF-1"]

    pb = build_playbook(st, tasks, excs, [mnf], dl)
    assert playbook_to_record(pb)["type"] == "store_playbook"
    assert playbook_summary([pb])["total_tasks"] == 1
