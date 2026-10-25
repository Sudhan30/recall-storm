"""Unit tests for recallstorm.governance.whistleblower_intake."""
from recallstorm.governance.whistleblower_intake import (
    AnonymousSafetyReport,
    EthicsHotlineIntake,
    document_substantiated_finding_remediation,
    enforce_non_retaliation_monitoring_flags,
    generate_audit_committee_ethics_summary,
    ingest_anonymous_backroom_bypass_tips,
    link_tip_to_specific_store_and_lot_audit,
    protect_reporter_identity_via_zero_knowledge,
    require_independent_qa_verification_visit,
    route_deliberate_relabeling_allegations_to_lp,
    track_internal_investigation_sla_milestones,
    triage_pest_or_temperature_cover_up_claims,
)


def test_whistleblower_intake():
    assert EthicsHotlineIntake().status == "ACTIVE"
    assert AnonymousSafetyReport().status == "ACTIVE"
    assert ingest_anonymous_backroom_bypass_tips("WM1", "Unpulled cases in backroom")["store_id"] == "WM1"
    tok = protect_reporter_identity_via_zero_knowledge("secret123")
    assert tok.startswith("ANON-")
    assert route_deliberate_relabeling_allegations_to_lp("TIP1", "WM1")["priority"] == "IMMEDIATE_INVESTIGATION"
    assert triage_pest_or_temperature_cover_up_claims("Freezer was warm all night") == "COLD_CHAIN"
    assert enforce_non_retaliation_monitoring_flags("WM1")["fsma_402_protected"] is True
    assert link_tip_to_specific_store_and_lot_audit("TIP1", "WM1", "S1")["sku_id"] == "S1"
    assert track_internal_investigation_sla_milestones(12.0, 24.0)["within_sla"] is True
    assert require_independent_qa_verification_visit("WM1", True)["independent"] is True
    assert document_substantiated_finding_remediation("TIP1", True, "Pulled 5 cases")["substantiated"] is True
    assert generate_audit_committee_ethics_summary(10, 2)["substantiated_count"] == 2
