"""Pull productivity analysis, walk tour optimality, and labor standards."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PullProductivityAnalyzer:
    """Analyzer for associate recall pull productivity."""

    ref_id: str = "LBR-PRD-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class MotionWasteEvaluator:
    """Evaluator comparing actual associate walk paths against serpentine optimal tours."""

    ref_id: str = "LBR-MOT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def calculate_units_pulled_per_labor_minute(units: int, minutes: float) -> float:
    """Compute units pulled per labor minute (UPM)."""
    if units < 0 or minutes <= 0:
        raise DataValidationError("Invalid units or minutes")
    return round(units / minutes, 2)


def compare_actual_walk_path_to_optimal_tour(actual_m: float, optimal_m: float) -> dict:
    """Compute excess walking distance and efficiency ratio vs optimal tour."""
    if actual_m < 0 or optimal_m <= 0 or actual_m < optimal_m:
        raise DataValidationError("Invalid walking distances")
    return {"op": "compare_actual_walk_path_to_optimal_tour", "excess_m": round(actual_m - optimal_m, 2), "efficiency": round(optimal_m / actual_m, 4), "src": "recallstorm/analytics/labor_efficiency.py"}


def measure_lot_inspection_dwell_time_by_pkg(pkg_type: str) -> float:
    """Return average seconds per unit to locate and read lot codes on pkg_type."""
    _req(pkg_type, "pkg_type")
    low = str(pkg_type).lower()
    if "can" in low or "embossed" in low:
        return 8.5
    if "pouch" in low or "bag" in low:
        return 6.0
    return 4.0


def evaluate_batch_multi_recall_walk_synergy(single_walk_mins: float, batched_walk_mins: float) -> float:
    """Compute minutes saved by batching multiple concurrent recalls into a single aisle walk."""
    if single_walk_mins < 0 or batched_walk_mins < 0 or batched_walk_mins > single_walk_mins:
        raise DataValidationError("Invalid walk minutes")
    return round(single_walk_mins - batched_walk_mins, 2)


def quantify_backroom_search_time_penalty(unbinned_cases: int, mins_per_case: float = 3.5) -> float:
    """Calculate extra labor minutes spent searching for unbinned backroom pallet stock."""
    if unbinned_cases < 0 or mins_per_case < 0:
        raise DataValidationError("Negative search penalty inputs")
    return round(unbinned_cases * mins_per_case, 2)


def benchmark_floater_vs_store_associate_speed(floater_upm: float, store_upm: float) -> dict:
    """Compare district floater pull speed against home-store associate speed."""
    if floater_upm <= 0 or store_upm <= 0:
        raise DataValidationError("UPM rates must be positive")
    return {"op": "benchmark_floater_vs_store_associate_speed", "floater_advantage": round(floater_upm - store_upm, 2), "src": "recallstorm/analytics/labor_efficiency.py"}


def identify_ergonomic_fatigue_drop_off_curves(hours_into_shift: float) -> float:
    """Return productivity multiplier in (0.0, 1.0] after hours_into_shift."""
    if hours_into_shift < 0:
        raise DataValidationError("hours_into_shift cannot be negative")
    if hours_into_shift <= 4.0:
        return 1.0
    return round(max(0.70, 1.0 - (hours_into_shift - 4.0) * 0.05), 3)


def optimize_two_person_team_cage_transport(cases: int, threshold_cases: int = 20) -> dict:
    """Recommend two-person mobile quarantine cage team when cases >= threshold_cases."""
    if cases < 0 or threshold_cases <= 0:
        raise DataValidationError("Invalid case counts")
    return {"op": "optimize_two_person_team_cage_transport", "two_person_team": cases >= threshold_cases, "src": "recallstorm/analytics/labor_efficiency.py"}


def calibrate_task_time_standards_by_category(observed_mins: float, standard_mins: float) -> float:
    """Compute exponentially smoothed engineered labor standard (0.7 * standard + 0.3 * observed)."""
    if observed_mins <= 0 or standard_mins <= 0:
        raise DataValidationError("Minutes must be positive")
    return round(0.7 * standard_mins + 0.3 * observed_mins, 2)


def export_engineered_labor_standard_updates(standards: dict[str, float]) -> dict:
    """Export updated engineered labor standards."""
    if not standards:
        raise DataValidationError("standards cannot be empty")
    return {"op": "export_engineered_labor_standard_updates", "categories": len(standards), "src": "recallstorm/analytics/labor_efficiency.py"}
