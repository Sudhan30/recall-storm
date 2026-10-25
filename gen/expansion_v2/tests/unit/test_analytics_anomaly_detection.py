"""Unit tests for recallstorm.analytics.anomaly_detection."""
from recallstorm.analytics.anomaly_detection import (
    FraudAndErrorFlag,
    PullScanAnomalyDetector,
    alert_on_after_hours_quarantine_bin_access,
    compare_sister_store_pull_ratios_by_cluster,
    detect_coordinated_multi_store_scan_gaps,
    detect_impossible_speed_pencil_whipping,
    flag_zero_unit_found_in_high_on_hand_store,
    identify_unusual_post_lock_pos_override_scans,
    isolate_handheld_scanner_clock_drift_errors,
    route_flagged_anomalies_to_audit_queue,
    score_store_submission_credibility_index,
    spot_outlier_destruction_weight_variances,
)


def test_anomaly_detection():
    assert PullScanAnomalyDetector().status == "ACTIVE"
    assert FraudAndErrorFlag().status == "ACTIVE"
    assert detect_impossible_speed_pencil_whipping(10, 15.0)["pencil_whipped"] is True
    assert flag_zero_unit_found_in_high_on_hand_store(36, 0, 24)["anomaly"] is True
    assert identify_unusual_post_lock_pos_override_scans("WM1", 2)["missed_shelf_stock"] is True
    assert spot_outlier_destruction_weight_variances(100.0, 50.0, 0.15)["outlier"] is True
    assert detect_coordinated_multi_store_scan_gaps(["WM1", "WM2", "WM3"], "D01")["systemic_gap"] is True
    assert alert_on_after_hours_quarantine_bin_access("WM1", 2, False)["alert"] is True
    assert compare_sister_store_pull_ratios_by_cluster(0.1, 0.85)["deviant"] is True
    assert isolate_handheld_scanner_clock_drift_errors(120.0, 60.0)["clock_drifted"] is True
    assert score_store_submission_credibility_index(2) == 50.0
    assert route_flagged_anomalies_to_audit_queue(["WM2", "WM1"]) == ["WM1", "WM2"]
