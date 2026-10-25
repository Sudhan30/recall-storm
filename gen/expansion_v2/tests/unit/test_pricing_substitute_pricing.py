"""Unit tests for recallstorm.pricing.substitute_pricing."""
from recallstorm.pricing.substitute_pricing import (
    PriceMatchOverrideRule,
    SubPriceParityEngine,
    authorize_equal_or_lesser_sub_price,
    calculate_promotional_price_carryover,
    cap_margin_erosion_on_national_sub,
    configure_bopis_substitution_discount,
    prevent_price_gouging_on_alternatives,
    reconcile_vendor_funded_sub_subsidy,
    restore_base_retail_after_restock,
    sync_electronic_shelf_label_sub_price,
    track_sub_price_override_redemptions,
    waive_delivery_fee_for_recalled_sub,
)


def test_substitute_pricing():
    assert PriceMatchOverrideRule().status == "ACTIVE"
    assert SubPriceParityEngine().status == "ACTIVE"
    assert authorize_equal_or_lesser_sub_price(2.98, 3.98) == 2.98
    assert configure_bopis_substitution_discount("O1", 2.98, 3.98)["discount"] == 1.0
    assert cap_margin_erosion_on_national_sub(2.50, 3.50, 2.0)["within_cap"] is True
    assert sync_electronic_shelf_label_sub_price("WM1", "SUB1", 2.98)["price"] == 2.98
    assert waive_delivery_fee_for_recalled_sub("O1", 7.95)["waived_usd"] == 7.95
    assert calculate_promotional_price_carryover(1.99, 2.99) == 1.99
    assert prevent_price_gouging_on_alternatives(20.0, 21.0, 0.10)["compliant"] is True
    assert track_sub_price_override_redemptions(100, 0.50) == 50.0
    assert reconcile_vendor_funded_sub_subsidy("V1", 50.0)["subsidy_usd"] == 50.0
    assert restore_base_retail_after_restock("SUB1", 3.98)["base_price"] == 3.98
