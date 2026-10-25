"""Unit tests for recallstorm.report.summary."""
from recallstorm.plan.assemble import assemble_plan
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
from tests.unit.test_plan_assemble import _sample_pack


def test_report_summary():
    pack = _sample_pack()
    sc = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    recs = assemble_plan(pack, sc)
    summ = drill_summary(recs)
    assert summ["verdicts"]["PULL"] == 1
    assert counts_by_verdict(recs)["KEEP"] == 1
    assert counts_by_action(recs)["PULL"] == 1
    assert len(sku_table(recs)) == 2
    assert len(store_table(recs)) == 1
    assert "# Recall Storm Drill Summary" in summary_to_markdown(summ)
    assert "ca_red3" in summary_to_json(summ)
    assert compare_runs(recs, recs)["pull_delta"] == 0
    sr = SummaryReport(summ["run_id"], summ["verdicts"], summ["actions"], summ["stores"])
    assert sr.store_count == 1
