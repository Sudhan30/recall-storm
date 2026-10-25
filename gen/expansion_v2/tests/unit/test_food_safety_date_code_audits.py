"""Unit tests for recallstorm.food_safety.date_code_audits."""
from recallstorm.food_safety.date_code_audits import (
    ExpiredStockSweep,
    RotationComplianceAudit,
    calculate_close_dated_shrink_risk,
    check_otc_drug_expiration_window,
    export_expired_pull_log,
    flag_fifo_rotation_violations,
    generate_random_aisle_date_walk,
    identify_chronic_overstock_skus,
    schedule_markdown_before_expiry,
    score_department_freshness_index,
    track_associate_rotation_velocity,
    verify_infant_formula_hard_pull,
)


def test_date_code_audits():
    assert RotationComplianceAudit().status == "ACTIVE"
    assert ExpiredStockSweep().status == "ACTIVE"
    assert generate_random_aisle_date_walk("WM1", ["A02", "A01"])["aisles"] == ["A01", "A02"]
    assert calculate_close_dated_shrink_risk(10, 5.0, 0) == 50.0
    assert flag_fifo_rotation_violations("2027-02-01", "2027-01-10")["violation"] is True
    assert verify_infant_formula_hard_pull("INF1", "2026-12-01", "2026-12-30")["pull_immediately"] is True
    assert check_otc_drug_expiration_window("OTC1", 10, 30)["pull"] is True
    assert score_department_freshness_index(100, 5) == 95.0
    assert identify_chronic_overstock_skus({"S1": 45, "S2": 10}, 30) == ["S1"]
    assert schedule_markdown_before_expiry("S1", 2)["cvp_eligible"] is True
    assert track_associate_rotation_velocity("A1", 30, 10.0) == 3.0
    assert export_expired_pull_log("WM1", 12)["pulled_units"] == 12
