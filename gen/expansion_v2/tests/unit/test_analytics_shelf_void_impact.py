"""Unit tests for recallstorm.analytics.shelf_void_impact."""
from recallstorm.analytics.shelf_void_impact import (
    OutOfStockDurationTracker,
    SubstituteCaptureRate,
    calculate_substitute_sku_sales_halo_lift,
    correlate_void_duration_with_nps_drop,
    evaluate_emergency_re_planogram_compliance,
    export_merchandising_recovery_scorecard,
    identify_orphaned_shelf_tags_without_stock,
    measure_days_of_empty_facing_post_pull,
    quantify_category_switching_walk_away_rate,
    recommend_safety_stock_buffer_adjustments,
    score_dc_emergency_allocation_fill_rate,
    track_time_to_replenish_with_clean_lot,
)


def test_shelf_void_impact():
    assert OutOfStockDurationTracker().status == "ACTIVE"
    assert SubstituteCaptureRate().status == "ACTIVE"
    assert measure_days_of_empty_facing_post_pull(1, 4) == 3
    assert calculate_substitute_sku_sales_halo_lift(100, 160) == 60.0
    assert quantify_category_switching_walk_away_rate(100, 75) == 0.25
    assert track_time_to_replenish_with_clean_lot(24.0, 48.0)["met_target"] is True
    assert evaluate_emergency_re_planogram_compliance(45, 50) == 90.0
    assert identify_orphaned_shelf_tags_without_stock([{"sku_id": "S1", "on_hand": 0, "has_po": False}]) == ["S1"]
    assert correlate_void_duration_with_nps_drop(10) == 4.0
    assert score_dc_emergency_allocation_fill_rate(80, 100) == 0.8
    assert recommend_safety_stock_buffer_adjustments("SUB1", 10, 1.5)["new_buffer_cases"] == 15
    assert export_merchandising_recovery_scorecard("baking", 0.85)["fill_rate"] == 0.85
