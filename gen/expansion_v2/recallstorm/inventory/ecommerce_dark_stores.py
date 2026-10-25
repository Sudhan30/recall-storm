"""BOPIS, curbside tote interception, and micro-fulfillment holds."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class MicroFulfillmentHold:
    """Hold record for e-commerce dark stores and micro-fulfillment centers (MFCs)."""

    ref_id: str = "ECOM-MFC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class OrderPickInterceptor:
    """Interceptor for BOPIS / online grocery pickup orders."""

    ref_id: str = "ECOM-PICK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def purge_recalled_sku_from_web_search(sku_id: str) -> dict:
    """Delist a recalled SKU from web/mobile search and product detail pages."""
    _req(sku_id, "sku_id")
    return {"op": "purge_recalled_sku_from_web_search", "sku_id": str(sku_id), "delisted": True, "src": "recallstorm/inventory/ecommerce_dark_stores.py"}


def cancel_unfulfilled_bopis_line_items(orders: list[dict], sku_id: str) -> list[str]:
    """Cancel unfulfilled BOPIS order line items containing sku_id and return affected order_ids."""
    if orders is None:
        raise DataValidationError("orders cannot be None")
    _req(sku_id, "sku_id")
    return [str(o["order_id"]) for o in orders if sku_id in o.get("skus", [])]


def intercept_staged_curbside_totes(store_id: str, tote_ids: list[str]) -> dict:
    """Block customer handoff on staged curbside totes containing recalled items."""
    _req(store_id, "store_id")
    if not tote_ids:
        raise DataValidationError("tote_ids cannot be empty")
    return {"op": "intercept_staged_curbside_totes", "store_id": str(store_id), "totes": sorted(tote_ids), "src": "recallstorm/inventory/ecommerce_dark_stores.py"}


def halt_autostore_bin_presentation(mfc_id: str, bin_id: str) -> dict:
    """Inhibit AutoStore / automated grid robot from presenting bin_id to pick ports."""
    _req(mfc_id, "mfc_id")
    _req(bin_id, "bin_id")
    return {"op": "halt_autostore_bin_presentation", "mfc_id": str(mfc_id), "bin_id": str(bin_id), "halted": True, "src": "recallstorm/inventory/ecommerce_dark_stores.py"}


def reroute_instacart_shopper_pick_path(order_id: str, sub_sku_id: str) -> dict:
    """Push substitute SKU to gig/in-store personal shopper handheld app."""
    _req(order_id, "order_id")
    _req(sub_sku_id, "sub_sku_id")
    return {"op": "reroute_instacart_shopper_pick_path", "order_id": str(order_id), "sub_sku_id": str(sub_sku_id), "src": "recallstorm/inventory/ecommerce_dark_stores.py"}


def flag_in_flight_last_mile_couriers(delivery_ids: list[str]) -> list[str]:
    """Flag active last-mile delivery drivers carrying recalled items."""
    if delivery_ids is None:
        raise DataValidationError("delivery_ids cannot be None")
    return sorted(str(d) for d in delivery_ids if str(d).strip())


def process_automatic_digital_refunds(order_ids: list[str], unit_price: float = 4.99) -> float:
    """Calculate total automatic digital refunds issued for intercepted online orders."""
    if order_ids is None or unit_price < 0:
        raise DataValidationError("Invalid refund inputs")
    return round(len(order_ids) * float(unit_price), 2)


def quarantine_dark_store_decant_totes(dark_store_id: str, tote_count: int = 1) -> dict:
    """Quarantine decanted plastic totes in a dark store."""
    _req(dark_store_id, "dark_store_id")
    if tote_count < 0:
        raise DataValidationError("tote_count cannot be negative")
    return {"op": "quarantine_dark_store_decant_totes", "dark_store_id": str(dark_store_id), "tote_count": int(tote_count), "src": "recallstorm/inventory/ecommerce_dark_stores.py"}


def audit_locker_pickup_compartments(store_id: str, compartment_ids: list[str]) -> dict:
    """Revoke customer PIN codes and unlock automated pickup locker compartments for associate retrieval."""
    _req(store_id, "store_id")
    if compartment_ids is None:
        raise DataValidationError("compartment_ids cannot be None")
    return {"op": "audit_locker_pickup_compartments", "store_id": str(store_id), "compartments": sorted(compartment_ids), "src": "recallstorm/inventory/ecommerce_dark_stores.py"}


def sync_virtual_inventory_availability(sku_id: str, available_to_promise: int = 0) -> dict:
    """Force Available-To-Promise (ATP) e-commerce inventory to zero."""
    _req(sku_id, "sku_id")
    if available_to_promise < 0:
        raise DataValidationError("available_to_promise cannot be negative")
    return {"op": "sync_virtual_inventory_availability", "sku_id": str(sku_id), "atp": int(available_to_promise), "src": "recallstorm/inventory/ecommerce_dark_stores.py"}
