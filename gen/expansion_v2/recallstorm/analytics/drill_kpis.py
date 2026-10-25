"""Drill SLA performance tracking and board-level KPI scorecards."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class DrillScorecardEngine:
    """Engine computing recall drill execution KPIs."""

    ref_id: str = "KPI-DRL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SlaPerformanceTracker:
    """Tracker for 2-hour and 4-hour recall completion SLAs."""

    ref_id: str = "KPI-SLA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def calculate_time_to_first_store_scan_mins(notice_mins: float, first_scan_mins: float) -> float:
    """Calculate elapsed minutes from recall notice issuance to first store RF scan."""
    if notice_mins < 0 or first_scan_mins < notice_mins:
        raise DataValidationError("Invalid scan timestamps")
    return round(float(first_scan_mins) - float(notice_mins), 2)


def measure_four_hour_completion_rate_pct(completed_stores: int, total_stores: int) -> float:
    """Calculate percentage of stores completing all shelf pulls within 4 hours."""
    if completed_stores < 0 or total_stores <= 0 or completed_stores > total_stores:
        raise DataValidationError("Invalid store counts")
    return round((completed_stores / total_stores) * 100.0, 2)


def compute_lot_capture_accuracy_precision(true_positives: int, false_positives: int) -> float:
    """Compute precision of lot-specific pulls: TP / (TP + FP)."""
    if true_positives < 0 or false_positives < 0 or (true_positives + false_positives) == 0:
        raise DataValidationError("Invalid TP/FP counts")
    return round(true_positives / (true_positives + false_positives), 4)


def score_pos_block_deployment_latency_secs(latency_secs: float, target_secs: float = 30.0) -> dict:
    """Score POS stop-sale deployment latency against 30-second target."""
    if latency_secs < 0 or target_secs <= 0:
        raise DataValidationError("Invalid latency_secs")
    return {"op": "score_pos_block_deployment_latency_secs", "met_target": latency_secs <= target_secs, "latency_secs": float(latency_secs), "src": "recallstorm/analytics/drill_kpis.py"}


def benchmark_division_vs_company_avg_speed(div_mins: float, company_mins: float) -> float:
    """Return signed minute delta vs company average completion speed (negative = faster)."""
    if div_mins <= 0 or company_mins <= 0:
        raise DataValidationError("Minutes must be positive")
    return round(float(div_mins) - float(company_mins), 2)


def track_false_positive_unaffected_pull_rate(unaffected_pulled: int, total_pulled: int) -> float:
    """Compute over-pull rate of unaffected lots."""
    if unaffected_pulled < 0 or total_pulled <= 0 or unaffected_pulled > total_pulled:
        raise DataValidationError("Invalid pull counts")
    return round(unaffected_pulled / total_pulled, 4)


def evaluate_backroom_vs_salesfloor_miss_rate(backroom_missed: int, salesfloor_missed: int) -> dict:
    """Compare backroom miss count vs salesfloor miss count."""
    if backroom_missed < 0 or salesfloor_missed < 0:
        raise DataValidationError("Negative miss counts")
    return {"op": "evaluate_backroom_vs_salesfloor_miss_rate", "backroom_higher": backroom_missed > salesfloor_missed, "src": "recallstorm/analytics/drill_kpis.py"}


def calculate_labor_hours_variance_to_plan(actual_hours: float, planned_hours: float) -> float:
    """Compute variance between actual execution labor hours and planned hours."""
    if actual_hours < 0 or planned_hours < 0:
        raise DataValidationError("Negative labor hours")
    return round(float(actual_hours) - float(planned_hours), 2)


def generate_executive_drill_grade_letter(completion_pct: float) -> str:
    """Assign letter grade ('A', 'B', 'C', 'F') based on 4-hour completion_pct."""
    if not (0.0 <= completion_pct <= 100.0):
        raise DataValidationError("completion_pct must be in [0, 100]")
    if completion_pct >= 98.0:
        return "A"
    if completion_pct >= 90.0:
        return "B"
    if completion_pct >= 80.0:
        return "C"
    return "F"


def export_board_level_compliance_kpi_deck(drill_id: str, grade: str = "A") -> dict:
    """Export board-level recall drill KPI summary."""
    _req(drill_id, "drill_id")
    _req(grade, "grade")
    return {"op": "export_board_level_compliance_kpi_deck", "drill_id": str(drill_id), "grade": str(grade), "src": "recallstorm/analytics/drill_kpis.py"}
