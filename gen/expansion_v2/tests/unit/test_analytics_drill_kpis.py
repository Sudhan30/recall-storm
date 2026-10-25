"""Unit tests for recallstorm.analytics.drill_kpis."""
from recallstorm.analytics.drill_kpis import (
    DrillScorecardEngine,
    SlaPerformanceTracker,
    benchmark_division_vs_company_avg_speed,
    calculate_labor_hours_variance_to_plan,
    calculate_time_to_first_store_scan_mins,
    compute_lot_capture_accuracy_precision,
    evaluate_backroom_vs_salesfloor_miss_rate,
    export_board_level_compliance_kpi_deck,
    generate_executive_drill_grade_letter,
    measure_four_hour_completion_rate_pct,
    score_pos_block_deployment_latency_secs,
    track_false_positive_unaffected_pull_rate,
)


def test_drill_kpis():
    assert DrillScorecardEngine().status == "ACTIVE"
    assert SlaPerformanceTracker().status == "ACTIVE"
    assert calculate_time_to_first_store_scan_mins(0.0, 6.5) == 6.5
    assert measure_four_hour_completion_rate_pct(49, 50) == 98.0
    assert compute_lot_capture_accuracy_precision(90, 10) == 0.9
    assert score_pos_block_deployment_latency_secs(12.0, 30.0)["met_target"] is True
    assert benchmark_division_vs_company_avg_speed(95.0, 110.0) == -15.0
    assert track_false_positive_unaffected_pull_rate(5, 100) == 0.05
    assert evaluate_backroom_vs_salesfloor_miss_rate(4, 1)["backroom_higher"] is True
    assert calculate_labor_hours_variance_to_plan(42.0, 40.0) == 2.0
    assert generate_executive_drill_grade_letter(98.5) == "A"
    assert export_board_level_compliance_kpi_deck("DR1", "A")["grade"] == "A"
