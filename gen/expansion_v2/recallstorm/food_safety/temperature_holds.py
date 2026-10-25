"""Cold chain excursion logging and FDA Food Code 4-hour TCS evaluation."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ColdChainExcursionLog:
    """Log of reefer or display case cold-chain temperature excursions."""

    ref_id: str = "TEMP-LOG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class TimeTempAbuseEvaluator:
    """Evaluator for FDA Food Code TCS (Time/Temperature Control for Safety) limits."""

    ref_id: str = "TEMP-TCS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def parse_reefer_data_logger_csv(csv_text: str) -> list[float]:
    """Parse comma-separated temperature readings in Fahrenheit from a reefer logger."""
    _req(csv_text, "csv_text")
    out: list[float] = []
    for tok in str(csv_text).replace("\n", ",").split(","):
        s = tok.strip()
        if s:
            try:
                out.append(float(s))
            except ValueError as exc:
                raise DataValidationError(f"Non-numeric temp reading: {s!r}") from exc
    return out


def calculate_cumulative_degree_minutes(temps_f: list[float], max_safe_f: float = 41.0, interval_mins: float = 15.0) -> float:
    """Calculate cumulative degree-minutes above max_safe_f."""
    if not temps_f or interval_mins <= 0:
        raise DataValidationError("Invalid temps_f or interval_mins")
    deg_mins = sum(max(0.0, t - max_safe_f) * interval_mins for t in temps_f)
    return round(deg_mins, 2)


def evaluate_fda_tcs_four_hour_rule(minutes_above_41f: float, max_temp_f: float = 50.0) -> dict:
    """Evaluate FDA Food Code 4-hour (240 min) / 70F TCS discard rule."""
    if minutes_above_41f < 0:
        raise DataValidationError("minutes_above_41f cannot be negative")
    discard = minutes_above_41f >= 240.0 or max_temp_f >= 70.0
    return {"op": "evaluate_fda_tcs_four_hour_rule", "discard": discard, "minutes": float(minutes_above_41f), "src": "recallstorm/food_safety/temperature_holds.py"}


def flag_defrost_cycle_anomalies(duration_mins: float, max_defrost_mins: float = 45.0) -> dict:
    """Flag abnormal cooler defrost cycles exceeding max_defrost_mins."""
    if duration_mins < 0 or max_defrost_mins <= 0:
        raise DataValidationError("Invalid defrost duration")
    return {"op": "flag_defrost_cycle_anomalies", "anomaly": duration_mins > max_defrost_mins, "src": "recallstorm/food_safety/temperature_holds.py"}


def trigger_cooler_failure_quarantine(store_id: str, case_id: str) -> dict:
    """Trigger an emergency quarantine for a failed refrigerated display case."""
    _req(store_id, "store_id")
    _req(case_id, "case_id")
    return {"op": "trigger_cooler_failure_quarantine", "store_id": str(store_id), "case_id": str(case_id), "status": "QUARANTINED", "src": "recallstorm/food_safety/temperature_holds.py"}


def assess_frozen_thaw_refreeze_risk(ice_crystals_present: bool, max_temp_f: float = 35.0) -> dict:
    """Assess thaw-and-refreeze adulteration risk on frozen food pallets."""
    adulterated = bool(ice_crystals_present) or max_temp_f > 32.0
    return {"op": "assess_frozen_thaw_refreeze_risk", "adulterated": adulterated, "src": "recallstorm/food_safety/temperature_holds.py"}


def map_multi_deck_case_zones(case_id: str, decks: int = 4) -> list[str]:
    """Map temperature sensor zones across a multi-deck refrigerated case."""
    _req(case_id, "case_id")
    if decks <= 0:
        raise DataValidationError("decks must be positive")
    return [f"{case_id}-DECK-{i}" for i in range(1, decks + 1)]


def generate_temp_hold_pallet_tags(dc_id: str, pallet_count: int = 1) -> list[str]:
    """Generate red temperature-hold pallet tag IDs."""
    _req(dc_id, "dc_id")
    if pallet_count <= 0:
        raise DataValidationError("pallet_count must be positive")
    return [f"THOLD-{dc_id}-{i:03d}" for i in range(1, pallet_count + 1)]


def validate_probe_calibration_status(probe_id: str, ice_point_f: float = 32.0) -> dict:
    """Validate thermometer probe calibration within +/- 1.0F of 32.0F ice point."""
    _req(probe_id, "probe_id")
    calibrated = abs(float(ice_point_f) - 32.0) <= 1.0
    return {"op": "validate_probe_calibration_status", "probe_id": str(probe_id), "calibrated": calibrated, "src": "recallstorm/food_safety/temperature_holds.py"}


def authorize_disposition_after_review(hold_id: str, qa_verdict: str = "DESTROY") -> dict:
    """Record QA disposition ('DESTROY' or 'RELEASE') after temperature log review."""
    _req(hold_id, "hold_id")
    v = str(qa_verdict).upper()
    if v not in {"DESTROY", "RELEASE"}:
        raise DataValidationError(f"Invalid qa_verdict: {qa_verdict!r}")
    return {"op": "authorize_disposition_after_review", "hold_id": str(hold_id), "verdict": v, "src": "recallstorm/food_safety/temperature_holds.py"}
