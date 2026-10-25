"""Unit tests for recallstorm.analytics.forecasting_exposure."""
from recallstorm.analytics.forecasting_exposure import (
    DepletionCurvePredictor,
    RecallExposureForecaster,
    adjust_forecast_for_holiday_promotional_lift,
    bound_confidence_interval_on_untracked_lots,
    calculate_substitute_stockout_runout_date,
    estimate_customer_pantry_consumption_risk,
    feed_exposure_estimate_to_reserve_accrual,
    forecast_remaining_shelf_units_at_hour_t,
    model_time_of_day_pos_basket_velocity,
    predict_quarantine_cage_overflow_by_store,
    project_total_financial_write_off_range,
    simulate_delayed_notice_exposure_penalty,
)


def test_forecasting_exposure():
    assert RecallExposureForecaster().status == "ACTIVE"
    assert DepletionCurvePredictor().status == "ACTIVE"
    assert forecast_remaining_shelf_units_at_hour_t(20, 4.0, 2.0) == 12
    assert model_time_of_day_pos_basket_velocity(17) == 2.0
    assert estimate_customer_pantry_consumption_risk(100, 15, 30) == 50
    assert predict_quarantine_cage_overflow_by_store(200.0, 150.0)["overflow"] is True
    assert project_total_financial_write_off_range(10, 20, 5.0) == (50.0, 100.0)
    assert simulate_delayed_notice_exposure_penalty(2.5, 20.0) == 50
    assert calculate_substitute_stockout_runout_date(30, 5.0) == 6
    assert bound_confidence_interval_on_untracked_lots(100.0, 0.15) == (85.0, 115.0)
    assert adjust_forecast_for_holiday_promotional_lift(100.0, 1.5) == 150.0
    assert feed_exposure_estimate_to_reserve_accrual("R1", 5000.0)["midpoint_usd"] == 5000.0
