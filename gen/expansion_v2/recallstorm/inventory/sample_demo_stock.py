"""Club store and in-store demo cart sampling quarantines."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class DemoStationQuarantine:
    """Quarantine directive for in-store food demonstration stations."""

    ref_id: str = "DEMO-Q-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ClubStoreSampleHold:
    """Sam's Club / club-format demo prep cart inventory hold."""

    ref_id: str = "DEMO-SAMS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def halt_active_in_store_sampling_events(store_id: str, sku_id: str) -> dict:
    """Immediately halt active in-store product sampling events for sku_id."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "halt_active_in_store_sampling_events", "store_id": str(store_id), "sku_id": str(sku_id), "halted": True, "src": "recallstorm/inventory/sample_demo_stock.py"}


def quarantine_demo_prep_cart_inventory(store_id: str, cart_id: str, units: int = 1) -> dict:
    """Quarantine opened and unopened units on demo prep carts."""
    _req(store_id, "store_id")
    _req(cart_id, "cart_id")
    if units < 0:
        raise DataValidationError("units cannot be negative")
    return {"op": "quarantine_demo_prep_cart_inventory", "store_id": str(store_id), "cart_id": str(cart_id), "units": int(units), "src": "recallstorm/inventory/sample_demo_stock.py"}


def reconcile_expensed_demo_unit_transfers(shelf_pulled: int, demo_transferred: int) -> int:
    """Combine salesfloor pulled units with units previously expensed to the demo department."""
    if shelf_pulled < 0 or demo_transferred < 0:
        raise DataValidationError("Negative unit counts")
    return int(shelf_pulled) + int(demo_transferred)


def alert_third_party_demo_agency_lead(agency_id: str, store_id: str) -> dict:
    """Alert third-party demo staffing agency lead of recall."""
    _req(agency_id, "agency_id")
    _req(store_id, "store_id")
    return {"op": "alert_third_party_demo_agency_lead", "agency_id": str(agency_id), "store_id": str(store_id), "src": "recallstorm/inventory/sample_demo_stock.py"}


def verify_trash_compactor_sample_disposal(store_id: str, disposed: bool = True) -> dict:
    """Verify that opened sample trays were disposed of in the locked compactor."""
    _req(store_id, "store_id")
    return {"op": "verify_trash_compactor_sample_disposal", "store_id": str(store_id), "disposed": bool(disposed), "src": "recallstorm/inventory/sample_demo_stock.py"}


def audit_bakery_free_cookie_bins(store_id: str, sprinkle_recalled: bool = True) -> dict:
    """Audit kids' free cookie bins in the bakery for recalled sprinkles/dyes."""
    _req(store_id, "store_id")
    return {"op": "audit_bakery_free_cookie_bins", "store_id": str(store_id), "pulled": bool(sprinkle_recalled), "src": "recallstorm/inventory/sample_demo_stock.py"}


def check_pharmacy_immunization_promos(store_id: str, promo_sku: str) -> dict:
    """Check promotional giveaway items at pharmacy/wellness counters."""
    _req(store_id, "store_id")
    _req(promo_sku, "promo_sku")
    return {"op": "check_pharmacy_immunization_promos", "store_id": str(store_id), "promo_sku": str(promo_sku), "src": "recallstorm/inventory/sample_demo_stock.py"}


def log_open_package_demo_destruction(store_id: str, open_units: int) -> dict:
    """Log destruction of partially served demo packages."""
    _req(store_id, "store_id")
    if open_units < 0:
        raise DataValidationError("open_units cannot be negative")
    return {"op": "log_open_package_demo_destruction", "store_id": str(store_id), "open_units": int(open_units), "src": "recallstorm/inventory/sample_demo_stock.py"}


def calculate_unbilled_sample_exposure(demo_units: int, unit_cost: float = 5.0) -> float:
    """Calculate vendor chargeback value for expensed demo units."""
    if demo_units < 0 or unit_cost < 0:
        raise DataValidationError("Negative demo exposure inputs")
    return round(float(demo_units) * float(unit_cost), 2)


def clear_demo_station_sanitation_hold(station_id: str, sanitized: bool = True) -> dict:
    """Release a demo cart/station after allergen/pathogen sanitation."""
    _req(station_id, "station_id")
    return {"op": "clear_demo_station_sanitation_hold", "station_id": str(station_id), "cleared": bool(sanitized), "src": "recallstorm/inventory/sample_demo_stock.py"}
