"""Unit tests for recallstorm.analytics.root_cause_mining."""
from recallstorm.analytics.root_cause_mining import (
    FailureModeClassifier,
    PostMortemTextMiner,
    attribute_misses_to_planogram_unmapped_locs,
    cluster_store_exception_reason_codes,
    correlate_missed_pulls_with_night_crew_gaps,
    extract_themes_from_manager_delay_notes,
    generate_capa_preventive_action_tickets,
    identify_pos_sync_failures_by_isp_carrier,
    measure_impact_of_unreadable_lot_stamps,
    quantify_dsd_endcap_blind_spot_frequency,
    rank_top_ten_systemic_execution_barriers,
    validate_fix_efficacy_in_subsequent_drills,
)


def test_root_cause_mining():
    assert FailureModeClassifier().status == "ACTIVE"
    assert PostMortemTextMiner().status == "ACTIVE"
    assert cluster_store_exception_reason_codes([{"kind": "TOPSTOCK"}, {"kind": "TOPSTOCK"}])["TOPSTOCK"] == 2
    assert "PLANOGRAM_DRIFT" in extract_themes_from_manager_delay_notes(["Aisle moved during remodel"])
    assert attribute_misses_to_planogram_unmapped_locs(6, 10) == 0.6
    assert quantify_dsd_endcap_blind_spot_frequency(4, 20) == 0.2
    assert measure_impact_of_unreadable_lot_stamps(2, 20) == 0.1
    assert correlate_missed_pulls_with_night_crew_gaps({"WM1", "WM2"}, {"WM1"}) == 1.0
    assert identify_pos_sync_failures_by_isp_carrier({"ISP_A": 1, "ISP_B": 5}) == "ISP_B"
    assert rank_top_ten_systemic_execution_barriers({"B1": 2, "B2": 9}) == ["B2", "B1"]
    assert generate_capa_preventive_action_tickets("TOPSTOCK")["barrier"] == "TOPSTOCK"
    assert validate_fix_efficacy_in_subsequent_drills(10, 2)["effective"] is True
