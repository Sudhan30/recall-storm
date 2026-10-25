"""Own-brand co-packer plant mapping, GFSI/SQF audits, and CAPA closure."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class OwnBrandRecallManager:
    """Recall manager for store-brand / private-label products (Great Value, Kirkland, Favorite Day)."""

    ref_id: str = "PLB-MGR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CoPackerAuditTracker:
    """Tracker for private-label co-packer GFSI (SQF / BRCGS) audits."""

    ref_id: str = "PLB-AUD-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def map_private_label_sku_to_copacker_plant(sku_id: str, plant_id: str) -> dict:
    """Map an own-brand SKU to its contract manufacturing plant_id."""
    _req(sku_id, "sku_id")
    _req(plant_id, "plant_id")
    return {"op": "map_private_label_sku_to_copacker_plant", "sku_id": str(sku_id), "plant_id": str(plant_id), "src": "recallstorm/vendor/private_label_qa.py"}


def access_tracegains_supplier_spec_portal(sku_id: str) -> dict:
    """Query supplier specification portal for sub-ingredient disclosures."""
    _req(sku_id, "sku_id")
    return {"op": "access_tracegains_supplier_spec_portal", "sku_id": str(sku_id), "spec_found": True, "src": "recallstorm/vendor/private_label_qa.py"}


def trigger_unannounced_gfSI_sqf_audit(plant_id: str, score: int = 92) -> dict:
    """Trigger an unannounced for-cause GFSI/SQF audit at a co-packer plant."""
    _req(plant_id, "plant_id")
    if not (0 <= score <= 100):
        raise DataValidationError("score must be in 0..100")
    return {"op": "trigger_unannounced_gfSI_sqf_audit", "plant_id": str(plant_id), "passed": score >= 85, "src": "recallstorm/vendor/private_label_qa.py"}


def quarantine_shared_line_national_brand_runs(line_id: str, sibling_skus: list[str]) -> dict:
    """Identify and hold national-brand SKUs run on the same contaminated co-packer line."""
    _req(line_id, "line_id")
    if sibling_skus is None:
        raise DataValidationError("sibling_skus cannot be None")
    return {"op": "quarantine_shared_line_national_brand_runs", "line_id": str(line_id), "sibling_skus": sorted(sibling_skus), "src": "recallstorm/vendor/private_label_qa.py"}


def review_copacker_environmental_swab_trends(plant_id: str, positives: int = 0) -> dict:
    """Review co-packer Zone 1-3 environmental pathogen monitoring trends."""
    _req(plant_id, "plant_id")
    if positives < 0:
        raise DataValidationError("positives cannot be negative")
    return {"op": "review_copacker_environmental_swab_trends", "plant_id": str(plant_id), "hold_plant": positives > 0, "src": "recallstorm/vendor/private_label_qa.py"}


def enforce_own_brand_zero_tolerance_policy(sku_id: str,synthetic_dye_found: bool = True) -> dict:
    """Enforce retailer own-brand clean-label policy (prohibiting synthetic dyes even ahead of statutory dates)."""
    _req(sku_id, "sku_id")
    return {"op": "enforce_own_brand_zero_tolerance_policy", "sku_id": str(sku_id), "pull": bool(synthetic_dye_found), "src": "recallstorm/vendor/private_label_qa.py"}


def coordinate_private_label_press_release(sku_id: str, brand: str = "Great Value") -> dict:
    """Coordinate FDA press release where the retailer is the brand owner of record."""
    _req(sku_id, "sku_id")
    _req(brand, "brand")
    return {"op": "coordinate_private_label_press_release", "sku_id": str(sku_id), "brand": str(brand), "src": "recallstorm/vendor/private_label_qa.py"}


def manage_packaging_film_write_off_liability(rolls: int, cost_per_roll: float = 250.0) -> float:
    """Calculate obsolete packaging film write-off during regulatory label transitions."""
    if rolls < 0 or cost_per_roll < 0:
        raise DataValidationError("Negative packaging film inputs")
    return round(float(rolls) * float(cost_per_roll), 2)


def track_capa_corrective_action_closure(capa_id: str, verified_effective: bool = True) -> dict:
    """Track co-packer CAPA closure before resuming private-label POs."""
    _req(capa_id, "capa_id")
    return {"op": "track_capa_corrective_action_closure", "capa_id": str(capa_id), "closed": bool(verified_effective), "src": "recallstorm/vendor/private_label_qa.py"}


def score_copacker_food_safety_culture(audit_score: float, timely_reporting: bool = True) -> float:
    """Compute composite co-packer food safety score in [0.0, 100.0]."""
    if not (0.0 <= audit_score <= 100.0):
        raise DataValidationError("audit_score must be in [0, 100]")
    penalty = 0.0 if timely_reporting else 20.0
    return round(max(0.0, audit_score - penalty), 2)
