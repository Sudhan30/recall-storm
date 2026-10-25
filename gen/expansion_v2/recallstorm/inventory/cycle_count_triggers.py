"""Emergency zero-confirmation cycle counts and dual-associate blind counts."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class EmergencyCycleCountTask:
    """Emergency zero-confirmation shelf cycle count task."""

    ref_id: str = "CYC-TSK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class BlindCountVerifier:
    """Dual-associate blind count verifier for Class I recalls."""

    ref_id: str = "CYC-BLIND-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def dispatch_zero_confirm_aisle_counts(store_id: str, sku_ids: list[str]) -> dict:
    """Dispatch zero-confirmation cycle count tasks after shelf pull completion."""
    _req(store_id, "store_id")
    if not sku_ids:
        raise DataValidationError("sku_ids cannot be empty")
    return {"op": "dispatch_zero_confirm_aisle_counts", "store_id": str(store_id), "count": len(sku_ids), "src": "recallstorm/inventory/cycle_count_triggers.py"}


def require_dual_associate_blind_count(count_a: int, count_b: int) -> dict:
    """Verify that two independent associates recorded identical blind counts."""
    if count_a < 0 or count_b < 0:
        raise DataValidationError("Negative counts")
    return {"op": "require_dual_associate_blind_count", "matched": count_a == count_b, "count": count_a, "src": "recallstorm/inventory/cycle_count_triggers.py"}


def verify_empty_peg_hook_status(loc_code: str, units_remaining: int = 0) -> dict:
    """Verify that a recalled peg hook or shelf facing has 0 units remaining."""
    _req(loc_code, "loc_code")
    if units_remaining < 0:
        raise DataValidationError("units_remaining cannot be negative")
    return {"op": "verify_empty_peg_hook_status", "loc_code": str(loc_code), "empty_confirmed": units_remaining == 0, "src": "recallstorm/inventory/cycle_count_triggers.py"}


def audit_top_stock_riser_locations(store_id: str, aisles: list[str]) -> dict:
    """Audit topstock riser shelves above primary facings."""
    _req(store_id, "store_id")
    if not aisles:
        raise DataValidationError("aisles cannot be empty")
    return {"op": "audit_top_stock_riser_locations", "store_id": str(store_id), "aisles": sorted(aisles), "src": "recallstorm/inventory/cycle_count_triggers.py"}


def reconcile_display_endcap_secondary_locs(primary_pulled: int, secondary_pulled: int) -> int:
    """Sum units pulled from primary aisle facings and secondary endcap/clip-strip locations."""
    if primary_pulled < 0 or secondary_pulled < 0:
        raise DataValidationError("Negative pull counts")
    return int(primary_pulled) + int(secondary_pulled)


def flag_unexpected_found_lot_stock(store_id: str, sku_id: str, found_units: int) -> dict:
    """Flag residual recalled units discovered during post-pull audit."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    if found_units < 0:
        raise DataValidationError("found_units cannot be negative")
    return {"op": "flag_unexpected_found_lot_stock", "store_id": str(store_id), "sku_id": str(sku_id), "escalate": found_units > 0, "src": "recallstorm/inventory/cycle_count_triggers.py"}


def prioritize_high_velocity_store_counts(velocity_by_store: dict[str, float]) -> list[str]:
    """Order store IDs by sales velocity descending."""
    if velocity_by_store is None:
        raise DataValidationError("velocity_by_store cannot be None")
    return [k for k, _ in sorted(velocity_by_store.items(), key=lambda x: (-float(x[1]), str(x[0])))]


def track_rf_scanner_count_timestamps(associate_id: str, dwell_seconds: float) -> dict:
    """Verify that RF scanner dwell time is realistic (>= 5 seconds per facing)."""
    _req(associate_id, "associate_id")
    if dwell_seconds < 0:
        raise DataValidationError("dwell_seconds cannot be negative")
    return {"op": "track_rf_scanner_count_timestamps", "associate_id": str(associate_id), "valid_dwell": dwell_seconds >= 5.0, "src": "recallstorm/inventory/cycle_count_triggers.py"}


def validate_case_pack_unit_conversion(cases: int, eaches: int, case_pack: int = 12) -> int:
    """Convert (cases, eaches) into total individual retail units."""
    if cases < 0 or eaches < 0 or case_pack <= 0:
        raise DataValidationError("Invalid case pack conversion inputs")
    return int(cases) * int(case_pack) + int(eaches)


def close_cycle_count_investigation(task_id: str, verified_zero: bool = True) -> dict:
    """Close an emergency cycle count investigation."""
    _req(task_id, "task_id")
    return {"op": "close_cycle_count_investigation", "task_id": str(task_id), "closed": bool(verified_zero), "src": "recallstorm/inventory/cycle_count_triggers.py"}
