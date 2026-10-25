"""Unit tests for recallstorm.analytics.simulation_calibration."""
from recallstorm.analytics.simulation_calibration import (
    DigitalTwinCalibrator,
    SimToRealGapAnalyzer,
    backtest_simulator_against_historical_recalls,
    calibrate_customer_basket_pick_interference,
    compare_simulated_walk_times_to_rf_scans,
    detect_store_layout_drift_from_cad_files,
    fit_lot_inspection_time_distributions,
    measure_disruption_model_prediction_error,
    publish_calibrated_sim_parameter_bundle,
    tune_backroom_clutter_delay_multipliers,
    update_monte_carlo_prior_probabilities,
    validate_truck_loading_cube_utilization_sim,
)


def test_simulation_calibration():
    assert DigitalTwinCalibrator().status == "ACTIVE"
    assert SimToRealGapAnalyzer().status == "ACTIVE"
    assert compare_simulated_walk_times_to_rf_scans(100.0, 110.0)["error_pct"] == 0.1
    assert fit_lot_inspection_time_distributions([4.0, 6.0])["mean_sec"] == 5.0
    assert calibrate_customer_basket_pick_interference(2.0) == 1.5
    assert tune_backroom_clutter_delay_multipliers(90.0) == 1.5
    assert validate_truck_loading_cube_utilization_sim(800.0, 10, 85.0)["actual_cube_ft3"] == 850.0
    assert measure_disruption_model_prediction_error(90.0, 100.0) == 0.1
    assert 0.0 <= update_monte_carlo_prior_probabilities(0.5, 0.8) <= 1.0
    assert backtest_simulator_against_historical_recalls(5)["passed"] is True
    assert detect_store_layout_drift_from_cad_files("WM1563", 1)["drifted"] is True
    assert publish_calibrated_sim_parameter_bundle("v1.1", 1.2)["version"] == "v1.1"
