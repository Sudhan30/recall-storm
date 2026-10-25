"""Unit tests for recallstorm.governance.access_logs."""
from recallstorm.governance.access_logs import (
    PrivilegedAccessLogger,
    RbacPolicyEnforcer,
    alert_infosec_on_permission_escalation_try,
    archive_quarterly_access_entitlement_review,
    audit_third_party_auditor_portal_sessions,
    detect_anomalous_bulk_export_of_vendor_lists,
    enforce_role_based_access_to_pos_kill_switch,
    generate_siem_compatible_cef_security_logs,
    log_every_view_of_unredacted_recall_drafts,
    require_mfa_step_up_for_hold_release_action,
    revoke_terminated_associate_drill_credentials,
    track_impersonation_support_session_actions,
)


def test_access_logs():
    assert PrivilegedAccessLogger().status == "ACTIVE"
    assert RbacPolicyEnforcer().status == "ACTIVE"
    assert log_every_view_of_unredacted_recall_drafts("U1", "DRF1")["logged"] is True
    assert enforce_role_based_access_to_pos_kill_switch("VP_FOOD_SAFETY")["allowed"] is True
    assert enforce_role_based_access_to_pos_kill_switch("VENDOR_REP")["allowed"] is False
    assert detect_anomalous_bulk_export_of_vendor_lists(1000, 500)["dlp_alert"] is True
    assert require_mfa_step_up_for_hold_release_action("U1", True)["allowed"] is True
    assert audit_third_party_auditor_portal_sessions("AUD1", ["WM1"])["stores"] == ["WM1"]
    assert track_impersonation_support_session_actions("IT1", "WM1", "INC1")["ticket_id"] == "INC1"
    assert revoke_terminated_associate_drill_credentials({"A1"}, {"A1", "A2"}) == ["A2"]
    assert generate_siem_compatible_cef_security_logs("POS_LOCK", "VP1", 8).startswith("CEF:0|RecallStorm")
    assert alert_infosec_on_permission_escalation_try("U1", "UNLOCK")["alert_sent"] is True
    assert archive_quarterly_access_entitlement_review("2026-Q4", 45)["reviewed_users"] == 45
