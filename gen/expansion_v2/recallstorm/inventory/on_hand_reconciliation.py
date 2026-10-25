"""Perpetual inventory snapshots and physical pull variance reconciliation."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PerpetualInventoryLedger:
    """Store/DC perpetual book inventory ledger."""

    ref_id: str = "INV-PERP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class RecallVarianceReconciler:
    """Reconciler for physical recall pull counts vs perpetual on-hand."""

    ref_id: str = "INV-REC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def snapshot_pre_recall_book_inventory(store_id: str, on_hand_by_sku: dict[str, int]) -> dict:
    """Freeze a point-in-time snapshot of perpetual on-hand inventory before shelf pulls start."""
    _req(store_id, "store_id")
    if on_hand_by_sku is None:
        raise DataValidationError("on_hand_by_sku cannot be None")
    return {"op": "snapshot_pre_recall_book_inventory", "store_id": str(store_id), "total_units": sum(on_hand_by_sku.values()), "src": "recallstorm/inventory/on_hand_reconciliation.py"}


def compare_physical_pull_to_on_hand(pulled_units: int, book_units: int) -> dict:
    """Compare physically pulled units against perpetual book units."""
    if pulled_units < 0:
        raise DataValidationError("pulled_units cannot be negative")
    return {"op": "compare_physical_pull_to_on_hand", "pulled": int(pulled_units), "book": int(book_units), "variance": int(pulled_units) - int(book_units), "src": "recallstorm/inventory/on_hand_reconciliation.py"}


def resolve_in_transit_asn_quantities(book_units: int, in_transit_units: int) -> int:
    """Add in-transit ASN units to book_units to determine total store exposure."""
    if book_units < 0 or in_transit_units < 0:
        raise DataValidationError("Negative unit counts")
    return int(book_units) + int(in_transit_units)


def adjust_phantom_inventory_balances(store_id: str, sku_id: str, new_balance: int = 0) -> dict:
    """Zero out phantom perpetual inventory after verified empty-shelf blind count."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    if new_balance < 0:
        raise DataValidationError("new_balance cannot be negative")
    return {"op": "adjust_phantom_inventory_balances", "store_id": str(store_id), "sku_id": str(sku_id), "new_balance": int(new_balance), "src": "recallstorm/inventory/on_hand_reconciliation.py"}


def account_for_unscanned_pos_cart_items(pulled: int, register_intercepts: int) -> int:
    """Combine shelf pull count with units intercepted at POS registers from customer carts."""
    if pulled < 0 or register_intercepts < 0:
        raise DataValidationError("Negative counts")
    return int(pulled) + int(register_intercepts)


def reconcile_click_and_collect_stagings(shelf_pulled: int, tote_pulled: int) -> int:
    """Combine salesfloor pulled units with units pulled from BOPIS pickup totes."""
    if shelf_pulled < 0 or tote_pulled < 0:
        raise DataValidationError("Negative counts")
    return int(shelf_pulled) + int(tote_pulled)


def flag_negative_on_hand_anomalies(balances: dict[str, int]) -> list[str]:
    """Return sorted SKU IDs with negative perpetual on-hand balances."""
    if balances is None:
        raise DataValidationError("balances cannot be None")
    return sorted(sku for sku, bal in balances.items() if int(bal) < 0)


def calculate_unexplained_lot_discrepancy(shipped: int, sold: int, pulled: int) -> int:
    """Calculate unexplained unit discrepancy: shipped - sold - pulled."""
    if shipped < 0 or sold < 0 or pulled < 0:
        raise DataValidationError("Negative unit inputs")
    return int(shipped) - int(sold) - int(pulled)


def post_erp_inventory_adjustment_journal(store_id: str, sku_id: str, delta_units: int) -> dict:
    """Post an ERP perpetual inventory adjustment journal entry."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "post_erp_inventory_adjustment_journal", "store_id": str(store_id), "sku_id": str(sku_id), "delta_units": int(delta_units), "src": "recallstorm/inventory/on_hand_reconciliation.py"}


def lock_sku_from_auto_replenishment(sku_id: str) -> dict:
    """Disable automated store replenishment ordering for a recalled SKU."""
    _req(sku_id, "sku_id")
    return {"op": "lock_sku_from_auto_replenishment", "sku_id": str(sku_id), "auto_order_locked": True, "src": "recallstorm/inventory/on_hand_reconciliation.py"}
