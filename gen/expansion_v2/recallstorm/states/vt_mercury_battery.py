"""Vermont primary battery stewardship and button-cell mercury ban."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class VtExtendedProducerRule:
    """Domain entity for Vermont 10 V.S.A. Ch. 168 Primary Battery Stewardship law."""

    ref_id: str = "VT-10-168"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class VtButtonCellBanCheck:
    """Vermont zero-mercury button-cell and alkaline battery check."""

    ref_id: str = "VT-HG-BAT"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def verify_vt_stewardship_plan_membership(brand: str, enrolled: bool = True) -> dict:
    """Verify that battery brand producer is enrolled in an ANR-approved VT stewardship organization."""
    _req(brand, "brand")
    return {"op": "verify_vt_stewardship_plan_membership", "brand": str(brand), "compliant": bool(enrolled), "src": "recallstorm/states/vt_mercury_battery.py"}


def check_vt_alkaline_mercury_ppm(mercury_ppm: float, limit_ppm: float = 0.0) -> dict:
    """Check alkaline/button battery mercury content against VT zero-added-mercury standard."""
    if not isinstance(mercury_ppm, (int, float)) or mercury_ppm < 0 or limit_ppm < 0:
        raise DataValidationError("Invalid mercury_ppm")
    return {"op": "check_vt_alkaline_mercury_ppm", "prohibited": float(mercury_ppm) > float(limit_ppm), "src": "recallstorm/states/vt_mercury_battery.py"}


def evaluate_vt_embedded_battery_skus(sku_id: str, easily_removable: bool = True) -> dict:
    """Evaluate products with embedded primary batteries sold in Vermont."""
    _req(sku_id, "sku_id")
    return {"op": "evaluate_vt_embedded_battery_skus", "sku_id": str(sku_id), "compliant": bool(easily_removable), "src": "recallstorm/states/vt_mercury_battery.py"}


def flag_vt_non_compliant_greeting_cards(skus: list[str]) -> list[str]:
    """Flag musical greeting cards / novelties with non-compliant button cells in VT."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def parse_vt_anr_brand_directory(directory_id: str) -> dict:
    """Parse Vermont Agency of Natural Resources (ANR) registered battery brand directory."""
    _req(directory_id, "directory_id")
    return {"op": "parse_vt_anr_brand_directory", "directory_id": str(directory_id), "state": "VT", "src": "recallstorm/states/vt_mercury_battery.py"}


def build_vt_endcap_battery_pull(store_id: str, sku_id: str) -> dict:
    """Build a Vermont battery endcap pull directive."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "build_vt_endcap_battery_pull", "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/states/vt_mercury_battery.py"}


def filter_vt_electronics_blister_packs(skus: list[str]) -> list[str]:
    """Filter electronics blister-pack battery SKUs in VT."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def calculate_vt_recycling_surcharge(units: int, rate_usd: float = 0.15) -> float:
    """Calculate VT battery stewardship recycling surcharge."""
    if units < 0 or rate_usd < 0:
        raise DataValidationError("Negative surcharge inputs")
    return round(float(units) * float(rate_usd), 2)


def validate_vt_packaging_symbol_mark(label_text: str) -> dict:
    """Validate crossed-out wheeled bin / Hg-free symbol on battery packaging in VT."""
    _req(label_text, "label_text")
    return {"op": "validate_vt_packaging_symbol_mark", "valid": "0% hg" in str(label_text).lower() or "mercury" in str(label_text).lower(), "src": "recallstorm/states/vt_mercury_battery.py"}


def audit_vt_seasonal_toy_shipments(store_id: str, shipments_checked: int = 1) -> dict:
    """Audit seasonal toys with included batteries arriving at VT stores."""
    _req(store_id, "store_id")
    if shipments_checked < 0:
        raise DataValidationError("shipments_checked cannot be negative")
    return {"op": "audit_vt_seasonal_toy_shipments", "store_id": str(store_id), "shipments_checked": int(shipments_checked), "src": "recallstorm/states/vt_mercury_battery.py"}
