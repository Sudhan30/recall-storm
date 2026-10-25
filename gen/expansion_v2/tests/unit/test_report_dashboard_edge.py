"""Edge case tests for recallstorm.report.dashboard."""
from recallstorm.report.dashboard import dashboard_data


def test_report_dashboard_edge():
    m = dashboard_data([], [], [])
    assert m.points == [] and m.timeline == []
