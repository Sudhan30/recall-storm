"""Vendor credit memo matching to RMAs and aged deduction clearance."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class VendorCreditLedger:
    """Ledger tracking supplier recall credit memos and AP deductions."""

    ref_id: str = "CRD-LED-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DeductionMatcher:
    """Matcher reconciling vendor credit memos against retailer RMA claims."""

    ref_id: str = "CRD-MAT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def match_vendor_credit_memo_to_rma_id(credit_memo_id: str, rma_id: str, billed_usd: float, credited_usd: float) -> dict:
    """Match a vendor credit memo to an RMA and compute any short-credit variance."""
    _req(credit_memo_id, "credit_memo_id")
    _req(rma_id, "rma_id")
    if billed_usd < 0 or credited_usd < 0:
        raise DataValidationError("Negative credit amounts")
    return {
        "op": "match_vendor_credit_memo_to_rma_id",
        "credit_memo_id": str(credit_memo_id),
        "rma_id": str(rma_id),
        "shortfall_usd": round(max(0.0, billed_usd - credited_usd), 2),
        "src": "recallstorm/vendor/credit_reconciliation.py",
    }


def reconcile_unit_cost_discrepancies_on_credit(po_cost: float, vendor_credit_cost: float, units: int) -> float:
    """Calculate total dollar variance when vendor credits lower promotional cost instead of landed PO cost."""
    if po_cost < 0 or vendor_credit_cost < 0 or units < 0:
        raise DataValidationError("Negative cost inputs")
    return round(max(0.0, po_cost - vendor_credit_cost) * units, 2)


def track_swell_allowance_vs_recall_eligibility(is_class_i_or_ii: bool = True) -> dict:
    """Confirm that Class I/II recalls are 100% billable even if vendor has a general unsaleable swell allowance."""
    return {"op": "track_swell_allowance_vs_recall_eligibility", "billable_above_swell": bool(is_class_i_or_ii), "src": "recallstorm/vendor/credit_reconciliation.py"}


def clear_aged_open_deduction_balances(deduction_ids: list[str]) -> list[str]:
    """Return sorted cleared deduction IDs."""
    if deduction_ids is None:
        raise DataValidationError("deduction_ids cannot be None")
    return sorted(str(d) for d in deduction_ids if str(d).strip())


def audit_3pl_reclamation_settlement_files(expected_usd: float, settled_usd: float) -> dict:
    """Audit third-party reclamation processor settlement files."""
    if expected_usd < 0 or settled_usd < 0:
        raise DataValidationError("Negative settlement amounts")
    return {"op": "audit_3pl_reclamation_settlement_files", "variance_usd": round(expected_usd - settled_usd, 2), "src": "recallstorm/vendor/credit_reconciliation.py"}


def calculate_cash_discount_reversal_impact(gross_credit_usd: float, cash_discount_pct: float = 0.02) -> float:
    """Calculate net credit impact accounting for 2% early-pay cash discount terms."""
    if gross_credit_usd < 0 or not (0.0 <= cash_discount_pct < 1.0):
        raise DataValidationError("Invalid cash discount parameters")
    return round(gross_credit_usd * (1.0 - cash_discount_pct), 2)


def resolve_short_paid_invoice_disputes(dispute_id: str, rebilled_usd: float) -> dict:
    """Issue a supplemental debit memo for short-credited recall RMAs."""
    _req(dispute_id, "dispute_id")
    if rebilled_usd < 0:
        raise DataValidationError("rebilled_usd cannot be negative")
    return {"op": "resolve_short_paid_invoice_disputes", "dispute_id": str(dispute_id), "rebilled_usd": round(float(rebilled_usd), 2), "src": "recallstorm/vendor/credit_reconciliation.py"}


def generate_vendor_statement_of_account_pdf(vendor_id: str, open_recalls: int = 1) -> dict:
    """Generate a vendor statement of account for open recall deductions."""
    _req(vendor_id, "vendor_id")
    if open_recalls < 0:
        raise DataValidationError("open_recalls cannot be negative")
    return {"op": "generate_vendor_statement_of_account_pdf", "vendor_id": str(vendor_id), "open_recalls": int(open_recalls), "src": "recallstorm/vendor/credit_reconciliation.py"}


def escalate_insolvent_vendor_write_offs(vendor_id: str, uncollectible_usd: float) -> dict:
    """Reclassify uncollectible recall receivables from insolvent vendors to bad-debt/shrink reserve."""
    _req(vendor_id, "vendor_id")
    if uncollectible_usd < 0:
        raise DataValidationError("uncollectible_usd cannot be negative")
    return {"op": "escalate_insolvent_vendor_write_offs", "vendor_id": str(vendor_id), "write_off_usd": round(float(uncollectible_usd), 2), "src": "recallstorm/vendor/credit_reconciliation.py"}


def close_financial_recall_event_ledger(recall_id: str, net_p_and_l_usd: float = 0.0) -> dict:
    """Close the financial sub-ledger for recall_id."""
    _req(recall_id, "recall_id")
    return {"op": "close_financial_recall_event_ledger", "recall_id": str(recall_id), "closed": True, "net_p_and_l_usd": round(float(net_p_and_l_usd), 2), "src": "recallstorm/vendor/credit_reconciliation.py"}
