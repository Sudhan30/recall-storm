"""Pennsylvania synthetic food dye warnings and school-zone restrictions."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PaSchoolDyeRule:
    """Domain entity for Pennsylvania synthetic food dye school-zone rules."""

    ref_id: str = "PA-DYE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class PaSyntheticDyeList:
    """List of FD&C synthetic dyes monitored in Pennsylvania."""

    ref_id: str = "PA-DYE-LIST"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_pa_dye_concentration(ppm: float, limit_ppm: float = 50.0) -> dict:
    """Check synthetic dye concentration in ppm against limit_ppm."""
    if not isinstance(ppm, (int, float)) or ppm < 0 or limit_ppm <= 0:
        raise DataValidationError("Invalid ppm or limit_ppm")
    return {"op": "check_pa_dye_concentration", "exceeds": float(ppm) > float(limit_ppm), "ppm": float(ppm), "src": "recallstorm/states/pa_synthetic_dyes.py"}


def flag_red40_yellow5_skus(ingredients: str) -> dict:
    """Flag ingredients containing Red 40, Yellow 5, Yellow 6, Blue 1, Blue 2, or Red 3."""
    _req(ingredients, "ingredients")
    up = str(ingredients).upper()
    flagged = any(d in up for d in ("RED 40", "RED #40", "YELLOW 5", "YELLOW 6", "BLUE 1", "BLUE 2", "RED 3", "RED #3"))
    return {"op": "flag_red40_yellow5_skus", "flagged": flagged, "src": "recallstorm/states/pa_synthetic_dyes.py"}


def evaluate_pa_school_zone_store(store_id: str, distance_m: float = 500.0) -> dict:
    """Evaluate if a PA store is within a school zone (< 1000m)."""
    _req(store_id, "store_id")
    if distance_m < 0:
        raise DataValidationError("distance_m cannot be negative")
    return {"op": "evaluate_pa_school_zone_store", "store_id": str(store_id), "in_zone": distance_m <= 1000.0, "src": "recallstorm/states/pa_synthetic_dyes.py"}


def verify_pa_warning_label_text(label_text: str) -> dict:
    """Verify presence of synthetic food dye warning text."""
    _req(label_text, "label_text")
    ok = "synthetic" in str(label_text).lower() or "warning" in str(label_text).lower()
    return {"op": "verify_pa_warning_label_text", "compliant": ok, "src": "recallstorm/states/pa_synthetic_dyes.py"}


def map_pa_affected_categories(category: str) -> dict:
    """Check if category is high-exposure confectionery/snacks in PA."""
    _req(category, "category")
    affected = any(k in str(category).lower() for k in ("candy", "snack", "beverage", "baking", "cereal"))
    return {"op": "map_pa_affected_categories", "affected": affected, "src": "recallstorm/states/pa_synthetic_dyes.py"}


def calculate_pa_pack_exposure(units: int, servings_per_unit: int = 4) -> int:
    """Calculate total child servings across units."""
    if units < 0 or servings_per_unit <= 0:
        raise DataValidationError("Invalid units or servings_per_unit")
    return int(units) * int(servings_per_unit)


def generate_pa_parent_advisory(store_id: str, sku_id: str) -> dict:
    """Generate a Pennsylvania consumer/parent advisory notice."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "generate_pa_parent_advisory", "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/states/pa_synthetic_dyes.py"}


def filter_pa_vending_inventory(skus: list[str]) -> list[str]:
    """Filter vending machine SKUs in PA."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def validate_pa_catering_menu(menu_name: str, dye_free: bool = True) -> dict:
    """Validate school/party catering menu dye-free status in PA."""
    _req(menu_name, "menu_name")
    return {"op": "validate_pa_catering_menu", "menu_name": str(menu_name), "approved": bool(dye_free), "src": "recallstorm/states/pa_synthetic_dyes.py"}


def audit_pa_confectionery_endcaps(store_id: str, endcap_count: int = 2) -> dict:
    """Audit confectionery endcaps in PA stores."""
    _req(store_id, "store_id")
    if endcap_count < 0:
        raise DataValidationError("endcap_count must be non-negative")
    return {"op": "audit_pa_confectionery_endcaps", "store_id": str(store_id), "endcap_count": int(endcap_count), "src": "recallstorm/states/pa_synthetic_dyes.py"}
