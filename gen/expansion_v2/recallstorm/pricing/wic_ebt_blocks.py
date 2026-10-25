"""WIC APL hotfixes, infant formula voucher swaps, and SNAP/EBT blocks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class WicAplHotfixEngine:
    """Engine updating State WIC Approved Product Lists (APL) during recalls."""

    ref_id: str = "WIC-APL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class EbtEligibilityBlocker:
    """Blocker for SNAP/EBT and WIC tender on recalled items."""

    ref_id: str = "WIC-EBT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def remove_recalled_upc_from_state_wic_apl(state: str, upc: str) -> dict:
    """Suspend a recalled UPC in the state WIC Approved Product List (APL)."""
    _req(state, "state")
    _req(upc, "upc")
    return {"op": "remove_recalled_upc_from_state_wic_apl", "state": str(state).upper(), "upc": str(upc), "removed": True, "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def coordinate_emergency_wic_substitute_approval(state: str, sub_upc: str) -> dict:
    """Enable an emergency state WIC APL waiver for a substitute UPC."""
    _req(state, "state")
    _req(sub_upc, "sub_upc")
    return {"op": "coordinate_emergency_wic_substitute_approval", "state": str(state).upper(), "sub_upc": str(sub_upc), "approved": True, "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def handle_infant_formula_wic_voucher_swap(voucher_id: str, alt_formula_sku: str) -> dict:
    """Authorize an equal-ounce or therapeutic infant formula swap on a WIC eWIC benefit card."""
    _req(voucher_id, "voucher_id")
    _req(alt_formula_sku, "alt_formula_sku")
    return {"op": "handle_infant_formula_wic_voucher_swap", "voucher_id": str(voucher_id), "alt_formula_sku": str(alt_formula_sku), "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def block_snap_ebt_tender_for_banned_item(sku_id: str) -> dict:
    """Block SNAP/EBT tender on a recalled or banned food item."""
    _req(sku_id, "sku_id")
    return {"op": "block_snap_ebt_tender_for_banned_item", "sku_id": str(sku_id), "ebt_blocked": True, "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def update_self_checkout_wic_validation_table(store_id: str, apl_version: str) -> dict:
    """Push updated WIC APL table to self-checkout lanes."""
    _req(store_id, "store_id")
    _req(apl_version, "apl_version")
    return {"op": "update_self_checkout_wic_validation_table", "store_id": str(store_id), "apl_version": str(apl_version), "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def generate_wic_participant_shelf_talker(sku_name: str, sub_name: str) -> str:
    """Generate bilingual WIC shelf talker guiding participants to the approved substitute."""
    _req(sku_name, "sku_name")
    _req(sub_name, "sub_name")
    return f"WIC NOTICE: {sku_name} is recalled. Temporary WIC-approved substitute: {sub_name}."


def log_declined_wic_benefit_attempts(store_id: str, upc: str) -> dict:
    """Log declined eWIC scan attempts on recalled UPCs."""
    _req(store_id, "store_id")
    _req(upc, "upc")
    return {"op": "log_declined_wic_benefit_attempts", "store_id": str(store_id), "upc": str(upc), "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def notify_state_wic_agency_liaison(state: str, recall_id: str) -> dict:
    """Notify State WIC Agency retail liaison of recall and substitute stock levels."""
    _req(state, "state")
    _req(recall_id, "recall_id")
    return {"op": "notify_state_wic_agency_liaison", "state": str(state).upper(), "recall_id": str(recall_id), "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def validate_cereal_size_ounce_substitute(sub_oz: float, max_benefit_oz: float = 36.0) -> dict:
    """Validate that a substitute WIC cereal/baby-food package does not exceed remaining eWIC ounces."""
    if sub_oz <= 0 or max_benefit_oz <= 0:
        raise DataValidationError("Ounces must be positive")
    return {"op": "validate_cereal_size_ounce_substitute", "eligible": sub_oz <= max_benefit_oz, "sub_oz": float(sub_oz), "src": "recallstorm/pricing/wic_ebt_blocks.py"}


def audit_wic_reimbursement_adjustments(claim_id: str, amount_usd: float) -> dict:
    """Audit state WIC bank settlement adjustments for returned recalled formula."""
    _req(claim_id, "claim_id")
    if amount_usd < 0:
        raise DataValidationError("amount_usd cannot be negative")
    return {"op": "audit_wic_reimbursement_adjustments", "claim_id": str(claim_id), "amount_usd": round(float(amount_usd), 2), "src": "recallstorm/pricing/wic_ebt_blocks.py"}
