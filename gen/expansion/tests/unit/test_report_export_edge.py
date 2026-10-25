"""Edge tests for recallstorm.report.export."""
from recallstorm.report.export import export_csv


def test_export_empty_csv(tmp_path):
    assert export_csv([], "shelf_task", tmp_path / "empty.csv") == 0
