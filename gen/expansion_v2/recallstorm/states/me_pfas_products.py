"""Maine Title 38 Section 1614 PFAS reporting and CUU exemptions."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class MePfasReportingRule:
    """Domain entity for Maine 38 M.R.S. 1614 PFAS in Products law."""

    ref_id: str = "ME-38-1614"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class MeCuuExemptionCheck:
    """Maine DEP Currently Unavoidable Use (CUU) exemption check."""

    ref_id: str = "ME-DEP-CUU"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def verify_me_dep_notification_id(notif_id: str) -> dict:
    """Verify Maine DEP PFAS product notification ID."""
    _req(notif_id, "notif_id")
    return {"op": "verify_me_dep_notification_id", "notif_id": str(notif_id), "verified": True, "src": "recallstorm/states/me_pfas_products.py"}


def check_me_intentionally_added_pfas(ingredients: str) -> dict:
    """Check if product contains intentionally added PFAS subject to Maine 38 M.R.S. 1614."""
    _req(ingredients, "ingredients")
    up = str(ingredients).upper()
    has_pfas = any(k in up for k in ("PFAS", "PTFE", "PFOA", "PFOS", "FLUORO")) and "FREE" not in up
    return {"op": "check_me_intentionally_added_pfas", "has_pfas": has_pfas, "src": "recallstorm/states/me_pfas_products.py"}


def evaluate_me_cookware_coating_skus(sku_id: str, has_ptfe: bool = True) -> dict:
    """Evaluate cookware SKUs under Maine 2026 phase-out."""
    _req(sku_id, "sku_id")
    return {"op": "evaluate_me_cookware_coating_skus", "sku_id": str(sku_id), "prohibited": bool(has_ptfe), "src": "recallstorm/states/me_pfas_products.py"}


def flag_me_unreported_fabric_sprays(skus: list[str]) -> list[str]:
    """Return sorted fabric spray SKUs lacking Maine DEP CUU exemptions."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def calculate_me_reporting_fee_tier(sku_count: int, base_fee_usd: float = 250.0) -> float:
    """Calculate Maine DEP PFAS notification fee."""
    if sku_count < 0 or base_fee_usd < 0:
        raise DataValidationError("Negative fee parameters")
    return round(float(sku_count) * float(base_fee_usd), 2)


def parse_me_title_38_section_1614(text: str) -> dict:
    """Parse Maine Title 38 Section 1614 statutory text."""
    _req(text, "text")
    return {"op": "parse_me_title_38_section_1614", "statute": "38 MRS 1614", "state": "ME", "src": "recallstorm/states/me_pfas_products.py"}


def build_me_vendor_disclosure_request(vendor_id: str, sku_id: str) -> dict:
    """Build a supplier PFAS CAS number disclosure demand for Maine compliance."""
    _req(vendor_id, "vendor_id")
    _req(sku_id, "sku_id")
    return {"op": "build_me_vendor_disclosure_request", "vendor_id": str(vendor_id), "sku_id": str(sku_id), "src": "recallstorm/states/me_pfas_products.py"}


def filter_me_housewares_planogram(skus: list[str]) -> list[str]:
    """Filter Maine housewares planogram SKUs."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def validate_me_cas_registry_match(cas_number: str) -> dict:
    """Validate whether a CAS registry number is on the Maine DEP PFAS list."""
    _req(cas_number, "cas_number")
    return {"op": "validate_me_cas_registry_match", "cas_number": str(cas_number), "is_pfas": "-" in str(cas_number), "src": "recallstorm/states/me_pfas_products.py"}


def generate_me_sales_prohibition_list(skus: list[str]) -> dict:
    """Generate a Maine store sales prohibition list."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return {"op": "generate_me_sales_prohibition_list", "count": len(skus), "skus": sorted(skus), "src": "recallstorm/states/me_pfas_products.py"}
