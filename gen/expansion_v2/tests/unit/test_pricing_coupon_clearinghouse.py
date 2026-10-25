"""Unit tests for recallstorm.pricing.coupon_clearinghouse."""
from recallstorm.pricing.coupon_clearinghouse import (
    ClearinghouseNotifier,
    CouponRedemptionHalt,
    adjust_manufacturer_redemption_invoices,
    archive_suspended_promotion_campaigns,
    audit_override_coupon_key_entries,
    block_paper_coupon_family_prefix_scan,
    flag_raincheck_coupon_combinations,
    notify_inmar_nch_of_recalled_family_code,
    prevent_Catalina_register_printer_triggers,
    reconcile_pre_recall_coupon_submissions,
    suspend_gs1_8112_universal_digital_coupons,
    void_clipped_loyalty_wallet_offers,
)


def test_coupon_clearinghouse():
    assert CouponRedemptionHalt().status == "ACTIVE"
    assert ClearinghouseNotifier().status == "ACTIVE"
    assert suspend_gs1_8112_universal_digital_coupons("81120012345")["suspended"] is True
    assert notify_inmar_nch_of_recalled_family_code("FAM1", "REC1")["family_code"] == "FAM1"
    assert block_paper_coupon_family_prefix_scan("992")["blocked"] is True
    assert void_clipped_loyalty_wallet_offers("OFF1", 50)["affected_wallets"] == 50
    assert reconcile_pre_recall_coupon_submissions(20, 1.50) == 30.0
    assert prevent_Catalina_register_printer_triggers("07502264930572")["disabled"] is True
    assert adjust_manufacturer_redemption_invoices("INV1", 0.08, 100)["handling_fee_usd"] == 8.0
    assert flag_raincheck_coupon_combinations("TX1")["flagged"] is True
    assert audit_override_coupon_key_entries("WM1", 2)["manual_entries"] == 2
    assert archive_suspended_promotion_campaigns(["C2", "C1"])["count"] == 2
