"""Unit tests for recallstorm.report.summary."""
from recallstorm.report.summary import (
    SummaryReport,
    compare_runs,
    counts_by_action,
    counts_by_verdict,
    drill_summary,
    sku_table,
    store_table,
    summary_to_json,
    summary_to_markdown,
)


def test_summary_reporting():
    recs = [
        {"type": "run", "run_id": "RUN-1", "scenario_id": "ca_red3"},
        {"type": "sku_verdict", "sku_id": "S1", "gtin": "00012345678905", "verdict": "PULL", "additive": "RED3", "rule_ids": ["R1"]},
        {"type": "sku_verdict", "sku_id": "S2", "gtin": "00012345678912", "verdict": "KEEP", "additive": None, "rule_ids": []},
        {"type": "shelf_task", "task_id": "T1", "action": "PULL"},
        {"type": "store_playbook", "store_id": "WM1", "format": "SUPERCENTER", "deadline": "2027-01-01", "counts": {"total_tasks": 1}, "associate_ids": ["A1"], "exception_ids": []},
    ]
    assert counts_by_verdict(recs)["PULL"] == 1
    assert counts_by_action(recs)["PULL"] == 1
    assert len(store_table(recs)) == 1
    assert len(sku_table(recs)) == 1
    s = drill_summary(recs)
    assert s["stores"] == 1
    md = summary_to_markdown(s)
    assert "# Recall Storm Drill Summary" in md
    assert "RUN-1" in summary_to_json(s)
    assert compare_runs(recs, recs)["pull_delta"] == 0
    sr = SummaryReport("RUN-1", s["verdicts"], s["actions"], 1)
    assert sr.store_count == 1
