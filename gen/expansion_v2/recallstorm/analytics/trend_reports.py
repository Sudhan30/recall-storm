"""Longitudinal compliance views and additive ban readiness burn-down."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class HistoricalRecallTrends:
    """Longitudinal recall volume and completion velocity trends."""

    ref_id: str = "TRN-HST-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class LongitudinalComplianceView:
    """Multi-quarter compliance burn-down view."""

    ref_id: str = "TRN-LNG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def plot_monthly_recall_volume_by_fda_class(counts: dict[str, int]) -> dict:
    """Summarize monthly recall counts by FDA Class."""
    if counts is None or any(v < 0 for v in counts.values()):
        raise DataValidationError("Invalid counts")
    return {"op": "plot_monthly_recall_volume_by_fda_class", "total": sum(counts.values()), "by_class": dict(counts), "src": "recallstorm/analytics/trend_reports.py"}


def analyze_additive_ban_readiness_burn_down(remaining_skus_by_month: list[int]) -> dict:
    """Compute burn-down slope across monthly remaining non-reformulated SKUs."""
    if not remaining_skus_by_month or any(x < 0 for x in remaining_skus_by_month):
        raise DataValidationError("Invalid remaining_skus_by_month")
    reduction = remaining_skus_by_month[0] - remaining_skus_by_month[-1]
    return {"op": "analyze_additive_ban_readiness_burn_down", "net_reduction": reduction, "current": remaining_skus_by_month[-1], "src": "recallstorm/analytics/trend_reports.py"}


def track_repeat_offender_vendor_trajectories(recalls_by_vendor: dict[str, int], min_recalls: int = 2) -> list[str]:
    """Return sorted vendor_ids with >= min_recalls in the trailing 12 months."""
    if recalls_by_vendor is None or min_recalls <= 0:
        raise DataValidationError("Invalid vendor recall inputs")
    return sorted(v for v, c in recalls_by_vendor.items() if int(c) >= min_recalls)


def compare_q_over_q_time_to_100_pct_closure(prev_q_mins: float, curr_q_mins: float) -> dict:
    """Compare quarter-over-quarter time to 100% store closure."""
    if prev_q_mins <= 0 or curr_q_mins <= 0:
        raise DataValidationError("Closure minutes must be positive")
    improved = curr_q_mins < prev_q_mins
    return {"op": "compare_q_over_q_time_to_100_pct_closure", "improved": improved, "delta_mins": round(curr_q_mins - prev_q_mins, 2), "src": "recallstorm/analytics/trend_reports.py"}


def identify_chronic_bottleneck_store_formats(avg_mins_by_format: dict[str, float]) -> str:
    """Return the store format with the slowest average recall completion time."""
    if not avg_mins_by_format:
        raise DataValidationError("avg_mins_by_format cannot be empty")
    return max(avg_mins_by_format.items(), key=lambda x: (float(x[1]), str(x[0])))[0]


def correlate_staff_turnover_with_drill_scores(turnover_pct: float, drill_score: float) -> dict:
    """Evaluate correlation indicator between high store turnover (> 40%) and low drill scores (< 85)."""
    if not (0.0 <= turnover_pct <= 200.0) or not (0.0 <= drill_score <= 100.0):
        raise DataValidationError("Invalid turnover or drill_score")
    return {"op": "correlate_staff_turnover_with_drill_scores", "at_risk": turnover_pct > 40.0 and drill_score < 85.0, "src": "recallstorm/analytics/trend_reports.py"}


def chart_allergen_vs_micro_recall_proportions(allergen_count: int, micro_count: int, additive_count: int = 0) -> dict[str, float]:
    """Compute relative proportions of allergen, microbial, and additive recalls."""
    tot = allergen_count + micro_count + additive_count
    if allergen_count < 0 or micro_count < 0 or additive_count < 0 or tot <= 0:
        raise DataValidationError("Invalid recall counts")
    return {
        "allergen": round(allergen_count / tot, 4),
        "micro": round(micro_count / tot, 4),
        "additive": round(additive_count / tot, 4),
    }


def measure_year_over_year_shrink_recovery_pct(recovered_usd: float, total_loss_usd: float) -> float:
    """Calculate percentage of recall shrink recovered via vendor chargebacks."""
    if recovered_usd < 0 or total_loss_usd <= 0 or recovered_usd > total_loss_usd:
        raise DataValidationError("Invalid recovery or loss amounts")
    return round((recovered_usd / total_loss_usd) * 100.0, 2)


def generate_annual_food_safety_review_charts(year: int, total_drills: int) -> dict:
    """Generate annual food safety review summary."""
    if year < 2000 or total_drills < 0:
        raise DataValidationError("Invalid year or total_drills")
    return {"op": "generate_annual_food_safety_review_charts", "year": int(year), "total_drills": int(total_drills), "src": "recallstorm/analytics/trend_reports.py"}


def export_longitudinal_dataset_to_parquet(out_path: str, row_count: int = 10) -> dict:
    """Export longitudinal recall analytics dataset metadata."""
    _req(out_path, "out_path")
    if row_count < 0:
        raise DataValidationError("row_count cannot be negative")
    return {"op": "export_longitudinal_dataset_to_parquet", "out_path": str(out_path), "row_count": int(row_count), "src": "recallstorm/analytics/trend_reports.py"}
