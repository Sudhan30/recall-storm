"""Washington Toxic-Free Kids and Cosmetics Act chemical checks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class WaTfkcaRule:
    """Domain entity for Washington Children's Safe Products Act (CSPA)."""

    ref_id: str = "WA-CSPA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class HighPriorityChemicalList:
    """Washington Department of Ecology CHCC (Chemicals of High Concern to Children) list."""

    ref_id: str = "WA-CHCC-66"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_wa_phthalates_ppm(ppm: float, limit_ppm: float = 1000.0) -> dict:
    """Check ortho-phthalates concentration against WA 1000 ppm limit."""
    if not isinstance(ppm, (int, float)) or ppm < 0 or limit_ppm <= 0:
        raise DataValidationError("Invalid ppm")
    return {"op": "check_wa_phthalates_ppm", "violation": float(ppm) > float(limit_ppm), "ppm": float(ppm), "src": "recallstorm/states/wa_toxic_free_kids.py"}


def evaluate_wa_childrens_product(category: str, age_months: int = 24) -> dict:
    """Evaluate if an item is a children's product under WA CSPA (under age 12)."""
    _req(category, "category")
    if age_months < 0:
        raise DataValidationError("age_months must be non-negative")
    return {"op": "evaluate_wa_childrens_product", "in_scope": age_months < 144, "src": "recallstorm/states/wa_toxic_free_kids.py"}


def verify_wa_ecology_reporting(vendor_id: str, reported: bool = True) -> dict:
    """Verify WA Department of Ecology annual CHCC disclosure status."""
    _req(vendor_id, "vendor_id")
    return {"op": "verify_wa_ecology_reporting", "vendor_id": str(vendor_id), "compliant": bool(reported), "src": "recallstorm/states/wa_toxic_free_kids.py"}


def calculate_wa_de_minimis_threshold(contaminant_ppm: float, de_minimis_ppm: float = 100.0) -> dict:
    """Evaluate whether a manufacturing contaminant exceeds WA de minimis threshold."""
    if contaminant_ppm < 0 or de_minimis_ppm <= 0:
        raise DataValidationError("Invalid ppm")
    return {"op": "calculate_wa_de_minimis_threshold", "reportable": contaminant_ppm >= de_minimis_ppm, "src": "recallstorm/states/wa_toxic_free_kids.py"}


def flag_wa_bisphenol_packaging(packaging_material: str) -> dict:
    """Flag BPA/BPS/BPF bisphenol food/drink can linings in WA."""
    _req(packaging_material, "packaging_material")
    flagged = any(b in str(packaging_material).upper() for b in ("BPA", "BPS", "BPF", "BISPHENOL"))
    return {"op": "flag_wa_bisphenol_packaging", "flagged": flagged, "src": "recallstorm/states/wa_toxic_free_kids.py"}


def parse_wa_cspa_notice_list(notice_id: str) -> dict:
    """Parse a WA Ecology CSPA enforcement notice."""
    _req(notice_id, "notice_id")
    return {"op": "parse_wa_cspa_notice_list", "notice_id": str(notice_id), "state": "WA", "src": "recallstorm/states/wa_toxic_free_kids.py"}


def build_wa_Ecology_declaration(sku_id: str, cas_number: str = "84-74-2") -> dict:
    """Build a WA Department of Ecology chemical declaration record."""
    _req(sku_id, "sku_id")
    _req(cas_number, "cas_number")
    return {"op": "build_wa_Ecology_declaration", "sku_id": str(sku_id), "cas_number": str(cas_number), "src": "recallstorm/states/wa_toxic_free_kids.py"}


def filter_wa_baby_aisle_skus(skus: list[str]) -> list[str]:
    """Filter baby aisle SKU identifiers for WA audit."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def validate_wa_supplier_assay(lab_id: str, passed: bool = True) -> dict:
    """Validate supplier analytical assay for WA CHCC chemicals."""
    _req(lab_id, "lab_id")
    return {"op": "validate_wa_supplier_assay", "lab_id": str(lab_id), "passed": bool(passed), "src": "recallstorm/states/wa_toxic_free_kids.py"}


def generate_wa_recall_directive(store_id: str, sku_id: str) -> dict:
    """Generate a WA store pull directive for CSPA/TFKCA violations."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "generate_wa_recall_directive", "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/states/wa_toxic_free_kids.py"}
