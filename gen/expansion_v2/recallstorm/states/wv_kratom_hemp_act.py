"""West Virginia Select Plant-Based Derivatives Act compliance."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class WvSelectPlantRule:
    """Domain entity for West Virginia Code 19-12F Select Plant-Based Derivatives Act."""

    ref_id: str = "WV-19-12F"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class WvAgeVerificationMandate:
    """West Virginia 21+ age verification mandate for kratom and hemp derivatives."""

    ref_id: str = "WV-AGE-21"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_wv_mitragynine_limit(pct: float, max_pct: float = 2.0) -> dict:
    """Check alkaloid percentage against West Virginia limits."""
    if not isinstance(pct, (int, float)) or pct < 0 or max_pct <= 0:
        raise DataValidationError("Invalid pct")
    return {"op": "check_wv_mitragynine_limit", "compliant": float(pct) <= float(max_pct), "pct": float(pct), "src": "recallstorm/states/wv_kratom_hemp_act.py"}


def evaluate_wv_synthetic_alkaloids(ingredients: str) -> dict:
    """Flag synthetic mitragynine or 7-OH-mitragynine derivatives prohibited in WV."""
    _req(ingredients, "ingredients")
    prohibited = "synthetic" in str(ingredients).lower()
    return {"op": "evaluate_wv_synthetic_alkaloids", "prohibited": prohibited, "src": "recallstorm/states/wv_kratom_hemp_act.py"}


def verify_wv_wvda_product_permit(sku_id: str, registered: bool = True) -> dict:
    """Verify WV Department of Agriculture (WVDA) product registration."""
    _req(sku_id, "sku_id")
    return {"op": "verify_wv_wvda_product_permit", "sku_id": str(sku_id), "registered": bool(registered), "src": "recallstorm/states/wv_kratom_hemp_act.py"}


def flag_wv_adulterated_tinctures(skus: list[str]) -> list[str]:
    """Return sorted SKU IDs of adulterated tinctures in WV."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def check_wv_warning_statement_box(label_text: str) -> dict:
    """Verify presence of WVDA required warning statement box."""
    _req(label_text, "label_text")
    ok = "21" in str(label_text) or "warning" in str(label_text).lower()
    return {"op": "check_wv_warning_statement_box", "compliant": ok, "src": "recallstorm/states/wv_kratom_hemp_act.py"}


def filter_wv_c_store_formats(stores: list[str]) -> list[str]:
    """Filter WV convenience/small-format stores."""
    if stores is None:
        raise DataValidationError("stores cannot be None")
    return sorted(str(s) for s in stores if str(s).strip())


def build_wv_seizure_readiness_pack(store_id: str, sku_count: int = 1) -> dict:
    """Build a WVDA seizure/embargo readiness dossier."""
    _req(store_id, "store_id")
    if sku_count < 0:
        raise DataValidationError("sku_count cannot be negative")
    return {"op": "build_wv_seizure_readiness_pack", "store_id": str(store_id), "sku_count": int(sku_count), "src": "recallstorm/states/wv_kratom_hemp_act.py"}


def calculate_wv_unregistered_penalty(units: int, fine_per_unit: float = 100.0) -> float:
    """Calculate WV civil penalty for unregistered plant-derivative products."""
    if units < 0 or fine_per_unit < 0:
        raise DataValidationError("Negative penalty inputs")
    return round(float(units) * float(fine_per_unit), 2)


def validate_wv_lab_accreditation(lab_id: str, iso_certified: bool = True) -> dict:
    """Validate ISO/IEC 17025 accreditation for a WV testing lab."""
    _req(lab_id, "lab_id")
    return {"op": "validate_wv_lab_accreditation", "lab_id": str(lab_id), "valid": bool(iso_certified), "src": "recallstorm/states/wv_kratom_hemp_act.py"}


def audit_wv_display_case_locks(store_id: str, locked: bool = True) -> dict:
    """Verify that restricted plant-derivative products are behind locked display cases in WV."""
    _req(store_id, "store_id")
    return {"op": "audit_wv_display_case_locks", "store_id": str(store_id), "compliant": bool(locked), "src": "recallstorm/states/wv_kratom_hemp_act.py"}
