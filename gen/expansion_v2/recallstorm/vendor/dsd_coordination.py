"""Coordinate Direct Store Delivery (DSD) driver pickups and DEX credit scans."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class DsdRecallExecution:
    """Direct Store Delivery (DSD) vendor pull and credit execution."""

    ref_id: str = "DSD-EXE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class RouteDriverSignOff:
    """Backdoor DEX/handheld sign-off for DSD route driver pickups."""

    ref_id: str = "DSD-DRV-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def notify_dsd_bottler_bakery_dispatcher(vendor_id: str, store_ids: list[str]) -> dict:
    """Dispatch urgent recall pickup notice to regional DSD bottler/bakery/snack distributor."""
    _req(vendor_id, "vendor_id")
    if not store_ids:
        raise DataValidationError("store_ids cannot be empty")
    return {"op": "notify_dsd_bottler_bakery_dispatcher", "vendor_id": str(vendor_id), "stores": sorted(store_ids), "src": "recallstorm/vendor/dsd_coordination.py"}


def schedule_driver_in_store_credit_pickup(store_id: str, vendor_id: str, window_hours: int = 24) -> dict:
    """Schedule DSD driver backroom credit pickup."""
    _req(store_id, "store_id")
    _req(vendor_id, "vendor_id")
    if window_hours <= 0:
        raise DataValidationError("window_hours must be positive")
    return {"op": "schedule_driver_in_store_credit_pickup", "store_id": str(store_id), "vendor_id": str(vendor_id), "window_hours": int(window_hours), "src": "recallstorm/vendor/dsd_coordination.py"}


def verify_backdoor_dex_return_invoice_scan(dex_invoice_id: str, credit_usd: float) -> dict:
    """Verify electronic DEX/UCS credit invoice at store receiving door before DSD driver exits with recalled goods."""
    _req(dex_invoice_id, "dex_invoice_id")
    if credit_usd < 0:
        raise DataValidationError("credit_usd cannot be negative")
    return {"op": "verify_backdoor_dex_return_invoice_scan", "dex_invoice_id": str(dex_invoice_id), "credit_usd": round(float(credit_usd), 2), "src": "recallstorm/vendor/dsd_coordination.py"}


def audit_driver_pulled_case_counts_at_exit(store_pulled: int, driver_credited: int) -> dict:
    """Verify that DSD driver credited 100% of the units pulled by store associates."""
    if store_pulled < 0 or driver_credited < 0:
        raise DataValidationError("Negative counts")
    return {"op": "audit_driver_pulled_case_counts_at_exit", "matched": store_pulled == driver_credited, "shortage": max(0, store_pulled - driver_credited), "src": "recallstorm/vendor/dsd_coordination.py"}


def prevent_unauthorized_dsd_shelf_restock(store_id: str, sku_id: str) -> dict:
    """Prevent DSD merchandisers from pack-out restocking a recalled SKU from backroom carts."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "prevent_unauthorized_dsd_shelf_restock", "store_id": str(store_id), "sku_id": str(sku_id), "blocked": True, "src": "recallstorm/vendor/dsd_coordination.py"}


def lock_dsd_item_in_receiving_handheld(sku_id: str) -> dict:
    """Block inbound DSD DEX receiving for a recalled SKU."""
    _req(sku_id, "sku_id")
    return {"op": "lock_dsd_item_in_receiving_handheld", "sku_id": str(sku_id), "dex_blocked": True, "src": "recallstorm/vendor/dsd_coordination.py"}


def reconcile_driver_handwritten_credit_slips(slip_id: str, units: int, unit_cost: float) -> float:
    """Value manual paper DSD credit slips when electronic DEX is unavailable."""
    _req(slip_id, "slip_id")
    if units < 0 or unit_cost < 0:
        raise DataValidationError("Negative slip inputs")
    return round(float(units) * float(unit_cost), 2)


def track_unserviced_rural_store_dsd_holds(stores: list[str], serviced: set[str]) -> list[str]:
    """Return sorted store_ids where DSD driver has not yet picked up staged recall stock."""
    if stores is None or serviced is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(stores) - set(serviced))


def escalate_missed_dsd_pickup_sla_window(store_id: str, hours_elapsed: float, sla_hours: float = 48.0) -> dict:
    """Authorize store compactor destruction + vendor chargeback when DSD driver misses 48h pickup SLA."""
    _req(store_id, "store_id")
    if hours_elapsed < 0 or sla_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "escalate_missed_dsd_pickup_sla_window", "store_id": str(store_id), "destroy_and_bill": hours_elapsed > sla_hours, "src": "recallstorm/vendor/dsd_coordination.py"}


def close_dsd_route_reconciliation_loop(store_id: str, dex_invoice_id: str) -> dict:
    """Close DSD store recall exception once DEX credit is posted."""
    _req(store_id, "store_id")
    _req(dex_invoice_id, "dex_invoice_id")
    return {"op": "close_dsd_route_reconciliation_loop", "store_id": str(store_id), "closed": True, "src": "recallstorm/vendor/dsd_coordination.py"}
