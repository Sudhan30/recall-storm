"""Unit tests for recallstorm.governance.policy_versioning."""
from recallstorm.governance.policy_versioning import (
    PolicyDiffTracker,
    StandardOperatingProcedureGit,
    audit_policy_exception_waiver_expirations,
    bind_drill_execution_to_immutable_policy_sha,
    diff_rule_engine_thresholds_between_drills,
    generate_regulatory_change_management_log,
    manage_annual_sop_recertification_cycles,
    publish_redlined_policy_updates_to_field,
    require_legal_review_on_jurisdiction_rules,
    roll_back_erroneous_rule_configuration_push,
    track_effective_dates_of_state_ban_modules,
    version_control_recall_playbook_markdown,
)


def test_policy_versioning():
    assert StandardOperatingProcedureGit().status == "ACTIVE"
    assert PolicyDiffTracker().status == "ACTIVE"
    sha = version_control_recall_playbook_markdown("# Playbook v1")
    assert len(sha) == 12
    assert require_legal_review_on_jurisdiction_rules("CA_AB418_RED3", "COUNSEL1")["approved_by"] == "COUNSEL1"
    assert track_effective_dates_of_state_ban_modules({"ca": "2027-01-01"})["CA"] == "2027-01-01"
    diff = diff_rule_engine_thresholds_between_drills({"VOC": 30.0}, {"VOC": 25.0})
    assert diff["VOC"] == (30.0, 25.0)
    assert bind_drill_execution_to_immutable_policy_sha("RUN1", sha)["policy_sha"] == sha
    assert manage_annual_sop_recertification_cycles("SOP1", 14)["recert_due"] is True
    assert publish_redlined_policy_updates_to_field("SOP1", "Added Red 3")["sop_id"] == "SOP1"
    assert roll_back_erroneous_rule_configuration_push(sha)["rolled_back_to"] == sha
    assert audit_policy_exception_waiver_expirations([{"waiver_id": "W1", "expires": "2026-01-01"}], "2026-12-30") == ["W1"]
    assert generate_regulatory_change_management_log(["C1"])["change_count"] == 1
