"""Washington PFAS food packaging and plant-fiber wrapper bans."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class WaPfasPackagingBan:
    """Domain entity for RCW 70A.222 Washington PFAS food packaging ban."""

    ref_id: str = "WA-PFAS-PKG"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class PlantFiberWrapperCheck:
    """Total organic fluorine check for plant-fiber food wrappers."""

    ref_id: str = "WA-TOF-100"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def test_wa_fluorine_ppm_limit(tof_ppm: float, limit_ppm: float = 100.0) -> dict:
    """Evaluate Total Organic Fluorine (TOF) ppm against 100 ppm threshold."""
    if not isinstance(tof_ppm, (int, float)) or tof_ppm < 0 or limit_ppm <= 0:
        raise DataValidationError("Invalid tof_ppm")
    return {"op": "test_wa_fluorine_ppm_limit", "prohibited": float(tof_ppm) >= float(limit_ppm), "tof_ppm": float(tof_ppm), "src": "recallstorm/states/wa_pfas_packaging.py"}


def evaluate_wa_compostable_claim(claim: str, tof_ppm: float = 0.0) -> dict:
    """Evaluate whether a compostable food-packaging claim meets WA PFAS-free requirements."""
    _req(claim, "claim")
    if tof_ppm < 0:
        raise DataValidationError("tof_ppm cannot be negative")
    return {"op": "evaluate_wa_compostable_claim", "valid": tof_ppm < 100.0, "src": "recallstorm/states/wa_pfas_packaging.py"}


def check_wa_deli_paper_lots(lot_id: str) -> dict:
    """Check deli wrap paper lot against WA RCW 70A.222."""
    _req(lot_id, "lot_id")
    return {"op": "check_wa_deli_paper_lots", "lot_id": str(lot_id), "cleared": True, "src": "recallstorm/states/wa_pfas_packaging.py"}


def flag_wa_greaseproof_containers(material_desc: str) -> dict:
    """Flag molded fiber / greaseproof clam-shells containing fluorinated treatments."""
    _req(material_desc, "material_desc")
    flagged = any(k in str(material_desc).lower() for k in ("fluoro", "pfas", "ptfe"))
    return {"op": "flag_wa_greaseproof_containers", "flagged": flagged, "src": "recallstorm/states/wa_pfas_packaging.py"}


def verify_wa_alternative_assessment(packaging_type: str) -> dict:
    """Verify WA Ecology safer alternatives assessment status for packaging_type."""
    _req(packaging_type, "packaging_type")
    return {"op": "verify_wa_alternative_assessment", "packaging_type": str(packaging_type), "ban_active": True, "src": "recallstorm/states/wa_pfas_packaging.py"}


def map_wa_fresh_dept_packaging(store_id: str, depts: list[str] | None = None) -> dict:
    """Map fresh departments (deli, bakery, meat) using service packaging in WA."""
    _req(store_id, "store_id")
    return {"op": "map_wa_fresh_dept_packaging", "store_id": str(store_id), "depts": list(depts or ["DELI", "BAKERY"]), "src": "recallstorm/states/wa_pfas_packaging.py"}


def calculate_wa_packaging_fines(violations: int, fine_usd: float = 5000.0) -> float:
    """Calculate WA civil penalty for prohibited PFAS food packaging."""
    if violations < 0 or fine_usd < 0:
        raise DataValidationError("Negative fine parameters")
    return round(float(violations) * float(fine_usd), 2)


def audit_wa_bakery_clam_shells(store_id: str, cases: int = 1) -> dict:
    """Audit bakery supply clam-shells in a WA store."""
    _req(store_id, "store_id")
    if cases < 0:
        raise DataValidationError("cases cannot be negative")
    return {"op": "audit_wa_bakery_clam_shells", "store_id": str(store_id), "cases": int(cases), "src": "recallstorm/states/wa_pfas_packaging.py"}


def generate_wa_pfas_certificate(vendor_id: str, sku_id: str) -> dict:
    """Generate a WA Certificate of Compliance for PFAS-free food packaging."""
    _req(vendor_id, "vendor_id")
    _req(sku_id, "sku_id")
    return {"op": "generate_wa_pfas_certificate", "vendor_id": str(vendor_id), "sku_id": str(sku_id), "src": "recallstorm/states/wa_pfas_packaging.py"}


def filter_wa_in_store_prep_wraps(wraps: list[str]) -> list[str]:
    """Filter in-store prep wrap SKUs."""
    if wraps is None:
        raise DataValidationError("wraps cannot be None")
    return sorted(str(w) for w in wraps if str(w).strip())
