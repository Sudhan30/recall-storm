"""Property tests for recallstorm.report.export."""
from recallstorm.report.export import export_index


def test_export_index_conservation():
    recs = [{"type": "shelf_task"} for _ in range(10)] + [{"type": "evidence"} for _ in range(5)]
    idx = export_index(recs)
    assert sum(idx["by_type"].values()) == idx["total_records"] == 15
