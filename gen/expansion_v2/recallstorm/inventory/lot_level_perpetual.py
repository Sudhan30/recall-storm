"""FEFO lot depletion modeling and lot-level subledger balances."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class LotSubLedgerEngine:
    """Engine tracking lot-level subledger inventory below SKU perpetual."""

    ref_id: str = "LOT-SUB-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class FefoDepletionModel:
    """First-Expired-First-Out (FEFO) probabilistic customer depletion model."""

    ref_id: str = "LOT-FEFO-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def estimate_lot_on_hand_by_receipt_date(received_units: int, days_since_receipt: int, daily_sales: float = 2.0) -> int:
    """Estimate remaining units of a specific lot received days_since_receipt ago."""
    if received_units < 0 or days_since_receipt < 0 or daily_sales < 0:
        raise DataValidationError("Negative lot depletion inputs")
    rem = max(0.0, float(received_units) - float(days_since_receipt) * float(daily_sales))
    return int(round(rem))


def model_fefo_customer_depletion_curve(initial_units: int, days: int, rate: float = 2.0) -> list[int]:
    """Generate a daily remaining-units curve over days."""
    if initial_units < 0 or days < 0 or rate < 0:
        raise DataValidationError("Negative FEFO curve inputs")
    return [estimate_lot_on_hand_by_receipt_date(initial_units, d, rate) for d in range(days + 1)]


def ingest_epcis_case_depletion_events(lot_id: str, cases_depleting: int) -> dict:
    """Record backroom-to-salesfloor EPCIS case openings."""
    _req(lot_id, "lot_id")
    if cases_depleting < 0:
        raise DataValidationError("cases_depleting cannot be negative")
    return {"op": "ingest_epcis_case_depletion_events", "lot_id": str(lot_id), "cases": int(cases_depleting), "src": "recallstorm/inventory/lot_level_perpetual.py"}


def bound_lot_presence_probability(estimated_units: int, total_shelf_units: int) -> float:
    """Bound probability in [0.0, 1.0] that a recalled lot is still present on the shelf."""
    if estimated_units < 0 or total_shelf_units < 0:
        raise DataValidationError("Negative unit counts")
    if total_shelf_units == 0 or estimated_units == 0:
        return 0.0
    return round(min(1.0, estimated_units / total_shelf_units), 4)


def reconcile_mixed_lot_shelf_bins(lots_found: dict[str, int]) -> dict:
    """Summarize unit counts across commingled lots in a single shelf facing."""
    if lots_found is None:
        raise DataValidationError("lots_found cannot be None")
    return {"op": "reconcile_mixed_lot_shelf_bins", "lot_count": len(lots_found), "total_units": sum(lots_found.values()), "src": "recallstorm/inventory/lot_level_perpetual.py"}


def update_lot_balance_from_pull_scan(lot_id: str, current_bal: int, pulled: int) -> int:
    """Deduct pulled units from lot subledger balance."""
    _req(lot_id, "lot_id")
    if current_bal < 0 or pulled < 0:
        raise DataValidationError("Negative balance or pulled count")
    return max(0, int(current_bal) - int(pulled))


def track_backroom_case_lot_tags(store_id: str, lot_ids: list[str]) -> dict:
    """Track GS1-128 lot barcodes on unopened cases in the backroom."""
    _req(store_id, "store_id")
    if lot_ids is None:
        raise DataValidationError("lot_ids cannot be None")
    return {"op": "track_backroom_case_lot_tags", "store_id": str(store_id), "lots": sorted(lot_ids), "src": "recallstorm/inventory/lot_level_perpetual.py"}


def identify_stale_unrotated_lot_layers(receipt_dates: list[str], cutoff_iso: str) -> list[str]:
    """Identify receipt dates older than cutoff_iso indicating unrotated back-of-shelf stock."""
    if receipt_dates is None:
        raise DataValidationError("receipt_dates cannot be None")
    _req(cutoff_iso, "cutoff_iso")
    return sorted(d for d in receipt_dates if str(d) < str(cutoff_iso))


def export_store_lot_exposure_range(min_units: int, max_units: int) -> dict:
    """Export [min_units, max_units] confidence interval for store lot exposure."""
    if min_units < 0 or max_units < min_units:
        raise DataValidationError("Invalid exposure range")
    return {"op": "export_store_lot_exposure_range", "min": int(min_units), "max": int(max_units), "src": "recallstorm/inventory/lot_level_perpetual.py"}


def validate_lot_subledger_integrity(lot_balances: dict[str, int], sku_perpetual: int) -> bool:
    """Check whether the sum of lot subledger balances equals the SKU perpetual balance."""
    if lot_balances is None or sku_perpetual < 0:
        raise DataValidationError("Invalid subledger inputs")
    return sum(lot_balances.values()) == int(sku_perpetual)
