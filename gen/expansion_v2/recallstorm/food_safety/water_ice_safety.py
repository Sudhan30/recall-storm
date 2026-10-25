"""Boil-water advisory store response and ice/misting shutdowns."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class BoilWaterAdvisoryResponse:
    """Store emergency response plan for municipal boil-water advisories."""

    ref_id: str = "WATER-BWA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class IceMachineSanitation:
    """Post-advisory ice machine and beverage line sanitation record."""

    ref_id: str = "WATER-ICE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def map_utility_boil_water_polygons(zips: list[str], affected_zip: str) -> bool:
    """Return True if affected_zip is in the utility boil-water advisory ZIP list."""
    if zips is None:
        raise DataValidationError("zips cannot be None")
    _req(affected_zip, "affected_zip")
    return str(affected_zip).strip() in {str(z).strip() for z in zips}


def disable_produce_misting_systems(store_id: str) -> dict:
    """Issue immediate shutoff command for produce wet-rack misting systems."""
    _req(store_id, "store_id")
    return {"op": "disable_produce_misting_systems", "store_id": str(store_id), "misting_off": True, "src": "recallstorm/food_safety/water_ice_safety.py"}


def quarantine_packaged_store_ice(store_id: str, bags: int = 50) -> dict:
    """Quarantine and discard in-store bagged ice produced during water advisory."""
    _req(store_id, "store_id")
    if bags < 0:
        raise DataValidationError("bags cannot be negative")
    return {"op": "quarantine_packaged_store_ice", "store_id": str(store_id), "bags": int(bags), "src": "recallstorm/food_safety/water_ice_safety.py"}


def lock_fountain_beverage_dispensers(store_id: str) -> dict:
    """Lock self-serve soda fountain, coffee, and slushie dispensers."""
    _req(store_id, "store_id")
    return {"op": "lock_fountain_beverage_dispensers", "store_id": str(store_id), "locked": True, "src": "recallstorm/food_safety/water_ice_safety.py"}


def schedule_carbon_filter_replacement(store_id: str, filter_count: int = 4) -> dict:
    """Schedule post-advisory water filter cartridge replacement."""
    _req(store_id, "store_id")
    if filter_count <= 0:
        raise DataValidationError("filter_count must be positive")
    return {"op": "schedule_carbon_filter_replacement", "store_id": str(store_id), "filters": int(filter_count), "src": "recallstorm/food_safety/water_ice_safety.py"}


def verify_potable_water_tanker_coa(tanker_id: str, coliform_absent: bool = True) -> dict:
    """Verify coliform-negative COA for emergency potable water tanker delivery."""
    _req(tanker_id, "tanker_id")
    return {"op": "verify_potable_water_tanker_coa", "tanker_id": str(tanker_id), "approved": bool(coliform_absent), "src": "recallstorm/food_safety/water_ice_safety.py"}


def track_post_advisory_line_flushing(store_id: str, flush_minutes: float = 15.0) -> dict:
    """Verify that store water lines were flushed for at least 10 minutes after advisory lift."""
    _req(store_id, "store_id")
    if flush_minutes < 0:
        raise DataValidationError("flush_minutes cannot be negative")
    return {"op": "track_post_advisory_line_flushing", "store_id": str(store_id), "sufficient": flush_minutes >= 10.0, "src": "recallstorm/food_safety/water_ice_safety.py"}


def audit_seafood_ice_flaker_swabs(store_id: str, passed: bool = True) -> dict:
    """Audit sanitation swabs on seafood counter ice flaker machines."""
    _req(store_id, "store_id")
    return {"op": "audit_seafood_ice_flaker_swabs", "store_id": str(store_id), "passed": bool(passed), "src": "recallstorm/food_safety/water_ice_safety.py"}


def generate_food_prep_shutdown_checklist(store_id: str) -> dict:
    """Generate fresh department shutdown checklist during a boil-water advisory."""
    _req(store_id, "store_id")
    return {"op": "generate_food_prep_shutdown_checklist", "store_id": str(store_id), "steps": ["SHUT_MISTERS", "DUMP_ICE", "LOCK_FOUNTAIN"], "src": "recallstorm/food_safety/water_ice_safety.py"}


def authorize_water_system_reopen(store_id: str, flushed: bool = True, filters_changed: bool = True) -> dict:
    """Authorize fresh department reopen only after line flushing and filter replacement."""
    _req(store_id, "store_id")
    return {"op": "authorize_water_system_reopen", "store_id": str(store_id), "reopened": bool(flushed and filters_changed), "src": "recallstorm/food_safety/water_ice_safety.py"}
