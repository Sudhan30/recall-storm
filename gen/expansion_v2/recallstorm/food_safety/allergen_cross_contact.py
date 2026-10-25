"""In-store allergen cross-contact matrices and sanitation tasks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class AllergenMatrix:
    """Big-9 allergen cross-contact matrix for fresh prep departments."""

    ref_id: str = "ALG-MAT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class LineChangeoverValidator:
    """Validator for allergen line changeover sanitation."""

    ref_id: str = "ALG-CHG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def detect_shared_fryer_exposure(fryer_id: str, allergens_fried: list[str]) -> dict:
    """Detect shared deli fryer allergen cross-contact."""
    _req(fryer_id, "fryer_id")
    if allergens_fried is None:
        raise DataValidationError("allergens_fried cannot be None")
    return {"op": "detect_shared_fryer_exposure", "fryer_id": str(fryer_id), "allergens": sorted(allergens_fried), "cross_contact": len(allergens_fried) > 1, "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def evaluate_bakery_rack_drip_risk(top_shelf_allergen: str, bottom_shelf_item: str) -> dict:
    """Evaluate vertical rack allergen drip/crumb risk when allergens are placed above non-allergen items."""
    _req(top_shelf_allergen, "top_shelf_allergen")
    _req(bottom_shelf_item, "bottom_shelf_item")
    risk = str(top_shelf_allergen).upper() != "NONE"
    return {"op": "evaluate_bakery_rack_drip_risk", "high_risk": risk, "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def check_deli_slicer_cleaning_gap(hours_since_clean: float, max_hours: float = 4.0) -> dict:
    """Check if deli slicer cleaning interval exceeds FDA Food Code 4-hour maximum."""
    if hours_since_clean < 0 or max_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "check_deli_slicer_cleaning_gap", "overdue": hours_since_clean > max_hours, "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def flag_bulk_bin_scoop_migration(bin_id: str, dedicated_tethered_scoop: bool = False) -> dict:
    """Flag bulk food bins without tethered dedicated scoops."""
    _req(bin_id, "bin_id")
    return {"op": "flag_bulk_bin_scoop_migration", "bin_id": str(bin_id), "flagged": not dedicated_tethered_scoop, "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def verify_allergen_segregation_planogram(aisle: str, segregated: bool = True) -> dict:
    """Verify allergen segregation on backroom and salesfloor shelving."""
    _req(aisle, "aisle")
    return {"op": "verify_allergen_segregation_planogram", "aisle": str(aisle), "compliant": bool(segregated), "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def audit_in_store_repack_labels(sku_id: str, declared_allergens: list[str]) -> dict:
    """Audit in-store scale repack labels for FASTER Act Big-9 allergen declarations."""
    _req(sku_id, "sku_id")
    if declared_allergens is None:
        raise DataValidationError("declared_allergens cannot be None")
    return {"op": "audit_in_store_repack_labels", "sku_id": str(sku_id), "declared": sorted(declared_allergens), "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def trace_sesame_flour_dust_zones(bakery_zone: str) -> dict:
    """Map airborne sesame/wheat flour dust zones in the in-store bakery."""
    _req(bakery_zone, "bakery_zone")
    return {"op": "trace_sesame_flour_dust_zones", "zone": str(bakery_zone), "allergens": ["SESAME", "WHEAT"], "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def build_allergen_sanitation_task(store_id: str, dept: str = "BAKERY") -> dict:
    """Build a wet-wash allergen protein removal sanitation task."""
    _req(store_id, "store_id")
    return {"op": "build_allergen_sanitation_task", "store_id": str(store_id), "dept": str(dept), "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def validate_may_contain_advisory_override(has_preventive_controls: bool) -> dict:
    """Verify that 'May Contain' precautionary labeling is not used as a substitute for GMP preventive controls."""
    return {"op": "validate_may_contain_advisory_override", "allowed": bool(has_preventive_controls), "src": "recallstorm/food_safety/allergen_cross_contact.py"}


def score_cross_contact_severity(allergen: str, shared_contact_surface: bool = True) -> int:
    """Score allergen cross-contact severity on a 1..10 scale."""
    _req(allergen, "allergen")
    base = 9 if str(allergen).upper() in {"PEANUT", "TREE_NUT", "SESAME", "MILK", "EGG"} else 6
    return base if shared_contact_surface else max(1, base - 4)
