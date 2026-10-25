"""Scan-based trading (SBT) and vendor-owned consignment stock holds."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ScanBasedTradingLedger:
    """Scan-Based Trading (SBT) consignment inventory ledger."""

    ref_id: str = "SBT-LED-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ConsignmentHoldTracker:
    """Tracker for recalled vendor-owned consignment stock."""

    ref_id: str = "SBT-HLD-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def identify_sbt_vendor_owned_skus(skus: list[dict]) -> list[str]:
    """Return sorted SKU IDs that are Scan-Based Trading (SBT) vendor-owned."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s["sku_id"]) for s in skus if s.get("is_sbt"))


def exclude_consignment_from_shrink_gl(retail_shrink_usd: float, sbt_value_usd: float) -> float:
    """Exclude vendor-owned SBT inventory value from retail shrink general ledger write-offs."""
    if retail_shrink_usd < 0 or sbt_value_usd < 0 or sbt_value_usd > retail_shrink_usd:
        raise DataValidationError("Invalid shrink or SBT value")
    return round(float(retail_shrink_usd) - float(sbt_value_usd), 2)


def notify_sbt_route_representative(vendor_id: str, store_id: str) -> dict:
    """Notify SBT route representative to remove recalled consignment stock within SLA."""
    _req(vendor_id, "vendor_id")
    _req(store_id, "store_id")
    return {"op": "notify_sbt_route_representative", "vendor_id": str(vendor_id), "store_id": str(store_id), "src": "recallstorm/inventory/consignment_stock.py"}


def record_zero_cost_quarantine_units(store_id: str, sku_id: str, units: int) -> dict:
    """Record pulled SBT units at $0.00 retailer book cost for regulatory count tracking."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    if units < 0:
        raise DataValidationError("units cannot be negative")
    return {"op": "record_zero_cost_quarantine_units", "store_id": str(store_id), "sku_id": str(sku_id), "units": int(units), "book_cost_usd": 0.0, "src": "recallstorm/inventory/consignment_stock.py"}


def verify_dsd_driver_buyback_scan(driver_id: str, cases: int) -> dict:
    """Verify backdoor DEX/handheld scan when DSD/SBT driver removes recalled cases."""
    _req(driver_id, "driver_id")
    if cases < 0:
        raise DataValidationError("cases cannot be negative")
    return {"op": "verify_dsd_driver_buyback_scan", "driver_id": str(driver_id), "cases": int(cases), "src": "recallstorm/inventory/consignment_stock.py"}


def reconcile_consignment_pad_counts(expected_units: int, physical_units: int) -> int:
    """Compute variance on consignment pad inventory."""
    if expected_units < 0 or physical_units < 0:
        raise DataValidationError("Negative unit counts")
    return int(physical_units) - int(expected_units)


def block_sbt_daily_pos_settlement(sku_id: str) -> dict:
    """Freeze automated EDI 852 POS scan settlement for a recalled SBT SKU."""
    _req(sku_id, "sku_id")
    return {"op": "block_sbt_daily_pos_settlement", "sku_id": str(sku_id), "settlement_frozen": True, "src": "recallstorm/inventory/consignment_stock.py"}


def audit_unremoved_vendor_racks(store_id: str, overdue_racks: int = 0) -> dict:
    """Audit vendor display racks that missed the DSD recall pickup deadline."""
    _req(store_id, "store_id")
    if overdue_racks < 0:
        raise DataValidationError("overdue_racks cannot be negative")
    return {"op": "audit_unremoved_vendor_racks", "store_id": str(store_id), "associate_pull_triggered": overdue_racks > 0, "src": "recallstorm/inventory/consignment_stock.py"}


def generate_consignment_removal_receipt(store_id: str, vendor_id: str, units: int) -> dict:
    """Generate a dual-signed receipt for vendor removal of recalled consignment stock."""
    _req(store_id, "store_id")
    _req(vendor_id, "vendor_id")
    if units < 0:
        raise DataValidationError("units cannot be negative")
    return {"op": "generate_consignment_removal_receipt", "store_id": str(store_id), "vendor_id": str(vendor_id), "units": int(units), "src": "recallstorm/inventory/consignment_stock.py"}


def validate_sbt_contract_recall_terms(contract_id: str, labor_reimbursable: bool = True) -> dict:
    """Validate that the SBT agreement reimburses retailer labor when store associates pull SBT items."""
    _req(contract_id, "contract_id")
    return {"op": "validate_sbt_contract_recall_terms", "contract_id": str(contract_id), "labor_reimbursable": bool(labor_reimbursable), "src": "recallstorm/inventory/consignment_stock.py"}
