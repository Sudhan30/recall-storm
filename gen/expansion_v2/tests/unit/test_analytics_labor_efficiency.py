"""Unit tests for recallstorm.analytics.labor_efficiency."""
from recallstorm.analytics.labor_efficiency import (
    MotionWasteEvaluator,
    PullProductivityAnalyzer,
    benchmark_floater_vs_store_associate_speed,
    calculate_units_pulled_per_labor_minute,
    calibrate_task_time_standards_by_category,
    compare_actual_walk_path_to_optimal_tour,
    evaluate_batch_multi_recall_walk_synergy,
    export_engineered_labor_standard_updates,
    identify_ergonomic_fatigue_drop_off_curves,
    measure_lot_inspection_dwell_time_by_pkg,
    optimize_two_person_team_cage_transport,
    quantify_backroom_search_time_penalty,
)


def test_labor_efficiency():
    assert PullProductivityAnalyzer().status == "ACTIVE"
    assert MotionWasteEvaluator().status == "ACTIVE"
    assert calculate_units_pulled_per_labor_minute(30, 10.0) == 3.0
    assert compare_actual_walk_path_to_optimal_tour(250.0, 200.0)["efficiency"] == 0.8
    assert measure_lot_inspection_dwell_time_by_pkg("embossed can") == 8.5
    assert evaluate_batch_multi_recall_walk_synergy(40.0, 25.0) == 15.0
    assert quantify_backroom_search_time_penalty(4, 3.5) == 14.0
    assert benchmark_floater_vs_store_associate_speed(4.5, 3.5)["floater_advantage"] == 1.0
    assert identify_ergonomic_fatigue_drop_off_curves(6.0) == 0.9
    assert optimize_two_person_team_cage_transport(25, 20)["two_person_team"] is True
    assert calibrate_task_time_standards_by_category(10.0, 10.0) == 10.0
    assert export_engineered_labor_standard_updates({"candy": 3.0})["categories"] == 1
