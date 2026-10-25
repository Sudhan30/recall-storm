"""CRV/bottle deposit tax credits and reverse vending machine blocks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ContainerDepositReconciler:
    """Reconciler for CA CRV and state bottle-bill deposits on recalled beverages."""

    ref_id: str = "CRV-REC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CrvRedemptionBlocker:
    """Blocker for Reverse Vending Machine (RVM) barcode tables."""

    ref_id: str = "CRV-RVM-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def calculate_unredeemed_crv_tax_credit(containers: int, rate_usd: float = 0.05) -> float:
    """Calculate prepaid beverage container deposit credit on pulled/destroyed stock."""
    if containers < 0 or rate_usd < 0:
        raise DataValidationError("Negative CRV inputs")
    return round(float(containers) * float(rate_usd), 2)


def block_reverse_vending_machine_barcodes(store_id: str, upc: str) -> dict:
    """Update bottle-room Reverse Vending Machines (RVMs) to flag/segregate recalled glass/cans."""
    _req(store_id, "store_id")
    _req(upc, "upc")
    return {"op": "block_reverse_vending_machine_barcodes", "store_id": str(store_id), "upc": str(upc), "rvm_updated": True, "src": "recallstorm/pricing/bottle_deposit_credits.py"}


def reconcile_distributor_deposit_chargebacks(cases: int, bottles_per_case: int = 24, rate_usd: float = 0.05) -> float:
    """Calculate total bottle deposit chargeback due from the beverage distributor."""
    if cases < 0 or bottles_per_case <= 0 or rate_usd < 0:
        raise DataValidationError("Invalid distributor deposit inputs")
    return round(cases * bottles_per_case * rate_usd, 2)


def adjust_crushed_beverage_can_counts(gross_lb: float, cans_per_lb: float = 32.0) -> int:
    """Estimate individual aluminum can count from crushed bale weight."""
    if gross_lb < 0 or cans_per_lb <= 0:
        raise DataValidationError("Invalid weight or cans_per_lb")
    return int(round(gross_lb * cans_per_lb))


def handle_multi_state_deposit_rate_diffs(state: str, fl_oz: float = 12.0) -> float:
    """Return statutory container deposit rate for state ('CA', 'OR', 'MI', 'NY', 'ME', 'VT', 'CT', 'MA', 'IA', 'HI')."""
    _req(state, "state")
    if fl_oz <= 0:
        raise DataValidationError("fl_oz must be positive")
    st = str(state).upper().strip()
    if st in {"OR", "MI"}:
        return 0.10
    if st == "CA":
        return 0.10 if fl_oz >= 24.0 else 0.05
    if st in {"NY", "ME", "VT", "CT", "MA", "IA", "HI"}:
        return 0.05
    return 0.0


def generate_calrecycle_destruction_notice(run_id: str, containers: int) -> dict:
    """Generate a CalRecycle notice of non-sale destruction for CRV tax recovery."""
    _req(run_id, "run_id")
    if containers < 0:
        raise DataValidationError("containers cannot be negative")
    return {"op": "generate_calrecycle_destruction_notice", "run_id": str(run_id), "containers": int(containers), "src": "recallstorm/pricing/bottle_deposit_credits.py"}


def audit_bottle_room_quarantine_bags(store_id: str, bags: int = 1) -> dict:
    """Audit bottle-room quarantine bags for glass breakage or pressurized fermentation hazards."""
    _req(store_id, "store_id")
    if bags < 0:
        raise DataValidationError("bags cannot be negative")
    return {"op": "audit_bottle_room_quarantine_bags", "store_id": str(store_id), "bags": int(bags), "src": "recallstorm/pricing/bottle_deposit_credits.py"}


def credit_customer_deposit_on_recall_return(retail_refund: float, crv_refund: float) -> float:
    """Combine base retail refund with full CRV bottle deposit refund."""
    if retail_refund < 0 or crv_refund < 0:
        raise DataValidationError("Negative refund inputs")
    return round(float(retail_refund) + float(crv_refund), 2)


def waive_handling_fee_on_recalled_flats(cases: int) -> dict:
    """Waive distributor empty-container handling fee adjustments on recalled full flats."""
    if cases < 0:
        raise DataValidationError("cases cannot be negative")
    return {"op": "waive_handling_fee_on_recalled_flats", "cases": int(cases), "waived": True, "src": "recallstorm/pricing/bottle_deposit_credits.py"}


def export_state_beverage_container_report(state: str, total_crv_usd: float) -> dict:
    """Export state beverage container deposit reconciliation report."""
    _req(state, "state")
    if total_crv_usd < 0:
        raise DataValidationError("total_crv_usd cannot be negative")
    return {"op": "export_state_beverage_container_report", "state": str(state).upper(), "total_crv_usd": round(float(total_crv_usd), 2), "src": "recallstorm/pricing/bottle_deposit_credits.py"}
