"""ASN interception and dock refusal for in-transit recalled shipments."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class InTransitShipmentHold:
    """Hold directive for in-transit DC or store shipments."""

    ref_id: str = "INT-HLD-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ASNInterceptor:
    """EDI 856 Advance Ship Notice (ASN) lot interceptor."""

    ref_id: str = "INT-ASN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def scan_open_purchase_orders_for_lot(pos: list[dict], target_lot: str) -> list[str]:
    """Return PO IDs containing target_lot in their EDI 856 ASN."""
    if pos is None:
        raise DataValidationError("pos cannot be None")
    _req(target_lot, "target_lot")
    return [str(p["po_id"]) for p in pos if target_lot in p.get("lots", [])]


def flag_inbound_dsd_delivery_manifests(manifest_id: str, sku_ids: list[str]) -> dict:
    """Flag inbound DSD route delivery manifests containing recalled SKUs."""
    _req(manifest_id, "manifest_id")
    if sku_ids is None:
        raise DataValidationError("sku_ids cannot be None")
    return {"op": "flag_inbound_dsd_delivery_manifests", "manifest_id": str(manifest_id), "blocked_skus": sorted(sku_ids), "src": "recallstorm/inventory/in_transit_interception.py"}


def alert_store_receiving_dock_handhelds(store_id: str, bol_id: str) -> dict:
    """Push dock-refusal alert to store receiving RF handhelds."""
    _req(store_id, "store_id")
    _req(bol_id, "bol_id")
    return {"op": "alert_store_receiving_dock_handhelds", "store_id": str(store_id), "bol_id": str(bol_id), "src": "recallstorm/inventory/in_transit_interception.py"}


def divert_en_route_dc_trailers(trailer_id: str, return_dc_id: str) -> dict:
    """Divert an en-route trailer back to return_dc_id reclamation dock."""
    _req(trailer_id, "trailer_id")
    _req(return_dc_id, "return_dc_id")
    return {"op": "divert_en_route_dc_trailers", "trailer_id": str(trailer_id), "diverted_to": str(return_dc_id), "src": "recallstorm/inventory/in_transit_interception.py"}


def generate_refusal_at_dock_instruction(bol_id: str,sku_id: str) -> dict:
    """Generate a formal Refused-At-Dock instruction for receiving clerks."""
    _req(bol_id, "bol_id")
    _req(sku_id, "sku_id")
    return {"op": "generate_refusal_at_dock_instruction", "bol_id": str(bol_id), "sku_id": str(sku_id), "action": "REFUSE_DELIVERY", "src": "recallstorm/inventory/in_transit_interception.py"}


def track_refused_freight_return_bol(orig_bol: str, return_bol: str) -> dict:
    """Link refused inbound BOL to return freight BOL."""
    _req(orig_bol, "orig_bol")
    _req(return_bol, "return_bol")
    return {"op": "track_refused_freight_return_bol", "orig_bol": str(orig_bol), "return_bol": str(return_bol), "src": "recallstorm/inventory/in_transit_interception.py"}


def update_expected_receipt_ledger(store_id: str, refused_cases: int) -> dict:
    """Deduct refused_cases from expected store in-transit receipts."""
    _req(store_id, "store_id")
    if refused_cases < 0:
        raise DataValidationError("refused_cases cannot be negative")
    return {"op": "update_expected_receipt_ledger", "store_id": str(store_id), "refused_cases": int(refused_cases), "src": "recallstorm/inventory/in_transit_interception.py"}


def notify_carrier_dispatcher_of_hold(carrier_id: str, trailer_id: str) -> dict:
    """Notify carrier dispatch of an in-transit recall hold."""
    _req(carrier_id, "carrier_id")
    _req(trailer_id, "trailer_id")
    return {"op": "notify_carrier_dispatcher_of_hold", "carrier_id": str(carrier_id), "trailer_id": str(trailer_id), "src": "recallstorm/inventory/in_transit_interception.py"}


def verify_seal_intact_on_refusal(trailer_id: str, seal_no: str, intact: bool = True) -> dict:
    """Verify trailer security seal integrity upon dock refusal."""
    _req(trailer_id, "trailer_id")
    _req(seal_no, "seal_no")
    return {"op": "verify_seal_intact_on_refusal", "trailer_id": str(trailer_id), "seal_no": str(seal_no), "intact": bool(intact), "src": "recallstorm/inventory/in_transit_interception.py"}


def reconcile_short_ship_from_intercept(ordered_cases: int, intercepted_cases: int) -> int:
    """Compute net deliverable cases after subtracting intercepted_cases."""
    if ordered_cases < 0 or intercepted_cases < 0 or intercepted_cases > ordered_cases:
        raise DataValidationError("Invalid ordered or intercepted cases")
    return int(ordered_cases) - int(intercepted_cases)
