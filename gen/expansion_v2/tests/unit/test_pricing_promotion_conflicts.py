"""Unit tests for recallstorm.pricing.promotion_conflicts."""
from recallstorm.pricing.promotion_conflicts import (
    CircularAdPuller,
    PromoConflictScanner,
    adjust_vendor_coop_ad_funding_claim,
    audit_loyalty_app_personalized_offers,
    calculate_raincheck_liability_suspension,
    cancel_active_bogo_deal_triggers,
    coordinate_ad_correction_apology_sign,
    flag_recalled_items_in_digital_coupons,
    halt_automated_social_media_ads,
    reallocate_feature_space_to_sub,
    remove_sku_from_endcap_theme_kits,
    scan_upcoming_weekly_print_circulars,
)


def test_promotion_conflicts():
    assert PromoConflictScanner().status == "ACTIVE"
    assert CircularAdPuller().status == "ACTIVE"
    assert scan_upcoming_weekly_print_circulars(["S1", "S2"], {"S1"}) == ["S1"]
    assert flag_recalled_items_in_digital_coupons([{"coupon_id": "C1", "sku_id": "S1"}], "S1") == ["C1"]
    assert cancel_active_bogo_deal_triggers("PRM1", "S1")["cancelled"] is True
    assert remove_sku_from_endcap_theme_kits("KIT1", "S1")["sku_id"] == "S1"
    assert calculate_raincheck_liability_suspension("S1")["rainchecks_suspended"] is True
    assert coordinate_ad_correction_apology_sign("WM1", "Sprinkles")["store_id"] == "WM1"
    assert reallocate_feature_space_to_sub("EC1", "SUB1")["sub_sku_id"] == "SUB1"
    assert halt_automated_social_media_ads("CMP1")["paused"] is True
    assert adjust_vendor_coop_ad_funding_claim(700.0, 2, 7) == 500.0
    assert audit_loyalty_app_personalized_offers(["O2", "O1"]) == ["O1", "O2"]
