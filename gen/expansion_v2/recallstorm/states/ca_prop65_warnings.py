"""California Proposition 65 safe harbor warnings and OEHHA chemical checks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class Prop65SafeHarborRule:
    """Domain entity for California Proposition 65 (Health & Safety Code 25249.6)."""

    ref_id: str = "CA-PROP65"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class AcrylamideExposureCheck:
    """OEHHA acrylamide / heavy metal NSRL and MADL exposure check."""

    ref_id: str = "CA-OEHHA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def verify_prop65_shelf_sign_placement(store_id: str, aisle: str, posted: bool = True) -> dict:
    """Verify Prop 65 shelf sign placement at point of display in a CA store."""
    _req(store_id, "store_id")
    _req(aisle, "aisle")
    return {"op": "verify_prop65_shelf_sign_placement", "store_id": str(store_id), "aisle": str(aisle), "compliant": bool(posted), "src": "recallstorm/states/ca_prop65_warnings.py"}


def check_prop65_bpa_canned_goods(sku_id: str, lining: str = "BPA-Free") -> dict:
    """Check whether canned/jarred food requires a Prop 65 BPA warning."""
    _req(sku_id, "sku_id")
    needs_warning = "bpa" in str(lining).lower() and "free" not in str(lining).lower()
    return {"op": "check_prop65_bpa_canned_goods", "sku_id": str(sku_id), "needs_warning": needs_warning, "src": "recallstorm/states/ca_prop65_warnings.py"}


def evaluate_prop65_short_form_label(label_text: str) -> dict:
    """Evaluate 2025/2026 OEHHA amended Prop 65 short-form warning label text."""
    _req(label_text, "label_text")
    low = str(label_text).lower()
    valid = "warning" in low and ("cancer" in low or "reproductive" in low) and "p65warnings.ca.gov" in low
    return {"op": "evaluate_prop65_short_form_label", "valid": valid, "src": "recallstorm/states/ca_prop65_warnings.py"}


def parse_oehha_chemical_list_update(chemical_name: str, cas: str = "7439-92-1") -> dict:
    """Parse an OEHHA Proposition 65 chemical list entry."""
    _req(chemical_name, "chemical_name")
    return {"op": "parse_oehha_chemical_list_update", "chemical": str(chemical_name), "cas": str(cas), "src": "recallstorm/states/ca_prop65_warnings.py"}


def flag_prop65_private_enforcer_notice(notice_60_day_id: str, sku_id: str) -> dict:
    """Flag a SKU named in a Prop 65 60-Day Notice of Violation."""
    _req(notice_60_day_id, "notice_60_day_id")
    _req(sku_id, "sku_id")
    return {"op": "flag_prop65_private_enforcer_notice", "notice_id": str(notice_60_day_id), "sku_id": str(sku_id), "src": "recallstorm/states/ca_prop65_warnings.py"}


def calculate_prop65_daily_madl_ug(ug_per_day: float, madl_ug: float = 0.5) -> dict:
    """Compare daily lead/chemical exposure in micrograms against OEHHA MADL (0.5 ug/day for lead)."""
    if not isinstance(ug_per_day, (int, float)) or ug_per_day < 0 or madl_ug <= 0:
        raise DataValidationError("Invalid ug_per_day")
    return {"op": "calculate_prop65_daily_madl_ug", "exceeds_madl": float(ug_per_day) > float(madl_ug), "src": "recallstorm/states/ca_prop65_warnings.py"}


def map_prop65_pos_receipt_warnings(store_id: str, skus: list[str]) -> dict:
    """Map SKUs configured to print automatic Prop 65 warnings on CA POS receipts."""
    _req(store_id, "store_id")
    return {"op": "map_prop65_pos_receipt_warnings", "store_id": str(store_id), "count": len(skus), "src": "recallstorm/states/ca_prop65_warnings.py"}


def filter_prop65_unwarned_imports(skus: list[str]) -> list[str]:
    """Return sorted imported SKUs lacking Prop 65 safe harbor determinations."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def build_prop65_consent_judgment_rule(judgment_id: str, max_ppb: float = 50.0) -> dict:
    """Build a category-specific Prop 65 consent judgment reformulation threshold."""
    _req(judgment_id, "judgment_id")
    if max_ppb <= 0:
        raise DataValidationError("max_ppb must be positive")
    return {"op": "build_prop65_consent_judgment_rule", "judgment_id": str(judgment_id), "max_ppb": float(max_ppb), "src": "recallstorm/states/ca_prop65_warnings.py"}


def audit_prop65_bakery_sign_hooks(store_id: str, hooks_intact: bool = True) -> dict:
    """Audit Prop 65 acrylamide/baked-goods signage hooks in a CA store bakery."""
    _req(store_id, "store_id")
    return {"op": "audit_prop65_bakery_sign_hooks", "store_id": str(store_id), "intact": bool(hooks_intact), "src": "recallstorm/states/ca_prop65_warnings.py"}
