"""Depletion curve forecasting and financial write-off range projection."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallExposureForecaster:
    """Forecaster for remaining shelf units and customer consumption exposure."""

    ref_id: str = "FRC-EXP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DepletionCurvePredictor:
    """Time-of-day POS basket depletion curve predictor."""

    ref_id: str = "FRC-DEP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def forecast_remaining_shelf_units_at_hour_t(initial_units: int, hours: float, hourly_rate: float = 1.5) -> int:
    """Forecast remaining shelf units after hours of customer sales."""
    if initial_units < 0 or hours < 0 or hourly_rate < 0:
        raise DataValidationError("Negative forecast inputs")
    return max(0, int(round(initial_units - hours * hourly_rate)))


def model_time_of_day_pos_basket_velocity(hour_24: int) -> float:
    """Return relative POS checkout velocity multiplier by hour of day (0..23)."""
    if not isinstance(hour_24, int) or not (0 <= hour_24 <= 23):
        raise DataValidationError("hour_24 must be in 0..23")
    if 16 <= hour_24 <= 19:
        return 2.0  # Evening rush
    if 0 <= hour_24 <= 5:
        return 0.1  # Overnight
    return 1.0


def estimate_customer_pantry_consumption_risk(units_sold: int, days_since_sale: int, shelf_life_days: int = 30) -> int:
    """Estimate how many purchased units remain unconsumed in customer pantries."""
    if units_sold < 0 or days_since_sale < 0 or shelf_life_days <= 0:
        raise DataValidationError("Invalid pantry consumption inputs")
    frac_left = max(0.0, 1.0 - (days_since_sale / shelf_life_days))
    return int(round(units_sold * frac_left))


def predict_quarantine_cage_overflow_by_store(pulled_cube_ft3: float, cage_capacity_ft3: float = 150.0) -> dict:
    """Predict whether a store's backroom quarantine cage will overflow."""
    if pulled_cube_ft3 < 0 or cage_capacity_ft3 <= 0:
        raise DataValidationError("Invalid cube values")
    return {"op": "predict_quarantine_cage_overflow_by_store", "overflow": pulled_cube_ft3 > cage_capacity_ft3, "excess_ft3": round(max(0.0, pulled_cube_ft3 - cage_capacity_ft3), 2), "src": "recallstorm/analytics/forecasting_exposure.py"}


def project_total_financial_write_off_range(min_units: int, max_units: int, unit_cost: float) -> tuple[float, float]:
    """Project (min_usd, max_usd) write-off range."""
    if min_units < 0 or max_units < min_units or unit_cost < 0:
        raise DataValidationError("Invalid write-off range inputs")
    return (round(min_units * unit_cost, 2), round(max_units * unit_cost, 2))


def simulate_delayed_notice_exposure_penalty(delay_hours: float, units_per_hour: float = 20.0) -> int:
    """Estimate additional recalled units sold to consumers due to a delay_hours lag in POS lock."""
    if delay_hours < 0 or units_per_hour < 0:
        raise DataValidationError("Negative delay or rate")
    return int(round(delay_hours * units_per_hour))


def calculate_substitute_stockout_runout_date(sub_cases: int, daily_demand_cases: float) -> int:
    """Return days of supply before substitute stock runs out."""
    if sub_cases < 0 or daily_demand_cases <= 0:
        raise DataValidationError("Invalid substitute cases or demand")
    return int(sub_cases // daily_demand_cases)


def bound_confidence_interval_on_untracked_lots(point_est: float, margin_pct: float = 0.15) -> tuple[float, float]:
    """Return (lower, upper) bounds around point_est."""
    if point_est < 0 or not (0.0 <= margin_pct <= 1.0):
        raise DataValidationError("Invalid point_est or margin_pct")
    return (round(point_est * (1.0 - margin_pct), 2), round(point_est * (1.0 + margin_pct), 2))


def adjust_forecast_for_holiday_promotional_lift(base_demand: float, holiday_lift: float = 1.5) -> float:
    """Scale demand forecast by seasonal/holiday promotional lift."""
    if base_demand < 0 or holiday_lift <= 0:
        raise DataValidationError("Invalid demand or lift")
    return round(base_demand * holiday_lift, 2)


def feed_exposure_estimate_to_reserve_accrual(recall_id: str, midpoint_usd: float) -> dict:
    """Feed midpoint financial exposure into accounting reserve accrual."""
    _req(recall_id, "recall_id")
    if midpoint_usd < 0:
        raise DataValidationError("midpoint_usd cannot be negative")
    return {"op": "feed_exposure_estimate_to_reserve_accrual", "recall_id": str(recall_id), "midpoint_usd": round(float(midpoint_usd), 2), "src": "recallstorm/analytics/forecasting_exposure.py"}
