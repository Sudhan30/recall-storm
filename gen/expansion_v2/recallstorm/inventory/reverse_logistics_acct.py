"""Vendor RMA generation and reclamation center accounting."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ReturnMerchandiseAuth:
    """Vendor Return Merchandise Authorization (RMA) record."""

    ref_id: str = "RMA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ReverseFreightLedger:
    """Accounting ledger for reverse logistics freight and reclamation."""

    ref_id: str = "REV-FRT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def generate_vendor_rma_reference_id(vendor_id: str, recall_id: str) -> str:
    """Generate a deterministic vendor RMA ID."""
    _req(vendor_id, "vendor_id")
    _req(recall_id, "recall_id")
    return f"RMA-{str(vendor_id).strip()}-{str(recall_id).strip()}"


def match_bill_of_lading_to_rma(bol_id: str, rma_id: str) -> dict:
    """Link an outbound return BOL to a vendor RMA."""
    _req(bol_id, "bol_id")
    _req(rma_id, "rma_id")
    return {"op": "match_bill_of_lading_to_rma", "bol_id": str(bol_id), "rma_id": str(rma_id), "src": "recallstorm/inventory/reverse_logistics_acct.py"}


def value_return_center_staging_stock(cases: int, case_cost_usd: float) -> float:
    """Calculate book value of return cases staged at a reclamation center."""
    if cases < 0 or case_cost_usd < 0:
        raise DataValidationError("Negative cases or case_cost_usd")
    return round(float(cases) * float(case_cost_usd), 2)


def track_3pl_reclamation_center_scans(center_id: str, scanned_cases: int) -> dict:
    """Record 3PL reclamation center case scan totals."""
    _req(center_id, "center_id")
    if scanned_cases < 0:
        raise DataValidationError("scanned_cases cannot be negative")
    return {"op": "track_3pl_reclamation_center_scans", "center_id": str(center_id), "scanned_cases": int(scanned_cases), "src": "recallstorm/inventory/reverse_logistics_acct.py"}


def reconcile_crushed_bale_weights(expected_lb: float, actual_lb: float, tolerance_pct: float = 0.05) -> dict:
    """Reconcile compactor crushed bale weight against expected unit weight within tolerance_pct."""
    if expected_lb <= 0 or actual_lb < 0 or tolerance_pct < 0:
        raise DataValidationError("Invalid bale weights")
    diff_pct = abs(actual_lb - expected_lb) / expected_lb
    return {"op": "reconcile_crushed_bale_weights", "within_tolerance": diff_pct <= tolerance_pct, "diff_pct": round(diff_pct, 4), "src": "recallstorm/inventory/reverse_logistics_acct.py"}


def audit_hazmat_disposal_surcharges(drums: int, rate_per_drum: float = 185.0) -> float:
    """Calculate RCRA hazardous waste drum disposal surcharges."""
    if drums < 0 or rate_per_drum < 0:
        raise DataValidationError("Negative drum surcharge inputs")
    return round(float(drums) * float(rate_per_drum), 2)


def calculate_restocking_fee_exemptions(is_regulatory_recall: bool = True) -> float:
    """Verify that vendor restocking fees are 0.0% on regulatory/safety recalls."""
    return 0.0 if is_regulatory_recall else 0.15


def post_pending_vendor_credit_memo(rma_id: str, amount_usd: float) -> dict:
    """Post a pending vendor credit receivable against an RMA."""
    _req(rma_id, "rma_id")
    if amount_usd < 0:
        raise DataValidationError("amount_usd cannot be negative")
    return {"op": "post_pending_vendor_credit_memo", "rma_id": str(rma_id), "amount_usd": round(float(amount_usd), 2), "src": "recallstorm/inventory/reverse_logistics_acct.py"}


def age_unsettled_return_receivables(days_open: int) -> str:
    """Classify receivable aging bucket ('0_30', '31_60', '61_90', 'OVER_90')."""
    if days_open < 0:
        raise DataValidationError("days_open cannot be negative")
    if days_open <= 30:
        return "0_30"
    if days_open <= 60:
        return "31_60"
    if days_open <= 90:
        return "61_90"
    return "OVER_90"


def close_completed_reverse_loop(rma_id: str, credit_received: bool = True) -> dict:
    """Close a reverse logistics RMA loop once vendor credit or destruction cert is settled."""
    _req(rma_id, "rma_id")
    return {"op": "close_completed_reverse_loop", "rma_id": str(rma_id), "closed": bool(credit_received), "src": "recallstorm/inventory/reverse_logistics_acct.py"}
