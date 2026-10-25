"""Reclamation sort chutes, vendor gaylords, and salvage auction blocks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ReclamationSortEngine:
    """Sortation engine at a return/reclamation center."""

    ref_id: str = "REC-SRT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CrushedBaleTracker:
    """Tracker for compacted/destroyed reclamation bales."""

    ref_id: str = "REC-BAL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def configure_reclamation_scanner_sort_chutes(sku_id: str, disposition: str = "DESTROY") -> str:
    """Route a scanned SKU to the appropriate reclamation sortation chute."""
    _req(sku_id, "sku_id")
    d = str(disposition).upper()
    if d == "RETURN_TO_VENDOR":
        return "CHUTE_VENDOR_RETURN"
    if d == "HAZMAT":
        return "CHUTE_HAZMAT_CAGE"
    return "CHUTE_COMPACTOR_DESTROY"


def route_scanned_returns_to_vendor_gaylords(vendor_id: str, units: int) -> dict:
    """Route vendor-returnable recall units into a vendor-specific gaylord pallet box."""
    _req(vendor_id, "vendor_id")
    if units <= 0:
        raise DataValidationError("units must be positive")
    return {"op": "route_scanned_returns_to_vendor_gaylords", "vendor_id": str(vendor_id), "units": int(units), "src": "recallstorm/dc_ops/reclamation_center.py"}


def separate_hazmat_aerosols_and_lithium_ion(items: list[dict]) -> dict[str, list[str]]:
    """Segregate aerosols and lithium-ion batteries from general trash compactor stream."""
    if items is None:
        raise DataValidationError("items cannot be None")
    haz: list[str] = []
    gen: list[str] = []
    for it in items:
        if it.get("is_hazmat"):
            haz.append(str(it["sku_id"]))
        else:
            gen.append(str(it["sku_id"]))
    return {"hazmat": sorted(haz), "general": sorted(gen)}


def weigh_and_tag_completed_vendor_pallets(gaylord_id: str, weight_lb: float) -> dict:
    """Weigh and seal a completed vendor return gaylord."""
    _req(gaylord_id, "gaylord_id")
    if weight_lb <= 0:
        raise DataValidationError("weight_lb must be positive")
    return {"op": "weigh_and_tag_completed_vendor_pallets", "gaylord_id": str(gaylord_id), "weight_lb": round(float(weight_lb), 2), "src": "recallstorm/dc_ops/reclamation_center.py"}


def record_zero_value_trash_compactor_throws(sku_id: str, units: int) -> dict:
    """Log compactor destruction throw count at reclamation."""
    _req(sku_id, "sku_id")
    if units < 0:
        raise DataValidationError("units cannot be negative")
    return {"op": "record_zero_value_trash_compactor_throws", "sku_id": str(sku_id), "units": int(units), "src": "recallstorm/dc_ops/reclamation_center.py"}


def verify_item_eligibility_for_food_bank_donate(is_recalled: bool = True) -> dict:
    """Strictly block any recalled or banned food product from food-bank donation chutes."""
    return {"op": "verify_item_eligibility_for_food_bank_donate", "donate_allowed": not is_recalled, "src": "recallstorm/dc_ops/reclamation_center.py"}


def prevent_recalled_item_from_salvage_auction(sku_id: str) -> dict:
    """Hard-block recalled SKUs from B-stock / secondary salvage liquidation pallets."""
    _req(sku_id, "sku_id")
    return {"op": "prevent_recalled_item_from_salvage_auction", "sku_id": str(sku_id), "salvage_blocked": True, "src": "recallstorm/dc_ops/reclamation_center.py"}


def audit_store_return_tote_manifest_accuracy(manifest_units: int, scanned_units: int) -> dict:
    """Compare store return tote manifest against reclamation center scan count."""
    if manifest_units < 0 or scanned_units < 0:
        raise DataValidationError("Negative unit counts")
    return {"op": "audit_store_return_tote_manifest_accuracy", "variance": scanned_units - manifest_units, "accurate": manifest_units == scanned_units, "src": "recallstorm/dc_ops/reclamation_center.py"}


def calculate_reclamation_processing_cost_per_unit(total_cost_usd: float, units_processed: int) -> float:
    """Compute per-unit reclamation center processing cost."""
    if total_cost_usd < 0 or units_processed <= 0:
        raise DataValidationError("Invalid cost or units_processed")
    return round(total_cost_usd / units_processed, 4)


def generate_vendor_pickup_ready_notification(vendor_id: str, pallet_count: int) -> dict:
    """Notify vendor that return gaylord pallets are staged for pickup."""
    _req(vendor_id, "vendor_id")
    if pallet_count <= 0:
        raise DataValidationError("pallet_count must be positive")
    return {"op": "generate_vendor_pickup_ready_notification", "vendor_id": str(vendor_id), "pallet_count": int(pallet_count), "src": "recallstorm/dc_ops/reclamation_center.py"}
