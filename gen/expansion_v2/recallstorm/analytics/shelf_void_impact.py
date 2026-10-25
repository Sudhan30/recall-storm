"""Out-of-stock duration tracking and substitute capture rate analytics."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class OutOfStockDurationTracker:
    """Tracker for empty shelf facing duration following a recall pull."""

    ref_id: str = "VOID-TRK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SubstituteCaptureRate:
    """Analytics model measuring demand transfer to substitute SKUs."""

    ref_id: str = "VOID-SUB-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def measure_days_of_empty_facing_post_pull(pull_day: int, restock_day: int) -> int:
    """Return days a shelf facing remained empty between recall pull and substitute/clean-lot restock."""
    if pull_day < 0 or restock_day < pull_day:
        raise DataValidationError("Invalid pull_day or restock_day")
    return int(restock_day) - int(pull_day)


def calculate_substitute_sku_sales_halo_lift(baseline_sub_units: int, post_recall_sub_units: int) -> float:
    """Compute percentage lift on substitute SKU sales after placing substitutes into recalled facings."""
    if baseline_sub_units <= 0 or post_recall_sub_units < 0:
        raise DataValidationError("Invalid unit counts")
    return round(((post_recall_sub_units - baseline_sub_units) / baseline_sub_units) * 100.0, 2)


def quantify_category_switching_walk_away_rate(recalled_baseline_units: int, sub_gained_units: int) -> float:
    """Compute walk-away rate in [0.0, 1.0]: fraction of recalled SKU demand not captured by substitutes."""
    if recalled_baseline_units <= 0 or sub_gained_units < 0:
        raise DataValidationError("Invalid unit counts")
    captured = min(1.0, sub_gained_units / recalled_baseline_units)
    return round(1.0 - captured, 4)


def track_time_to_replenish_with_clean_lot(hours_elapsed: float, target_hours: float = 48.0) -> dict:
    """Evaluate time to replenish empty facings with DC substitute or clean-lot stock."""
    if hours_elapsed < 0 or target_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "track_time_to_replenish_with_clean_lot", "met_target": hours_elapsed <= target_hours, "hours": float(hours_elapsed), "src": "recallstorm/analytics/shelf_void_impact.py"}


def evaluate_emergency_re_planogram_compliance(stores_spread: int, total_stores: int) -> float:
    """Compute percentage of stores that spread adjacent facings to cover long-term recall voids."""
    if stores_spread < 0 or total_stores <= 0 or stores_spread > total_stores:
        raise DataValidationError("Invalid store counts")
    return round((stores_spread / total_stores) * 100.0, 2)


def identify_orphaned_shelf_tags_without_stock(tags: list[dict]) -> list[str]:
    """Return sorted SKU IDs with active shelf tags but zero stock and no inbound PO."""
    if tags is None:
        raise DataValidationError("tags cannot be None")
    return sorted(str(t["sku_id"]) for t in tags if int(t.get("on_hand", 0)) == 0 and not t.get("has_po"))


def correlate_void_duration_with_nps_drop(void_days: int) -> float:
    """Estimate Net Promoter Score (NPS) point drop from prolonged shelf voids."""
    if void_days < 0:
        raise DataValidationError("void_days cannot be negative")
    return round(min(15.0, void_days * 0.4), 2)


def score_dc_emergency_allocation_fill_rate(allocated_cases: int, demanded_cases: int) -> float:
    """Compute DC substitute case fill rate in [0.0, 1.0]."""
    if allocated_cases < 0 or demanded_cases <= 0 or allocated_cases > demanded_cases:
        raise DataValidationError("Invalid case counts")
    return round(allocated_cases / demanded_cases, 4)


def recommend_safety_stock_buffer_adjustments(sub_sku_id: str, current_buffer_cases: int, lift_factor: float = 1.5) -> dict:
    """Recommend increased DC safety stock buffer for designated substitute SKUs."""
    _req(sub_sku_id, "sub_sku_id")
    if current_buffer_cases < 0 or lift_factor < 1.0:
        raise DataValidationError("Invalid buffer inputs")
    return {"op": "recommend_safety_stock_buffer_adjustments", "sub_sku_id": str(sub_sku_id), "new_buffer_cases": int(round(current_buffer_cases * lift_factor)), "src": "recallstorm/analytics/shelf_void_impact.py"}


def export_merchandising_recovery_scorecard(category: str, fill_rate: float) -> dict:
    """Export category merchandising recovery scorecard."""
    _req(category, "category")
    if not (0.0 <= fill_rate <= 1.0):
        raise DataValidationError("fill_rate must be in [0, 1]")
    return {"op": "export_merchandising_recovery_scorecard", "category": str(category), "fill_rate": float(fill_rate), "src": "recallstorm/analytics/shelf_void_impact.py"}
