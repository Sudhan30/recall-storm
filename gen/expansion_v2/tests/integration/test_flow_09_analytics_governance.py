"""Integration test 09: core -> labor -> sim -> analytics -> governance."""
from recallstorm.analytics.drill_kpis import (
    generate_executive_drill_grade_letter,
    measure_four_hour_completion_rate_pct,
)
from recallstorm.core.ids import make_run_id
from recallstorm.governance.approvals_workflow import enforce_dual_control_on_chainwide_pulls
from recallstorm.governance.audit_evidence_packs import compute_sha256_merkle_root_for_evidence
from recallstorm.labor.estimates import pull_minutes
from recallstorm.sim.events import DoneEvent, event_to_record
from recallstorm.sim.metrics import tasks_done_by


def test_flow_analytics_and_governance():
    run_id = make_run_id("ca_red3", "2026-12-30T18:00:00-08:00")
    assert pull_minutes(12) == 3.2
    ev = event_to_record(DoneEvent("2026-12-30T22:30:00-08:00", "WM1", "A1", {"aisle": "A01"}, "T1"))
    assert tasks_done_by([ev], "2026-12-31T00:00:00-08:00") == 1
    pct = measure_four_hour_completion_rate_pct(50, 50)
    assert generate_executive_drill_grade_letter(pct) == "A"
    assert enforce_dual_control_on_chainwide_pulls("VP_QA", "VP_OPS")["dual_control_met"] is True
    root = compute_sha256_merkle_root_for_evidence([run_id, ev["task_id"]])
    assert len(root) == 16
