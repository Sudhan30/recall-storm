"""Circular ad pulls, BOGO cancellations, and raincheck suspensions."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PromoConflictScanner:
    """Scanner detecting recalled SKUs in active or upcoming promotions."""

    ref_id: str = "PRM-SCN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CircularAdPuller:
    """Controller pulling recalled items from weekly circular ads."""

    ref_id: str = "PRM-CIR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def scan_upcoming_weekly_print_circulars(ad_skus: list[str], recalled_skus: set[str]) -> list[str]:
    """Return sorted SKUs appearing in both ad_skus and recalled_skus."""
    if ad_skus is None or recalled_skus is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(ad_skus) & set(recalled_skus))


def flag_recalled_items_in_digital_coupons(coupons: list[dict], sku_id: str) -> list[str]:
    """Return coupon_ids targeting a recalled sku_id."""
    if coupons is None:
        raise DataValidationError("coupons cannot be None")
    _req(sku_id, "sku_id")
    return [str(c["coupon_id"]) for c in coupons if c.get("sku_id") == sku_id]


def cancel_active_bogo_deal_triggers(promo_id: str, sku_id: str) -> dict:
    """Cancel an active Buy-One-Get-One (BOGO) promotion trigger."""
    _req(promo_id, "promo_id")
    _req(sku_id, "sku_id")
    return {"op": "cancel_active_bogo_deal_triggers", "promo_id": str(promo_id), "sku_id": str(sku_id), "cancelled": True, "src": "recallstorm/pricing/promotion_conflicts.py"}


def remove_sku_from_endcap_theme_kits(kit_id: str, sku_id: str) -> dict:
    """Remove a recalled SKU from a promotional endcap theme kit."""
    _req(kit_id, "kit_id")
    _req(sku_id, "sku_id")
    return {"op": "remove_sku_from_endcap_theme_kits", "kit_id": str(kit_id), "sku_id": str(sku_id), "src": "recallstorm/pricing/promotion_conflicts.py"}


def calculate_raincheck_liability_suspension(sku_id: str) -> dict:
    """Suspend raincheck issuance on advertised items pulled due to regulatory recall."""
    _req(sku_id, "sku_id")
    return {"op": "calculate_raincheck_liability_suspension", "sku_id": str(sku_id), "rainchecks_suspended": True, "src": "recallstorm/pricing/promotion_conflicts.py"}


def coordinate_ad_correction_apology_sign(store_id: str, sku_name: str) -> dict:
    """Generate a front-vestibule ad correction notice when a circular item is recalled after print."""
    _req(store_id, "store_id")
    _req(sku_name, "sku_name")
    return {"op": "coordinate_ad_correction_apology_sign", "store_id": str(store_id), "sku_name": str(sku_name), "src": "recallstorm/pricing/promotion_conflicts.py"}


def reallocate_feature_space_to_sub(endcap_id: str, sub_sku_id: str) -> dict:
    """Reassign promotional endcap feature space to an approved substitute SKU."""
    _req(endcap_id, "endcap_id")
    _req(sub_sku_id, "sub_sku_id")
    return {"op": "reallocate_feature_space_to_sub", "endcap_id": str(endcap_id), "sub_sku_id": str(sub_sku_id), "src": "recallstorm/pricing/promotion_conflicts.py"}


def halt_automated_social_media_ads(campaign_id: str) -> dict:
    """Pause automated retail media / social ad campaigns featuring a recalled product."""
    _req(campaign_id, "campaign_id")
    return {"op": "halt_automated_social_media_ads", "campaign_id": str(campaign_id), "paused": True, "src": "recallstorm/pricing/promotion_conflicts.py"}


def adjust_vendor_coop_ad_funding_claim(coop_budget_usd: float, days_active: int, total_days: int = 7) -> float:
    """Calculate pro-rata co-op advertising allowance adjustment."""
    if coop_budget_usd < 0 or days_active < 0 or total_days <= 0 or days_active > total_days:
        raise DataValidationError("Invalid co-op budget parameters")
    return round(coop_budget_usd * ((total_days - days_active) / total_days), 2)


def audit_loyalty_app_personalized_offers(offer_ids: list[str]) -> list[str]:
    """Purge personalized loyalty app offers recommending recalled SKUs."""
    if offer_ids is None:
        raise DataValidationError("offer_ids cannot be None")
    return sorted(str(o) for o in offer_ids if str(o).strip())
