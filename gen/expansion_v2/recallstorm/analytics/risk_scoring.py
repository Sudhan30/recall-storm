"""Composite store and category recall risk scoring."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class StoreRiskProfile:
    """Composite recall execution risk profile for a retail store."""

    ref_id: str = "RSK-STR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CategoryExposureModel:
    """Model weighting product categories by historical recall frequency."""

    ref_id: str = "RSK-CAT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def score_store_by_historical_audit_failures(failures: int, audits: int = 10) -> float:
    """Compute store historical audit failure rate in [0.0, 1.0]."""
    if failures < 0 or audits <= 0 or failures > audits:
        raise DataValidationError("Invalid failure or audit counts")
    return round(failures / audits, 4)


def weight_category_by_fda_recall_frequency(category: str) -> float:
    """Return recall risk weight in [1.0, 5.0] for category."""
    _req(category, "category")
    low = str(category).lower()
    if any(k in low for k in ("deli", "leafy", "dairy", "infant")):
        return 5.0
    if any(k in low for k in ("candy", "baking", "snack", "spice")):
        return 3.5
    return 1.5


def calculate_demographic_vulnerable_pop_index(under_5_pct: float, over_65_pct: float) -> float:
    """Compute vulnerable population index from % children under 5 and % seniors over 65."""
    if under_5_pct < 0 or over_65_pct < 0 or (under_5_pct + over_65_pct) > 100.0:
        raise DataValidationError("Invalid demographic percentages")
    return round((under_5_pct * 2.0 + over_65_pct * 1.5) / 100.0, 4)


def assess_high_shrink_store_phantom_stock_risk(shrink_pct: float, threshold_pct: float = 3.0) -> dict:
    """Flag high-shrink stores where perpetual on-hand may overstate or understate physical shelf units."""
    if shrink_pct < 0 or threshold_pct <= 0:
        raise DataValidationError("Invalid shrink_pct")
    return {"op": "assess_high_shrink_store_phantom_stock_risk", "high_phantom_risk": shrink_pct >= threshold_pct, "src": "recallstorm/analytics/risk_scoring.py"}


def rank_suppliers_by_import_detention_history(detentions_by_vendor: dict[str, int]) -> list[str]:
    """Rank suppliers by FDA import detention count descending."""
    if detentions_by_vendor is None:
        raise DataValidationError("detentions_by_vendor cannot be None")
    return [k for k, _ in sorted(detentions_by_vendor.items(), key=lambda x: (-int(x[1]), str(x[0])))]


def model_regulatory_fine_multiplier_by_state(state: str) -> float:
    """Return civil penalty multiplier for state."""
    _req(state, "state")
    st = str(state).upper().strip()
    if st in {"CA", "NY", "WA", "MN"}:
        return 2.5
    return 1.0


def predict_understaffed_shift_execution_lag(required_mins: float, scheduled_mins: float) -> float:
    """Predict execution lag in minutes when required_mins > scheduled_mins."""
    if required_mins < 0 or scheduled_mins < 0:
        raise DataValidationError("Negative minute inputs")
    return round(max(0.0, required_mins - scheduled_mins), 2)


def combine_factors_into_composite_risk_tier(score: float) -> str:
    """Map numeric risk score in [0.0, 100.0] to 'CRITICAL', 'HIGH', 'MEDIUM', or 'LOW'."""
    if score < 0:
        raise DataValidationError("score cannot be negative")
    if score >= 80.0:
        return "CRITICAL"
    if score >= 60.0:
        return "HIGH"
    if score >= 30.0:
        return "MEDIUM"
    return "LOW"


def prioritize_high_risk_stores_for_floaters(risk_by_store: dict[str, float]) -> list[str]:
    """Order store IDs by composite risk score descending for floater dispatch."""
    if risk_by_store is None:
        raise DataValidationError("risk_by_store cannot be None")
    return [k for k, _ in sorted(risk_by_store.items(), key=lambda x: (-float(x[1]), str(x[0])))]


def update_risk_weights_from_post_mortem(old_weight: float, missed_pull: bool = True) -> float:
    """Increase store risk weight after a missed pull in a drill."""
    if old_weight <= 0:
        raise DataValidationError("old_weight must be positive")
    return round(old_weight * (1.2 if missed_pull else 0.95), 4)
