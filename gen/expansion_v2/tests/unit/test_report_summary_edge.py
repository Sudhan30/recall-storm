"""Edge case tests for recallstorm.report.summary."""
from recallstorm.report.summary import drill_summary


def test_report_summary_edge():
    s = drill_summary([])
    assert s["run_id"] == "UNKNOWN" and s["stores"] == 0
