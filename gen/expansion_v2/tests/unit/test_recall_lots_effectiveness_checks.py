"""Unit tests for recallstorm.recall_lots.effectiveness_checks."""
from recallstorm.recall_lots.effectiveness_checks import (
    EdcResponseCompiler,
    EffectivenessCheckQuestionnaire,
    audit_sub_account_notification_logs,
    build_fda_district_status_report,
    calculate_effectiveness_completion_pct,
    compile_affidavit_return_counts,
    flag_non_responding_locations,
    generate_store_verification_survey,
    score_check_timeliness_sla,
    select_fda_level_a_through_e_sample,
    trigger_recheck_for_discrepancies,
    verify_physical_destruction_photos,
)


def test_effectiveness_checks():
    assert EffectivenessCheckQuestionnaire().status == "ACTIVE"
    assert EdcResponseCompiler().status == "ACTIVE"
    stores = ["WM1", "WM2", "WM3", "WM4"]
    assert len(select_fda_level_a_through_e_sample("A", stores)) == 4
    assert len(select_fda_level_a_through_e_sample("B", stores)) == 2
    assert select_fda_level_a_through_e_sample("E", stores) == []
    assert generate_store_verification_survey("WM1", "R1")["store_id"] == "WM1"
    assert calculate_effectiveness_completion_pct(3, 4) == 75.0
    assert flag_non_responding_locations(stores, {"WM1", "WM2", "WM3"}) == ["WM4"]
    assert compile_affidavit_return_counts([{"units": 5}, {"units": 7}]) == 12
    assert verify_physical_destruction_photos("WM1", ["hash1"])["verified"] is True
    assert audit_sub_account_notification_logs("ACC1", True)["notified"] is True
    assert score_check_timeliness_sla(12.0, 24.0)["within_sla"] is True
    assert build_fda_district_status_report("R1", 100.0)["completion_pct"] == 100.0
    assert trigger_recheck_for_discrepancies("WM1", 5)["recheck"] is True
