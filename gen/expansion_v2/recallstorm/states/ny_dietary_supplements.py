"""NY age-gated weight-loss and muscle-building dietary supplement rules."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class NySupplementAgeGate:
    """Configuration for NY General Business Law 391-oo 18+ supplement age gate."""

    ref_id: str = "NY-SUPP-18"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class WeightLossClaimMatcher:
    """Matcher for weight-loss and muscle-building marketing claims."""

    ref_id: str = "NY-CLAIM-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _check(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def is_restricted_ny_supplement(text: str, category: str = "supplement") -> bool:
    """Return True if a supplement makes restricted weight-loss or muscle-building claims."""
    _check(text, "text")
    low = f"{text} {category}".lower()
    return any(k in low for k in ("creatine", "thermogenic", "fat burner", "muscle building", "weight loss", "steroid"))


def verify_ny_pos_id_prompt(sku_id: str, customer_age: int = 21) -> dict:
    """Verify 18+ age gate prompt at POS for restricted NY dietary supplements."""
    _check(sku_id, "sku_id")
    if customer_age < 0:
        raise DataValidationError("customer_age must be non-negative")
    return {"op": "verify_ny_pos_id_prompt", "sku_id": str(sku_id), "allowed": customer_age >= 18, "src": "recallstorm/states/ny_dietary_supplements.py"}


def scan_muscle_building_claims(label_text: str) -> dict:
    """Scan label text for muscle-building claims subject to NY GBL 391-oo."""
    _check(label_text, "label_text")
    flagged = is_restricted_ny_supplement(label_text)
    return {"op": "scan_muscle_building_claims", "flagged": flagged, "src": "recallstorm/states/ny_dietary_supplements.py"}


def flag_creatine_products(skus: list[dict]) -> list[str]:
    """Return sku_ids of products containing creatine."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return [str(s["sku_id"]) for s in skus if "creatine" in str(s.get("ingredients", "")).lower() or "creatine" in str(s.get("name", "")).lower()]


def check_ny_delivery_age_gate(order_id: str, adult_signature: bool = True) -> dict:
    """Verify adult signature requirement on NY supplement delivery orders."""
    _check(order_id, "order_id")
    return {"op": "check_ny_delivery_age_gate", "order_id": str(order_id), "compliant": bool(adult_signature), "src": "recallstorm/states/ny_dietary_supplements.py"}


def audit_ny_self_checkout_block(store_id: str, override_count: int = 0) -> dict:
    """Audit self-checkout attendant age-verification overrides in NY stores."""
    _check(store_id, "store_id")
    if override_count < 0:
        raise DataValidationError("override_count cannot be negative")
    return {"op": "audit_ny_self_checkout_block", "store_id": str(store_id), "override_count": override_count, "src": "recallstorm/states/ny_dietary_supplements.py"}


def classify_ny_thermogenic_sku(sku_id: str, ingredients: str) -> dict:
    """Classify thermogenic/stimulant blend SKUs under NY supplement rules."""
    _check(sku_id, "sku_id")
    restricted = is_restricted_ny_supplement(ingredients)
    return {"op": "classify_ny_thermogenic_sku", "sku_id": str(sku_id), "restricted": restricted, "src": "recallstorm/states/ny_dietary_supplements.py"}


def generate_ny_ag_notice(store_id: str, sku_ids: list[str]) -> dict:
    """Generate a NY Attorney General compliance notice record."""
    _check(store_id, "store_id")
    return {"op": "generate_ny_ag_notice", "store_id": str(store_id), "count": len(sku_ids), "src": "recallstorm/states/ny_dietary_supplements.py"}


def map_ny_supplement_aisles(store_id: str, aisles: list[str]) -> dict:
    """Map nutrition/supplement aisles requiring NY age-restriction signage."""
    _check(store_id, "store_id")
    return {"op": "map_ny_supplement_aisles", "store_id": str(store_id), "aisles": sorted(aisles), "src": "recallstorm/states/ny_dietary_supplements.py"}


def validate_ny_courier_handoff(handoff_id: str, id_scanned: bool = True) -> dict:
    """Validate that last-mile courier scanned government ID upon NY supplement handoff."""
    _check(handoff_id, "handoff_id")
    return {"op": "validate_ny_courier_handoff", "handoff_id": str(handoff_id), "valid": bool(id_scanned), "src": "recallstorm/states/ny_dietary_supplements.py"}
