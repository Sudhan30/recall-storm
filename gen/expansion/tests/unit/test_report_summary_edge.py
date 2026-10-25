"""Edge tests for recallstorm.report.summary."""
from recallstorm.report.summary import drill_summary


def test_summary_empty():
    s = drill_summary([])
    assert s["stores"] == 0
    assert s["verdicts"]["PULL"] == 0
