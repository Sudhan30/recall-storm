"""Calculate vendor recall execution chargebacks and AP remittance deductions."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallChargebackInvoice:
    """Supplier recall execution and product write-off chargeback invoice."""

    ref_id: str = "CBK-INV-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class FeeScheduleCalculator:
    """Calculator for Master Vendor Agreement recall fee schedules."""

    ref_id: str = "CBK-FEE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def calculate_per_store_execution_labor_fee(store_count: int, fee_per_store_usd: float = 75.0) -> float:
    """Calculate per-store recall execution labor fee."""
    if store_count < 0 or fee_per_store_usd < 0:
        raise DataValidationError("Negative store_count or fee_per_store_usd")
    return round(float(store_count) * float(fee_per_store_usd), 2)


def apply_per_unit_handling_and_hauling_rate(units: int, rate_per_unit_usd: float = 0.50) -> float:
    """Calculate per-unit reverse logistics handling and disposal fee."""
    if units < 0 or rate_per_unit_usd < 0:
        raise DataValidationError("Negative units or rate_per_unit_usd")
    return round(float(units) * float(rate_per_unit_usd), 2)


def bill_pos_programming_and_signage_flat_fee(fda_class: str = "Class I") -> float:
    """Return flat corporate administrative/POS/signage fee ($5,000 for Class I, $2,500 otherwise)."""
    _req(fda_class, "fda_class")
    return 5000.0 if "CLASS I" in str(fda_class).upper() and "II" not in str(fda_class).upper() else 2500.0


def compute_lost_gross_margin_recovery(units: int, retail_price: float, unit_cost: float) -> float:
    """Compute lost gross margin recovery when contractually allowed on Class I recalls."""
    if units < 0 or retail_price < 0 or unit_cost < 0 or retail_price < unit_cost:
        raise DataValidationError("Invalid margin parameters")
    return round(units * (retail_price - unit_cost), 2)


def attach_store_scan_audit_backup_csv(invoice_id: str, scan_rows: int) -> dict:
    """Attach store-by-store RF pull scan backup CSV to invoice_id."""
    _req(invoice_id, "invoice_id")
    if scan_rows < 0:
        raise DataValidationError("scan_rows cannot be negative")
    return {"op": "attach_store_scan_audit_backup_csv", "invoice_id": str(invoice_id), "scan_rows": int(scan_rows), "src": "recallstorm/vendor/chargeback_engine.py"}


def deduct_chargeback_from_ap_remittance(ap_balance_usd: float, chargeback_usd: float) -> dict:
    """Net recall chargeback against open Accounts Payable remittance to the vendor."""
    if ap_balance_usd < 0 or chargeback_usd < 0:
        raise DataValidationError("Negative AP or chargeback amounts")
    deducted = min(ap_balance_usd, chargeback_usd)
    unrecovered = round(max(0.0, chargeback_usd - deducted), 2)
    return {"op": "deduct_chargeback_from_ap_remittance", "deducted_usd": round(deducted, 2), "unrecovered_usd": unrecovered, "src": "recallstorm/vendor/chargeback_engine.py"}


def handle_vendor_chargeback_dispute_claim(dispute_id: str, valid_proof: bool = False) -> dict:
    """Evaluate a supplier chargeback dispute."""
    _req(dispute_id, "dispute_id")
    return {"op": "handle_vendor_chargeback_dispute_claim", "dispute_id": str(dispute_id), "upheld": not valid_proof, "src": "recallstorm/vendor/chargeback_engine.py"}


def enforce_master_vendor_agreement_caps(fee_usd: float, cap_usd: float = 100000.0) -> float:
    """Apply contractual fee cap if specified in the Master Vendor Agreement."""
    if fee_usd < 0 or cap_usd <= 0:
        raise DataValidationError("Invalid fee or cap")
    return round(min(float(fee_usd), float(cap_usd)), 2)


def escalate_unpaid_private_label_claims(vendor_id: str, days_past_due: int) -> dict:
    """Escalate unpaid co-packer recall claims > 60 days past due to Legal."""
    _req(vendor_id, "vendor_id")
    if days_past_due < 0:
        raise DataValidationError("days_past_due cannot be negative")
    return {"op": "escalate_unpaid_private_label_claims", "vendor_id": str(vendor_id), "escalate": days_past_due > 60, "src": "recallstorm/vendor/chargeback_engine.py"}


def export_erp_accounts_receivable_debit(invoice_id: str, total_usd: float) -> dict:
    """Export ERP AR debit memo record."""
    _req(invoice_id, "invoice_id")
    if total_usd < 0:
        raise DataValidationError("total_usd cannot be negative")
    return {"op": "export_erp_accounts_receivable_debit", "invoice_id": str(invoice_id), "total_usd": round(float(total_usd), 2), "src": "recallstorm/vendor/chargeback_engine.py"}
