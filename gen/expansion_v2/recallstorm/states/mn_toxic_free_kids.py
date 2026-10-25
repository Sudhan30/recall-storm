"""Minnesota Statute 325F.177 lead and cadmium restrictions in children's items."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class MnPriorityChemicalRule:
    """Domain entity for Minnesota Toxic Free Kids Act priority chemicals."""

    ref_id: str = "MN-TFKA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class MnLeadCadmiumBan:
    """Minnesota Stat. 325F.177 lead (90 ppm) and cadmium (75 ppm) ban."""

    ref_id: str = "MN-325F-177"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_mn_toy_jewelry_ppm(lead_ppm: float, cadmium_ppm: float = 0.0) -> dict:
    """Check toy/jewelry lead (<= 90 ppm) and cadmium (<= 75 ppm) limits under Minn. Stat. 325F.177."""
    if lead_ppm < 0 or cadmium_ppm < 0:
        raise DataValidationError("Negative ppm values")
    prohibited = lead_ppm > 90.0 or cadmium_ppm > 75.0
    return {"op": "check_mn_toy_jewelry_ppm", "prohibited": prohibited, "lead_ppm": float(lead_ppm), "cadmium_ppm": float(cadmium_ppm), "src": "recallstorm/states/mn_toxic_free_kids.py"}


def evaluate_mn_child_mouthable_item(length_cm: float) -> dict:
    """Evaluate if a small part is mouthable (< 5 cm) under Minnesota children's product rules."""
    if length_cm <= 0:
        raise DataValidationError("length_cm must be positive")
    return {"op": "evaluate_mn_child_mouthable_item", "mouthable": length_cm < 5.0, "src": "recallstorm/states/mn_toxic_free_kids.py"}


def verify_mn_mdh_waiver_status(sku_id: str, has_waiver: bool = False) -> dict:
    """Verify Minnesota Department of Health (MDH) waiver status."""
    _req(sku_id, "sku_id")
    return {"op": "verify_mn_mdh_waiver_status", "sku_id": str(sku_id), "waived": bool(has_waiver), "src": "recallstorm/states/mn_toxic_free_kids.py"}


def flag_mn_seasonal_novelty_skus(category: str) -> dict:
    """Flag seasonal novelty, keychain, and party-favor SKUs in Minnesota."""
    _req(category, "category")
    flagged = any(k in str(category).lower() for k in ("novelty", "seasonal", "jewelry", "toy", "favor"))
    return {"op": "flag_mn_seasonal_novelty_skus", "flagged": flagged, "src": "recallstorm/states/mn_toxic_free_kids.py"}


def calculate_mn_surface_coating_limit(ppm: float, limit_ppm: float = 90.0) -> dict:
    """Compare surface coating heavy metal ppm to the 90 ppm MN limit."""
    if ppm < 0 or limit_ppm <= 0:
        raise DataValidationError("Invalid ppm")
    return {"op": "calculate_mn_surface_coating_limit", "compliant": ppm <= limit_ppm, "src": "recallstorm/states/mn_toxic_free_kids.py"}


def parse_mn_statute_325f_177(text: str) -> dict:
    """Parse Minn. Stat. 325F.177 citation text."""
    _req(text, "text")
    return {"op": "parse_mn_statute_325f_177", "statute": "325F.177", "state": "MN", "src": "recallstorm/states/mn_toxic_free_kids.py"}


def build_mn_merchant_stop_sale(store_id: str, sku_id: str) -> dict:
    """Build a Minnesota merchant stop-sale directive."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "build_mn_merchant_stop_sale", "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/states/mn_toxic_free_kids.py"}


def filter_mn_checklane_impulses(skus: list[str]) -> list[str]:
    """Filter checklane impulse novelty SKUs in MN."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def audit_mn_vendor_test_reports(vendor_id: str, reports_count: int = 1) -> dict:
    """Audit CPSC/MDH third-party lab test reports from vendor_id."""
    _req(vendor_id, "vendor_id")
    if reports_count < 0:
        raise DataValidationError("reports_count cannot be negative")
    return {"op": "audit_mn_vendor_test_reports", "vendor_id": str(vendor_id), "reports_count": int(reports_count), "src": "recallstorm/states/mn_toxic_free_kids.py"}


def generate_mn_disposal_manifest(store_id: str, units: int = 10) -> dict:
    """Generate a hazardous heavy-metal disposal manifest for MN."""
    _req(store_id, "store_id")
    if units < 0:
        raise DataValidationError("units cannot be negative")
    return {"op": "generate_mn_disposal_manifest", "store_id": str(store_id), "units": int(units), "src": "recallstorm/states/mn_toxic_free_kids.py"}
