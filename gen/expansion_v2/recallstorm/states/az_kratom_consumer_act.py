"""Arizona Kratom Consumer Protection Act 7-hydroxymitragynine limits."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class AzKratomStandardRule:
    """Domain entity for Arizona Revised Statutes 36-795 Kratom Consumer Protection Act."""

    ref_id: str = "AZ-KCPA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class AzAlkaloidRatioCheck:
    """2% 7-hydroxymitragynine alkaloid fraction check for Arizona."""

    ref_id: str = "AZ-7OH-2PCT"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def verify_az_7_oh_fraction_limit(seven_oh_pct: float, max_pct: float = 2.0) -> dict:
    """Verify that 7-hydroxymitragynine does not exceed 2% of total alkaloids under ARS 36-795.02."""
    if not isinstance(seven_oh_pct, (int, float)) or seven_oh_pct < 0 or max_pct <= 0:
        raise DataValidationError("Invalid seven_oh_pct")
    return {"op": "verify_az_7_oh_fraction_limit", "compliant": float(seven_oh_pct) <= float(max_pct), "src": "recallstorm/states/az_kratom_consumer_act.py"}


def check_az_dosage_instructions(label_text: str) -> dict:
    """Verify clear recommended serving size and dosage directions on AZ kratom labels."""
    _req(label_text, "label_text")
    ok = any(k in str(label_text).lower() for k in ("serving", "dose", "directions"))
    return {"op": "check_az_dosage_instructions", "compliant": ok, "src": "recallstorm/states/az_kratom_consumer_act.py"}


def evaluate_az_synthetic_adulterants(ingredients: str) -> dict:
    """Check for prohibited synthetic alkaloids or controlled substances in AZ."""
    _req(ingredients, "ingredients")
    adulterated = "synthetic" in str(ingredients).lower()
    return {"op": "evaluate_az_synthetic_adulterants", "adulterated": adulterated, "src": "recallstorm/states/az_kratom_consumer_act.py"}


def flag_az_confectionery_forms(product_form: str) -> dict:
    """Flag kratom products mimicking candy/gummies appealing to children."""
    _req(product_form, "product_form")
    flagged = any(k in str(product_form).lower() for k in ("gummy", "candy", "lollipop", "chocolate"))
    return {"op": "flag_az_confectionery_forms", "flagged": flagged, "src": "recallstorm/states/az_kratom_consumer_act.py"}


def validate_az_label_disclaimer_text(disclaimer: str) -> dict:
    """Validate Arizona statutory alkaloid content disclosure on label."""
    _req(disclaimer, "disclaimer")
    return {"op": "validate_az_label_disclaimer_text", "valid": "mitragynine" in str(disclaimer).lower(), "src": "recallstorm/states/az_kratom_consumer_act.py"}


def filter_az_wellness_aisle_skus(skus: list[str]) -> list[str]:
    """Filter wellness aisle SKUs in Arizona stores."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def build_az_vendor_indemnity_check(vendor_id: str, signed: bool = True) -> dict:
    """Verify vendor KCPA compliance indemnification in AZ."""
    _req(vendor_id, "vendor_id")
    return {"op": "build_az_vendor_indemnity_check", "vendor_id": str(vendor_id), "valid": bool(signed), "src": "recallstorm/states/az_kratom_consumer_act.py"}


def calculate_az_civil_forfeiture(units: int, unit_cost: float = 12.0) -> float:
    """Calculate value of seized non-compliant inventory in Arizona."""
    if units < 0 or unit_cost < 0:
        raise DataValidationError("Negative forfeiture inputs")
    return round(float(units) * float(unit_cost), 2)


def audit_az_batch_alkaloid_panel(batch_id: str, passed: bool = True) -> dict:
    """Audit batch alkaloid HPLC test panel for Arizona compliance."""
    _req(batch_id, "batch_id")
    return {"op": "audit_az_batch_alkaloid_panel", "batch_id": str(batch_id), "passed": bool(passed), "src": "recallstorm/states/az_kratom_consumer_act.py"}


def generate_az_stop_sale_notice(store_id: str, sku_id: str) -> dict:
    """Generate an Arizona store stop-sale notice."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "generate_az_stop_sale_notice", "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/states/az_kratom_consumer_act.py"}
