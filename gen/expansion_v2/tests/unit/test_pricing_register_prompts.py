"""Unit tests for recallstorm.pricing.register_prompts."""
from recallstorm.pricing.register_prompts import (
    A_B_test_prompt_clarity_speed,
    CashierPromptConfig,
    LotCheckDialogBuilder,
    build_lot_prefix_validation_screen,
    capture_cashier_entered_lot_string,
    configure_date_code_entry_prompt,
    disable_expired_lot_check_prompts,
    display_safe_lot_visual_guide,
    localize_register_prompt_translations,
    require_supervisor_key_flick_override,
    throttle_prompt_for_unaffected_upcs,
    track_prompt_bypass_rate_by_cashier,
)


def test_register_prompts():
    assert CashierPromptConfig().status == "ACTIVE"
    assert LotCheckDialogBuilder().status == "ACTIVE"
    assert configure_date_code_entry_prompt("S1", "2026-12-31")["sku_id"] == "S1"
    assert build_lot_prefix_validation_screen("S1", ["L26"])["banned_prefixes"] == ["L26"]
    assert require_supervisor_key_flick_override("CLASS_I") is True
    assert display_safe_lot_visual_guide("S1", "https://img.example/1")["sku_id"] == "S1"
    assert capture_cashier_entered_lot_string("L2601", ["L26*"])["sale_blocked"] is True
    assert throttle_prompt_for_unaffected_upcs("U1", {"U1"}) is True
    assert track_prompt_bypass_rate_by_cashier(8, 10)["flagged"] is True
    assert "[ES]" in localize_register_prompt_translations("Check Lot", "es")["text"]
    assert A_B_test_prompt_clarity_speed(4.2, 6.1) == "A"
    assert disable_expired_lot_check_prompts("S1", 100, 90)["disabled"] is True
