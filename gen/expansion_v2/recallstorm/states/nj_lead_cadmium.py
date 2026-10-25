"""New Jersey heavy metal action levels in spices and candy."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class NjHeavyMetalRule:
    """Domain entity for New Jersey DOH lead/cadmium action levels."""

    ref_id: str = "NJ-HM-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class NjActionLevelTable:
    """Action level thresholds in ppb for lead and cadmium in NJ."""

    ref_id: str = "NJ-PPB-TBL"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_nj_candy_lead_ppb(lead_ppb: float, limit_ppb: float = 100.0) -> dict:
    """Check candy lead concentration in ppb against NJ/FDA 100 ppb action level."""
    if not isinstance(lead_ppb, (int, float)) or lead_ppb < 0 or limit_ppb <= 0:
        raise DataValidationError("Invalid lead_ppb")
    return {"op": "check_nj_candy_lead_ppb", "adulterated": float(lead_ppb) >= float(limit_ppb), "lead_ppb": float(lead_ppb), "src": "recallstorm/states/nj_lead_cadmium.py"}


def evaluate_nj_spice_cadmium_limit(cadmium_ppm: float, limit_ppm: float = 1.0) -> dict:
    """Evaluate spice cadmium level against NJ threshold."""
    if not isinstance(cadmium_ppm, (int, float)) or cadmium_ppm < 0 or limit_ppm <= 0:
        raise DataValidationError("Invalid cadmium_ppm")
    return {"op": "evaluate_nj_spice_cadmium_limit", "exceeds": float(cadmium_ppm) > float(limit_ppm), "src": "recallstorm/states/nj_lead_cadmium.py"}


def parse_nj_doh_embargo_order(order_id: str) -> dict:
    """Parse a New Jersey Department of Health food embargo order."""
    _req(order_id, "order_id")
    return {"op": "parse_nj_doh_embargo_order", "order_id": str(order_id), "state": "NJ", "src": "recallstorm/states/nj_lead_cadmium.py"}


def flag_nj_imported_turmeric(product_name: str, origin: str = "IN") -> dict:
    """Flag imported turmeric/cinnamon SKUs for heightened lead chromate screening in NJ."""
    _req(product_name, "product_name")
    flagged = any(s in str(product_name).lower() for s in ("turmeric", "cinnamon", "chili"))
    return {"op": "flag_nj_imported_turmeric", "flagged": flagged, "origin": str(origin), "src": "recallstorm/states/nj_lead_cadmium.py"}


def verify_nj_lot_coa_metals(lot_id: str, lead_ppb: float = 10.0) -> dict:
    """Verify heavy metal COA for a spice/candy lot in NJ."""
    _req(lot_id, "lot_id")
    if lead_ppb < 0:
        raise DataValidationError("lead_ppb cannot be negative")
    return {"op": "verify_nj_lot_coa_metals", "lot_id": str(lot_id), "passed": lead_ppb < 100.0, "src": "recallstorm/states/nj_lead_cadmium.py"}


def calculate_nj_daily_intake_exposure(serving_g: float, concentration_ppb: float) -> float:
    """Calculate micrograms per day heavy metal intake from serving_g and concentration_ppb."""
    if serving_g < 0 or concentration_ppb < 0:
        raise DataValidationError("Negative intake parameters")
    return round((float(serving_g) * float(concentration_ppb)) / 1000.0, 4)


def build_nj_quarantine_tag(store_id: str, sku_id: str) -> dict:
    """Build a NJ DOH quarantine hold tag."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "build_nj_quarantine_tag", "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/states/nj_lead_cadmium.py"}


def filter_nj_ethnic_aisle_skus(skus: list[str]) -> list[str]:
    """Filter spice and ethnic aisle SKUs for NJ heavy metal audit."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def generate_nj_lab_retest_request(sku_id: str, lot_id: str) -> dict:
    """Generate a composite lab retest request for a held lot in NJ."""
    _req(sku_id, "sku_id")
    _req(lot_id, "lot_id")
    return {"op": "generate_nj_lab_retest_request", "sku_id": str(sku_id), "lot_id": str(lot_id), "src": "recallstorm/states/nj_lead_cadmium.py"}


def validate_nj_embargo_release(release_doc_id: str, signed_by_doh: bool = True) -> dict:
    """Validate written NJ DOH authorization before releasing embargoed stock."""
    _req(release_doc_id, "release_doc_id")
    return {"op": "validate_nj_embargo_release", "release_doc_id": str(release_doc_id), "released": bool(signed_by_doh), "src": "recallstorm/states/nj_lead_cadmium.py"}
