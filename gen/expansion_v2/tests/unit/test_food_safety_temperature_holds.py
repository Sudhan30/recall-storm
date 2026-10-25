"""Unit tests for recallstorm.food_safety.temperature_holds."""
from recallstorm.food_safety.temperature_holds import (
    ColdChainExcursionLog,
    TimeTempAbuseEvaluator,
    assess_frozen_thaw_refreeze_risk,
    authorize_disposition_after_review,
    calculate_cumulative_degree_minutes,
    evaluate_fda_tcs_four_hour_rule,
    flag_defrost_cycle_anomalies,
    generate_temp_hold_pallet_tags,
    map_multi_deck_case_zones,
    parse_reefer_data_logger_csv,
    trigger_cooler_failure_quarantine,
    validate_probe_calibration_status,
)


def test_temperature_holds():
    assert ColdChainExcursionLog().status == "ACTIVE"
    assert TimeTempAbuseEvaluator().status == "ACTIVE"
    temps = parse_reefer_data_logger_csv("38.0, 43.0, 45.0")
    assert len(temps) == 3
    assert calculate_cumulative_degree_minutes(temps, 41.0, 15.0) == 90.0
    assert evaluate_fda_tcs_four_hour_rule(250.0, 48.0)["discard"] is True
    assert flag_defrost_cycle_anomalies(60.0, 45.0)["anomaly"] is True
    assert trigger_cooler_failure_quarantine("WM1", "C1")["status"] == "QUARANTINED"
    assert assess_frozen_thaw_refreeze_risk(True, 20.0)["adulterated"] is True
    assert len(map_multi_deck_case_zones("C1", 3)) == 3
    assert len(generate_temp_hold_pallet_tags("DC1", 2)) == 2
    assert validate_probe_calibration_status("P1", 32.4)["calibrated"] is True
    assert authorize_disposition_after_review("H1", "DESTROY")["verdict"] == "DESTROY"
