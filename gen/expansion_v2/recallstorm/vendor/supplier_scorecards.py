"""Vendor recall frequency/severity scorecards and line-review penalties."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class VendorComplianceScorecard:
    """Supplier food-safety and regulatory recall compliance scorecard."""

    ref_id: str = "SCR-VND-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class RecallPenaltyWeighting:
    """Weighting model for Class I, II, and III supplier recalls."""

    ref_id: str = "SCR-WGT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def calculate_recall_frequency_severity_index(class_i: int, class_ii: int, class_iii: int = 0) -> float:
    """Calculate weighted recall severity index (Class I = 10x, Class II = 4x, Class III = 1x)."""
    if class_i < 0 or class_ii < 0 or class_iii < 0:
        raise DataValidationError("Recall counts cannot be negative")
    return float(class_i * 10 + class_ii * 4 + class_iii * 1)


def penalize_late_recall_notification_lag(lag_hours: float, sla_hours: float = 2.0) -> float:
    """Compute scorecard point deduction for late vendor recall notification (> 2.0h after FDA filing)."""
    if lag_hours < 0 or sla_hours <= 0:
        raise DataValidationError("Invalid hours")
    if lag_hours <= sla_hours:
        return 0.0
    return round(min(50.0, (lag_hours - sla_hours) * 5.0), 2)


def score_lot_traceability_data_completeness(fields_present: int, total_fields: int = 10) -> float:
    """Score GS1/EPCIS lot data completeness in [0.0, 100.0]."""
    if fields_present < 0 or total_fields <= 0 or fields_present > total_fields:
        raise DataValidationError("Invalid field counts")
    return round((fields_present / total_fields) * 100.0, 2)


def evaluate_chargeback_dispute_friction_rate(disputed_claims: int, total_claims: int) -> float:
    """Compute fraction of recall chargebacks disputed by the supplier."""
    if disputed_claims < 0 or total_claims <= 0 or disputed_claims > total_claims:
        raise DataValidationError("Invalid claim counts")
    return round(disputed_claims / total_claims, 4)


def rank_category_suppliers_by_safety_risk(scores: dict[str, float]) -> list[str]:
    """Order supplier IDs from highest risk score to lowest."""
    if scores is None:
        raise DataValidationError("scores cannot be None")
    return [k for k, _ in sorted(scores.items(), key=lambda x: (-float(x[1]), str(x[0])))]


def trigger_probationary_business_review(vendor_id: str, scorecard_grade: float) -> dict:
    """Place supplier on Probationary Quality Hold when scorecard_grade < 70.0."""
    _req(vendor_id, "vendor_id")
    if not (0.0 <= scorecard_grade <= 100.0):
        raise DataValidationError("scorecard_grade must be in [0, 100]")
    return {"op": "trigger_probationary_business_review", "vendor_id": str(vendor_id), "probation": scorecard_grade < 70.0, "src": "recallstorm/vendor/supplier_scorecards.py"}


def feed_scorecard_to_merchandising_line_review(vendor_id: str, score: float) -> dict:
    """Export supplier safety score to annual merchandising category line review."""
    _req(vendor_id, "vendor_id")
    return {"op": "feed_scorecard_to_merchandising_line_review", "vendor_id": str(vendor_id), "score": float(score), "src": "recallstorm/vendor/supplier_scorecards.py"}


def benchmark_dsd_vs_warehouse_compliance(dsd_score: float, whse_score: float) -> dict:
    """Compare DSD supplier compliance against warehouse-delivered supplier compliance."""
    if dsd_score < 0 or whse_score < 0:
        raise DataValidationError("Scores cannot be negative")
    return {"op": "benchmark_dsd_vs_warehouse_compliance", "delta": round(dsd_score - whse_score, 2), "src": "recallstorm/vendor/supplier_scorecards.py"}


def track_reformulation_deadline_adherence(on_time_skus: int, total_skus: int) -> float:
    """Compute percentage of supplier SKUs reformulated on time."""
    return score_lot_traceability_data_completeness(on_time_skus, total_skus)


def export_executive_vendor_risk_matrix(vendors: list[dict]) -> dict:
    """Export executive vendor risk matrix."""
    if vendors is None:
        raise DataValidationError("vendors cannot be None")
    return {"op": "export_executive_vendor_risk_matrix", "vendor_count": len(vendors), "src": "recallstorm/vendor/supplier_scorecards.py"}
