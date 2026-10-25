"""Edge case tests for recallstorm.report.export."""
from recallstorm.report.export import export_csv, export_index


def test_report_export_edge(tmp_path):
    assert export_csv([], str(tmp_path / "empty.csv")) == 0
    assert export_index([])["total_records"] == 0
