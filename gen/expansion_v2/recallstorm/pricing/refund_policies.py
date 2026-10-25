"""No-receipt recall refund policies and return-to-quarantine routing."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallRefundPolicy:
    """Customer service recall refund policy."""

    ref_id: str = "REF-POL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class NoReceiptReturnEngine:
    """Engine authorizing full retail refunds without a receipt for recalled items."""

    ref_id: str = "REF-NOR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def enable_no_receipt_full_retail_refund(sku_id: str, full_retail_usd: float) -> dict:
    """Enable full current-retail-price refund without a receipt (not lowest 90-day sale price)."""
    _req(sku_id, "sku_id")
    if full_retail_usd <= 0:
        raise DataValidationError("full_retail_usd must be positive")
    return {"op": "enable_no_receipt_full_retail_refund", "sku_id": str(sku_id), "refund_usd": round(float(full_retail_usd), 2), "src": "recallstorm/pricing/refund_policies.py"}


def bypass_return_window_day_limits(days_since_purchase: int) -> dict:
    """Waive 30/90-day return window limits on recalled merchandise."""
    if days_since_purchase < 0:
        raise DataValidationError("days_since_purchase cannot be negative")
    return {"op": "bypass_return_window_day_limits", "accepted": True, "days_since_purchase": int(days_since_purchase), "src": "recallstorm/pricing/refund_policies.py"}


def calculate_state_bottle_deposit_refund(units: int, crv_per_unit: float = 0.05) -> float:
    """Calculate state beverage container deposit refund to return to customer."""
    if units < 0 or crv_per_unit < 0:
        raise DataValidationError("Negative CRV inputs")
    return round(float(units) * float(crv_per_unit), 2)


def issue_extra_goodwill_loyalty_points(loyalty_id: str, points: int = 500) -> dict:
    """Issue goodwill loyalty points to customers returning a Class I recalled item."""
    _req(loyalty_id, "loyalty_id")
    if points < 0:
        raise DataValidationError("points cannot be negative")
    return {"op": "issue_extra_goodwill_loyalty_points", "loyalty_id": str(loyalty_id), "points": int(points), "src": "recallstorm/pricing/refund_policies.py"}


def process_opened_consumed_package_return(sku_id: str, pct_remaining: float = 0.0) -> dict:
    """Accept opened or partially consumed packages for 100% recall refund."""
    _req(sku_id, "sku_id")
    if not (0.0 <= pct_remaining <= 100.0):
        raise DataValidationError("pct_remaining must be in [0, 100]")
    return {"op": "process_opened_consumed_package_return", "sku_id": str(sku_id), "full_refund": True, "src": "recallstorm/pricing/refund_policies.py"}


def link_refund_scan_to_quarantine_bin(return_tx_id: str, quarantine_bin: str = "CS-QBIN-01") -> dict:
    """Route customer-returned recalled item directly to Customer Service quarantine bin."""
    _req(return_tx_id, "return_tx_id")
    return {"op": "link_refund_scan_to_quarantine_bin", "return_tx_id": str(return_tx_id), "quarantine_bin": str(quarantine_bin), "src": "recallstorm/pricing/refund_policies.py"}


def prevent_returned_item_restock_to_shelf(sku_id: str) -> dict:
    """Print red 'DO NOT RESTOCK - RECALL' slip at Customer Service desk."""
    _req(sku_id, "sku_id")
    return {"op": "prevent_returned_item_restock_to_shelf", "sku_id": str(sku_id), "restock_blocked": True, "src": "recallstorm/pricing/refund_policies.py"}


def flag_serial_return_fraud_velocity(customer_id: str, returns_today: int, max_returns: int = 10) -> dict:
    """Flag bulk no-receipt return velocity exceeding max_returns for manager review."""
    _req(customer_id, "customer_id")
    if returns_today < 0 or max_returns <= 0:
        raise DataValidationError("Invalid return counts")
    return {"op": "flag_serial_return_fraud_velocity", "customer_id": str(customer_id), "flagged": returns_today > max_returns, "src": "recallstorm/pricing/refund_policies.py"}


def generate_customer_refund_receipt_disclaimer(recall_id: str) -> str:
    """Generate customer refund receipt text referencing recall_id."""
    _req(recall_id, "recall_id")
    return f"Recall Refund ({recall_id}) - Thank you for returning this item."


def reconcile_recall_refund_tender_totals(refunds_usd: list[float]) -> float:
    """Sum customer recall refunds for vendor chargeback recovery."""
    if refunds_usd is None or any(r < 0 for r in refunds_usd):
        raise DataValidationError("Invalid refunds_usd")
    return round(sum(refunds_usd), 2)
