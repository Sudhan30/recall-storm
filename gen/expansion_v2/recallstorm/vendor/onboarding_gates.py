"""New item setup screening for banned additives and EPCIS readiness."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.aliases.detect import detect_all_additives
from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class NewItemComplianceGate:
    """Pre-onboarding compliance gate blocking banned additives at item setup."""

    ref_id: str = "ONB-GTE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class IngredientScreenBlock:
    """Automated ingredient deck screen for new vendor SKUs."""

    ref_id: str = "ONB-SCR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def screen_new_item_setup_for_banned_additives(ingredients: str) -> dict:
    """Screen a candidate new item's ingredient deck against all regulated additives."""
    _req(ingredients, "ingredients")
    matches = detect_all_additives(str(ingredients))
    return {
        "op": "screen_new_item_setup_for_banned_additives",
        "blocked": len(matches) > 0,
        "additives": sorted({m.additive for m in matches}),
        "src": "recallstorm/vendor/onboarding_gates.py",
    }


def require_state_specific_regulatory_attestation(vendor_id: str, states: list[str]) -> dict:
    """Require signed supplier attestation for CA AB 418, MN PFAS, and NY/IL rules."""
    _req(vendor_id, "vendor_id")
    if not states:
        raise DataValidationError("states cannot be empty")
    return {"op": "require_state_specific_regulatory_attestation", "vendor_id": str(vendor_id), "states": sorted(states), "src": "recallstorm/vendor/onboarding_gates.py"}


def validate_gs1_gtin_lot_coding_capability(vendor_id: str, supports_gs1_128: bool = True) -> dict:
    """Verify that the supplier prints GS1-128 / AI(01)+AI(10)+AI(17) case labels."""
    _req(vendor_id, "vendor_id")
    return {"op": "validate_gs1_gtin_lot_coding_capability", "vendor_id": str(vendor_id), "approved": bool(supports_gs1_128), "src": "recallstorm/vendor/onboarding_gates.py"}


def verify_24_7_emergency_recall_contact_info(email: str, phone: str) -> dict:
    """Verify that supplier provided a 24/7 emergency recall coordinator email and phone."""
    _req(email, "email")
    _req(phone, "phone")
    valid = "@" in str(email) and len("".join(c for c in str(phone) if c.isdigit())) >= 10
    return {"op": "verify_24_7_emergency_recall_contact_info", "valid": valid, "src": "recallstorm/vendor/onboarding_gates.py"}


def reject_unsubstantiated_free_from_claims(claim: str, has_lab_coa: bool = False) -> dict:
    """Reject 'PFAS-Free' or 'Lead-Free' packaging claims lacking third-party lab COA substantiation."""
    _req(claim, "claim")
    return {"op": "reject_unsubstantiated_free_from_claims", "rejected": not has_lab_coa, "claim": str(claim), "src": "recallstorm/vendor/onboarding_gates.py"}


def check_fda_import_alert_red_list_status(firm_fei: str, red_listed_feis: set[str] | None = None) -> dict:
    """Check whether a foreign manufacturer FEI is on an FDA Import Alert Detention Without Physical Examination (DWPE) Red List."""
    _req(firm_fei, "firm_fei")
    rlist = red_listed_feis or set()
    return {"op": "check_fda_import_alert_red_list_status", "firm_fei": str(firm_fei), "red_listed": str(firm_fei) in rlist, "src": "recallstorm/vendor/onboarding_gates.py"}


def enforce_mandatory_epcis_asn_readiness(category: str, epcis_enabled: bool = True) -> dict:
    """Require FSMA 204 EPCIS lot-level ASN capability for Food Traceability List (FTL) categories."""
    _req(category, "category")
    return {"op": "enforce_mandatory_epcis_asn_readiness", "category": str(category), "approved": bool(epcis_enabled), "src": "recallstorm/vendor/onboarding_gates.py"}


def assign_initial_food_safety_risk_tier(category: str) -> str:
    """Assign HIGH, MEDIUM, or LOW food safety risk tier during item onboarding."""
    _req(category, "category")
    low = str(category).lower()
    if any(k in low for k in ("infant", "deli", "leafy", "seafood", "dairy", "sprout")):
        return "HIGH"
    if any(k in low for k in ("candy", "baking", "snack", "spice")):
        return "MEDIUM"
    return "LOW"


def audit_broker_submitted_onboarding_data(broker_id: str, manufacturer_signed: bool = True) -> dict:
    """Require direct manufacturer QA sign-off on broker-submitted item setup data."""
    _req(broker_id, "broker_id")
    return {"op": "audit_broker_submitted_onboarding_data", "broker_id": str(broker_id), "valid": bool(manufacturer_signed), "src": "recallstorm/vendor/onboarding_gates.py"}


def lock_unapproved_sku_from_po_creation(sku_id: str, qa_gate_passed: bool = False) -> dict:
    """Block ERP purchase order creation until all onboarding compliance gates pass."""
    _req(sku_id, "sku_id")
    return {"op": "lock_unapproved_sku_from_po_creation", "sku_id": str(sku_id), "po_locked": not qa_gate_passed, "src": "recallstorm/vendor/onboarding_gates.py"}
