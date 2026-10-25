"""Suspend GS1 AI 8112 digital coupons and paper family prefixes."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class CouponRedemptionHalt:
    """Halt directive for manufacturer and store coupons on recalled SKUs."""

    ref_id: str = "CPN-HLT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ClearinghouseNotifier:
    """Notifier for coupon clearinghouses (Inmar / NCH) and GS1 AI(8112) registries."""

    ref_id: str = "CPN-CLR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def suspend_gs1_8112_universal_digital_coupons(ai_8112_code: str) -> dict:
    """Suspend a GS1 AI(8112) universal digital coupon offer code."""
    _req(ai_8112_code, "ai_8112_code")
    return {"op": "suspend_gs1_8112_universal_digital_coupons", "code": str(ai_8112_code), "suspended": True, "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def notify_inmar_nch_of_recalled_family_code(family_code: str, recall_id: str) -> dict:
    """Notify coupon clearinghouse of a recalled product family code."""
    _req(family_code, "family_code")
    _req(recall_id, "recall_id")
    return {"op": "notify_inmar_nch_of_recalled_family_code", "family_code": str(family_code), "recall_id": str(recall_id), "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def block_paper_coupon_family_prefix_scan(prefix: str) -> dict:
    """Block GS1 DataBar paper coupon family prefix at POS checkout."""
    _req(prefix, "prefix")
    return {"op": "block_paper_coupon_family_prefix_scan", "prefix": str(prefix), "blocked": True, "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def void_clipped_loyalty_wallet_offers(offer_id: str, affected_wallets: int = 100) -> dict:
    """Void clipped digital coupons in customer loyalty wallets and substitute a generic category offer."""
    _req(offer_id, "offer_id")
    if affected_wallets < 0:
        raise DataValidationError("affected_wallets cannot be negative")
    return {"op": "void_clipped_loyalty_wallet_offers", "offer_id": str(offer_id), "affected_wallets": int(affected_wallets), "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def reconcile_pre_recall_coupon_submissions(coupons_redeemed: int, face_value_usd: float) -> float:
    """Calculate manufacturer reimbursement due for coupons legitimately redeemed prior to recall timestamp."""
    if coupons_redeemed < 0 or face_value_usd < 0:
        raise DataValidationError("Negative coupon inputs")
    return round(float(coupons_redeemed) * float(face_value_usd), 2)


def prevent_Catalina_register_printer_triggers(trigger_gtin: str) -> dict:
    """Disable checkout lane Catalina coupon printer triggers for trigger_gtin."""
    _req(trigger_gtin, "trigger_gtin")
    return {"op": "prevent_Catalina_register_printer_triggers", "trigger_gtin": str(trigger_gtin), "disabled": True, "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def adjust_manufacturer_redemption_invoices(invoice_id: str, handling_fee_per_cpn: float = 0.08, count: int = 100) -> dict:
    """Calculate coupon clearinghouse invoice including $0.08 per-coupon handling fee."""
    _req(invoice_id, "invoice_id")
    if handling_fee_per_cpn < 0 or count < 0:
        raise DataValidationError("Negative invoice inputs")
    return {"op": "adjust_manufacturer_redemption_invoices", "invoice_id": str(invoice_id), "handling_fee_usd": round(handling_fee_per_cpn * count, 2), "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def flag_raincheck_coupon_combinations(tx_id: str) -> dict:
    """Flag stacked raincheck + coupon overrides on recalled SKUs."""
    _req(tx_id, "tx_id")
    return {"op": "flag_raincheck_coupon_combinations", "tx_id": str(tx_id), "flagged": True, "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def audit_override_coupon_key_entries(store_id: str, manual_entries: int = 0) -> dict:
    """Audit manual cashier vendor-coupon key entries."""
    _req(store_id, "store_id")
    if manual_entries < 0:
        raise DataValidationError("manual_entries cannot be negative")
    return {"op": "audit_override_coupon_key_entries", "store_id": str(store_id), "manual_entries": int(manual_entries), "src": "recallstorm/pricing/coupon_clearinghouse.py"}


def archive_suspended_promotion_campaigns(campaigns: list[str]) -> dict:
    """Archive suspended coupon campaigns."""
    if campaigns is None:
        raise DataValidationError("campaigns cannot be None")
    return {"op": "archive_suspended_promotion_campaigns", "count": len(campaigns), "campaigns": sorted(campaigns), "src": "recallstorm/pricing/coupon_clearinghouse.py"}
