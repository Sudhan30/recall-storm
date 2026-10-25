"""Reconcile ASN/BOL shipped cases against store receiving logs."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ConsigneeShipmentLedger:
    """Ledger reconciling vendor ASN shipments against DC/store receipts."""

    ref_id: str = "CON-LED-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ShipToMatcher:
    """Matcher for vendor Ship-To GLNs and store IDs."""

    ref_id: str = "CON-SHP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def match_asn_bol_to_recall_lots(asn_lots: list[str], recall_lots: set[str]) -> list[str]:
    """Intersect ASN lot numbers with recall_lots."""
    if asn_lots is None or recall_lots is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(asn_lots) & set(recall_lots))


def reconcile_billed_vs_received_cases(billed: int, received: int) -> dict:
    """Compute case variance between vendor invoice and DC/store receipt."""
    if billed < 0 or received < 0:
        raise DataValidationError("Negative case counts")
    return {"op": "reconcile_billed_vs_received_cases", "billed": int(billed), "received": int(received), "variance": int(received) - int(billed), "src": "recallstorm/recall_lots/consignee_reconciliation.py"}


def identify_drop_ship_store_deliveries(deliveries: list[dict]) -> list[str]:
    """Return store_ids that received direct vendor drop-shipments bypassing the DC."""
    if deliveries is None:
        raise DataValidationError("deliveries cannot be None")
    return sorted(str(d["store_id"]) for d in deliveries if d.get("drop_ship"))


def flag_diverted_wholesaler_loads(bol_id: str, authorized_source: bool = False) -> dict:
    """Flag gray-market/diverted wholesaler loads."""
    _req(bol_id, "bol_id")
    return {"op": "flag_diverted_wholesaler_loads", "bol_id": str(bol_id), "flagged": not authorized_source, "src": "recallstorm/recall_lots/consignee_reconciliation.py"}


def calculate_net_shipped_exposure(shipped_cases: int, returned_cases: int) -> int:
    """Calculate net unrecovered cases still in field."""
    if shipped_cases < 0 or returned_cases < 0:
        raise DataValidationError("Negative case counts")
    return max(0, int(shipped_cases) - int(returned_cases))


def resolve_dc_cross_dock_splits(master_lpn: str, store_splits: dict[str, int]) -> dict:
    """Resolve a DC cross-dock master pallet into store case allocations."""
    _req(master_lpn, "master_lpn")
    if store_splits is None:
        raise DataValidationError("store_splits cannot be None")
    return {"op": "resolve_dc_cross_dock_splits", "master_lpn": str(master_lpn), "total_cases": sum(store_splits.values()), "src": "recallstorm/recall_lots/consignee_reconciliation.py"}


def audit_unmatched_po_receipts(po_ids: list[str]) -> list[str]:
    """Return sorted unmatched purchase order IDs."""
    if po_ids is None:
        raise DataValidationError("po_ids cannot be None")
    return sorted(str(p) for p in po_ids if str(p).strip())


def track_in_transit_carrier_trailers(trailer_id: str, eta_iso: str) -> dict:
    """Track an in-transit trailer carrying recalled lots."""
    _req(trailer_id, "trailer_id")
    _req(eta_iso, "eta_iso")
    return {"op": "track_in_transit_carrier_trailers", "trailer_id": str(trailer_id), "eta": str(eta_iso), "src": "recallstorm/recall_lots/consignee_reconciliation.py"}


def generate_consignee_variance_table(records: list[dict]) -> dict:
    """Compile consignee variance table summary."""
    if records is None:
        raise DataValidationError("records cannot be None")
    return {"op": "generate_consignee_variance_table", "row_count": len(records), "src": "recallstorm/recall_lots/consignee_reconciliation.py"}


def verify_zero_shipment_attestation(store_id: str, received_cases: int = 0) -> dict:
    """Verify that a store received zero cases of the recalled lot."""
    _req(store_id, "store_id")
    if received_cases < 0:
        raise DataValidationError("received_cases cannot be negative")
    return {"op": "verify_zero_shipment_attestation", "store_id": str(store_id), "zero_confirmed": received_cases == 0, "src": "recallstorm/recall_lots/consignee_reconciliation.py"}
