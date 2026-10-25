"""NY food additive restrictions and Titanium Dioxide evaluations."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class NyAdditiveRule:
    """Domain entity for New York food additive legislation."""

    ref_id: str = "NY-ADD-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class TitaniumDioxideCheck:
    """Titanium Dioxide (E171) screening record for NY compliance."""

    ref_id: str = "NY-TIO2-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _check_arg(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}: cannot be None or empty")


def check_ny_ban_date(as_of_iso: str, effective_iso: str = "2027-01-01") -> dict:
    """Check whether as_of_iso is on or after the NY statutory ban date."""
    _check_arg(as_of_iso, "as_of_iso")
    prohibited = str(as_of_iso) >= str(effective_iso)
    return {"op": "check_ny_ban_date", "prohibited": prohibited, "effective": effective_iso, "src": "recallstorm/states/ny_food_additives.py"}


def evaluate_tio2_exemption(category: str, is_Import: bool = False) -> dict:
    """Evaluate whether a product category qualifies for a NY TiO2 exemption."""
    _check_arg(category, "category")
    exempt = "pharmaceutical" in str(category).lower() and not is_Import
    return {"op": "evaluate_tio2_exemption", "category": str(category), "exempt": exempt, "src": "recallstorm/states/ny_food_additives.py"}


def parse_ny_senate_bill(bill_text: str) -> dict:
    """Parse NY Senate bill text for prohibited additive clauses."""
    _check_arg(bill_text, "bill_text")
    has_tio2 = "titanium dioxide" in str(bill_text).lower()
    return {"op": "parse_ny_senate_bill", "has_tio2": has_tio2, "length": len(str(bill_text)), "src": "recallstorm/states/ny_food_additives.py"}


def build_ny_violation_record(sku_id: str, additive: str = "TITANIUM_DIOXIDE") -> dict:
    """Build a NY statutory food additive violation record."""
    _check_arg(sku_id, "sku_id")
    return {"op": "build_ny_violation_record", "sku_id": str(sku_id), "additive": additive, "state": "NY", "src": "recallstorm/states/ny_food_additives.py"}


def filter_ny_store_zips(zips: list[str]) -> list[str]:
    """Filter ZIP codes to NY prefixes (10xxx-14xxx)."""
    if zips is None:
        raise DataValidationError("zips cannot be None")
    return [z for z in zips if str(z).startswith(("10", "11", "12", "13", "14"))]


def map_ny_ingredient_aliases(additive: str) -> list[str]:
    """Return NY statutory aliases for an additive."""
    _check_arg(additive, "additive")
    if "tio2" in str(additive).lower() or "titanium" in str(additive).lower():
        return ["titanium dioxide", "E171", "CI 77891"]
    return [str(additive).lower()]


def calculate_ny_civil_penalty(violations: int, repeat: bool = False) -> float:
    """Calculate NY civil penalty in USD for additive violations."""
    if not isinstance(violations, (int, float)) or violations < 0:
        raise DataValidationError("violations must be non-negative")
    rate = 1000.0 if repeat else 500.0
    return round(float(violations) * rate, 2)


def exempt_ny_in_transit_stock(bol_id: str, destination_state: str = "NJ") -> dict:
    """Check interstate commerce transit exemption through NY."""
    _check_arg(bol_id, "bol_id")
    exempt = str(destination_state).upper() != "NY"
    return {"op": "exempt_ny_in_transit_stock", "bol_id": str(bol_id), "exempt": exempt, "src": "recallstorm/states/ny_food_additives.py"}


def generate_ny_compliance_memo(store_id: str, sku_count: int = 1) -> dict:
    """Generate a NY store compliance memo."""
    _check_arg(store_id, "store_id")
    return {"op": "generate_ny_compliance_memo", "store_id": str(store_id), "sku_count": int(sku_count), "src": "recallstorm/states/ny_food_additives.py"}


def validate_ny_label_claim(claim_text: str) -> dict:
    """Validate a NY additive-free label claim."""
    _check_arg(claim_text, "claim_text")
    valid = "artificial" not in str(claim_text).lower()
    return {"op": "validate_ny_label_claim", "valid": valid, "claim": str(claim_text), "src": "recallstorm/states/ny_food_additives.py"}
