"""Edge tests for recallstorm.report.dashboard."""
from recallstorm.report.dashboard import dashboard_data, dashboard_html


def test_dashboard_empty():
    d = dashboard_data([], [], [])
    assert len(d["kpis"]) == 4
    assert "Recall Storm" in dashboard_html(d)
