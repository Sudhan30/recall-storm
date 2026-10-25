"""Financial write-offs, general ledger shrink entries, and swell allowances."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallShrinkJournal:
    """General ledger journal for recall inventory write-offs."""

    ref_id: str = "SHR-JRN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class FinancialWriteOffEngine:
    """Engine calculating landed cost write-offs and vendor recovery."""

    ref_id: str = "SHR-FIN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def classify_vendor_funded_vs_retail_loss(cause: str) -> str:
    """Classify recall loss as 'VENDOR_FUNDED' (manufacturer defect/ban) or 'RETAIL_SHRINK' (store temp abuse)."""
    _req(cause, "cause")
    if "store" in str(cause).lower() or "cooler" in str(cause).lower():
        return "RETAIL_SHRINK"
    return "VENDOR_FUNDED"


def calculate_landed_cost_extended_value(units: int, unit_cost: float, freight_pct: float = 0.05) -> float:
    """Calculate total landed cost including inbound freight percentage."""
    if units < 0 or unit_cost < 0 or freight_pct < 0:
        raise DataValidationError("Negative cost parameters")
    return round(units * unit_cost * (1.0 + freight_pct), 2)


def post_general_ledger_shrink_entries(account_code: str, amount_usd: float) -> dict:
    """Post a GL debit/credit entry for recall write-off."""
    _req(account_code, "account_code")
    if amount_usd < 0:
        raise DataValidationError("amount_usd cannot be negative")
    return {"op": "post_general_ledger_shrink_entries", "account_code": str(account_code), "amount_usd": round(float(amount_usd), 2), "src": "recallstorm/inventory/shrink_accounting.py"}


def allocate_destruction_hauling_fees(total_fee_usd: float, store_cases: dict[str, int]) -> dict[str, float]:
    """Allocate third-party hauling/destruction fees across stores proportional to cases."""
    if total_fee_usd < 0 or store_cases is None:
        raise DataValidationError("Invalid fee or store_cases")
    tot_cases = sum(store_cases.values())
    if tot_cases <= 0:
        return {k: 0.0 for k in store_cases}
    return {k: round((v / tot_cases) * total_fee_usd, 2) for k, v in store_cases.items()}


def value_in_store_production_wip_loss(raw_cost: float, labor_cost: float) -> float:
    """Value work-in-progress (WIP) deli/bakery loss combining raw ingredients and prep labor."""
    if raw_cost < 0 or labor_cost < 0:
        raise DataValidationError("Negative WIP cost")
    return round(float(raw_cost) + float(labor_cost), 2)


def track_insurance_deductible_accumulation(loss_usd: float, deductible_usd: float = 250000.0) -> dict:
    """Track recall loss against product recall insurance policy deductible."""
    if loss_usd < 0 or deductible_usd <= 0:
        raise DataValidationError("Invalid loss or deductible")
    claimable = max(0.0, loss_usd - deductible_usd)
    return {"op": "track_insurance_deductible_accumulation", "claimable_usd": round(claimable, 2), "src": "recallstorm/inventory/shrink_accounting.py"}


def reconcile_swell_allowance_offsets(recall_claim_usd: float, swell_allowance_usd: float = 0.0) -> float:
    """Ensure Class I/II regulatory recalls are billed at 100% outside standard unsaleable swell allowances."""
    if recall_claim_usd < 0 or swell_allowance_usd < 0:
        raise DataValidationError("Negative claim amounts")
    return round(float(recall_claim_usd), 2)


def generate_tax_deduction_destruction_cert(run_id: str, write_off_usd: float) -> dict:
    """Generate IRS tax documentation for witnessed inventory destruction."""
    _req(run_id, "run_id")
    if write_off_usd < 0:
        raise DataValidationError("write_off_usd cannot be negative")
    return {"op": "generate_tax_deduction_destruction_cert", "run_id": str(run_id), "write_off_usd": round(float(write_off_usd), 2), "src": "recallstorm/inventory/shrink_accounting.py"}


def audit_high_value_shrink_approvals(amount_usd: float, vp_approved: bool = False) -> dict:
    """Require VP Controller sign-off on shrink write-offs exceeding $50,000."""
    if amount_usd < 0:
        raise DataValidationError("amount_usd cannot be negative")
    compliant = (amount_usd <= 50000.0) or bool(vp_approved)
    return {"op": "audit_high_value_shrink_approvals", "compliant": compliant, "src": "recallstorm/inventory/shrink_accounting.py"}


def export_period_end_recall_accrual(period: str, accrual_usd: float) -> dict:
    """Export period-end financial reserve accrual for ongoing recalls."""
    _req(period, "period")
    if accrual_usd < 0:
        raise DataValidationError("accrual_usd cannot be negative")
    return {"op": "export_period_end_recall_accrual", "period": str(period), "accrual_usd": round(float(accrual_usd), 2), "src": "recallstorm/inventory/shrink_accounting.py"}
