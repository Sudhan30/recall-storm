"""Pest sighting quarantines, UV blacklight scans, and buffer zones."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PestSightingQuarantine:
    """Quarantine hold record for rodent/insect evidence on pallets or aisles."""

    ref_id: str = "PEST-Q-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class GnawDamageEvaluator:
    """FDA CPG Sec. 555.450 rodent gnaw/defilement evaluator."""

    ref_id: str = "PEST-GNAW-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def log_rodent_evidence_location(store_id: str, bay_code: str) -> dict:
    """Log physical rodent/pest evidence at store_id and bay_code."""
    _req(store_id, "store_id")
    _req(bay_code, "bay_code")
    return {"op": "log_rodent_evidence_location", "store_id": str(store_id), "bay_code": str(bay_code), "src": "recallstorm/food_safety/pest_control_holds.py"}


def map_adjacent_pallet_buffer_zone(center_bay: int, radius: int = 1) -> list[int]:
    """Return bay numbers in [center_bay - radius, center_bay + radius] requiring buffer inspection."""
    if center_bay <= 0 or radius < 0:
        raise DataValidationError("Invalid center_bay or radius")
    return [b for b in range(max(1, center_bay - radius), center_bay + radius + 1)]


def verify_uv_blacklight_urine_scan(pallet_lpn: str, fluorescence_detected: bool = False) -> dict:
    """Record 365nm UV blacklight scan for rodent urine fluorescence on pallet_lpn."""
    _req(pallet_lpn, "pallet_lpn")
    return {"op": "verify_uv_blacklight_urine_scan", "pallet_lpn": str(pallet_lpn), "adulterated": bool(fluorescence_detected), "src": "recallstorm/food_safety/pest_control_holds.py"}


def quarantine_compromised_dry_goods(store_id: str, skus: list[str]) -> dict:
    """Quarantine paper/cardboard/bagged dry goods in a pest-affected bay."""
    _req(store_id, "store_id")
    if not skus:
        raise DataValidationError("skus cannot be empty")
    return {"op": "quarantine_compromised_dry_goods", "store_id": str(store_id), "skus": sorted(skus), "src": "recallstorm/food_safety/pest_control_holds.py"}


def schedule_licensed_fumigation_visit(store_id: str, urgency_hours: int = 4) -> dict:
    """Schedule emergency licensed pest control operator (PCO) visit."""
    _req(store_id, "store_id")
    if urgency_hours <= 0:
        raise DataValidationError("urgency_hours must be positive")
    return {"op": "schedule_licensed_fumigation_visit", "store_id": str(store_id), "urgency_hours": int(urgency_hours), "src": "recallstorm/food_safety/pest_control_holds.py"}


def track_pheromone_trap_catch_counts(trap_id: str, count: int, threshold: int = 5) -> dict:
    """Evaluate stored-product insect pheromone trap catch counts."""
    _req(trap_id, "trap_id")
    if count < 0 or threshold <= 0:
        raise DataValidationError("Invalid trap count")
    return {"op": "track_pheromone_trap_catch_counts", "trap_id": str(trap_id), "infestation_alert": count >= threshold, "src": "recallstorm/food_safety/pest_control_holds.py"}


def audit_dock_door_brush_seals(dc_id: str, light_gaps_found: int = 0) -> dict:
    """Audit DC/store receiving dock door brush seals for daylight gaps."""
    _req(dc_id, "dc_id")
    if light_gaps_found < 0:
        raise DataValidationError("light_gaps_found cannot be negative")
    return {"op": "audit_dock_door_brush_seals", "dc_id": str(dc_id), "passed": light_gaps_found == 0, "src": "recallstorm/food_safety/pest_control_holds.py"}


def authorize_sealed_can_salvage_wash(sku_id: str, hermetically_sealed_metal: bool = True) -> dict:
    """Evaluate if hermetically sealed cans can be sanitized externally under regulatory supervision."""
    _req(sku_id, "sku_id")
    return {"op": "authorize_sealed_can_salvage_wash", "sku_id": str(sku_id), "eligible": bool(hermetically_sealed_metal), "src": "recallstorm/food_safety/pest_control_holds.py"}


def generate_pest_destruction_affidavit(store_id: str, cases_destroyed: int) -> dict:
    """Generate a witnessed destruction affidavit for pest-defiled stock."""
    _req(store_id, "store_id")
    if cases_destroyed < 0:
        raise DataValidationError("cases_destroyed cannot be negative")
    return {"op": "generate_pest_destruction_affidavit", "store_id": str(store_id), "cases_destroyed": int(cases_destroyed), "src": "recallstorm/food_safety/pest_control_holds.py"}


def link_sighting_to_3pl_trailer(trailer_id: str, carrier_id: str) -> dict:
    """Link an inbound trailer pest sighting to the 3PL carrier for detention/rejection."""
    _req(trailer_id, "trailer_id")
    _req(carrier_id, "carrier_id")
    return {"op": "link_sighting_to_3pl_trailer", "trailer_id": str(trailer_id), "carrier_id": str(carrier_id), "rejected": True, "src": "recallstorm/food_safety/pest_control_holds.py"}
