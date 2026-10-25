"""Unit tests for recallstorm.governance.board_reporting."""
from recallstorm.governance.board_reporting import (
    FiduciaryOversightBrief,
    RiskCommitteePackage,
    archive_signed_board_resolution_minutes,
    benchmark_compliance_maturity_against_peers,
    compile_quarterly_enterprise_recall_summary,
    document_crisis_simulation_readiness_scores,
    highlight_supply_chain_single_point_failures,
    provide_directors_and_officers_liability_view,
    quantify_unmitigated_state_ban_exposures,
    report_material_fda_warning_letter_risks,
    summarize_whistleblower_and_audit_exceptions,
    track_capex_investment_in_esl_and_epcis,
)


def test_board_reporting():
    assert RiskCommitteePackage().status == "ACTIVE"
    assert FiduciaryOversightBrief().status == "ACTIVE"
    assert compile_quarterly_enterprise_recall_summary("2026-Q4", 4, 98.5)["recalls"] == 4
    assert quantify_unmitigated_state_ban_exposures(10, 50000.0) == 500000.0
    assert report_material_fda_warning_letter_risks(1)["material_risk"] is True
    assert summarize_whistleblower_and_audit_exceptions(3, 1)["tips"] == 3
    assert benchmark_compliance_maturity_against_peers(94.0, 85.0)["outperforming"] is True
    assert track_capex_investment_in_esl_and_epcis(12.5, 4.5) == 17.0
    assert highlight_supply_chain_single_point_failures(2)["action_required"] is True
    assert document_crisis_simulation_readiness_scores(6, 96.0)["drills_run"] == 6
    assert provide_directors_and_officers_liability_view(True)["caremark_compliant"] is True
    assert archive_signed_board_resolution_minutes("RES1", "2026-Q4")["resolution_id"] == "RES1"
