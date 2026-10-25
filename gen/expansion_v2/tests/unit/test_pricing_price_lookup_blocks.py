"""Unit tests for recallstorm.pricing.price_lookup_blocks."""
from recallstorm.pricing.price_lookup_blocks import (
    PluScaleDeactivator,
    TareAndPluSync,
    archive_deactivated_plu_recipe_text,
    audit_unnetworked_standalone_scales,
    block_produce_cashier_look_up_menu,
    disable_bakery_self_serve_plu_buttons,
    monitor_scale_firmware_sync_errors,
    prevent_in_store_bar_code_printing,
    purge_recalled_plu_from_deli_scales,
    push_scale_network_lockout_file,
    restore_cleared_plu_price_tables,
    verify_hobart_toledo_scale_ack,
)


def test_price_lookup_blocks():
    assert PluScaleDeactivator().status == "ACTIVE"
    assert TareAndPluSync().status == "ACTIVE"
    assert purge_recalled_plu_from_deli_scales("WM1", "4011")["purged"] is True
    assert disable_bakery_self_serve_plu_buttons("WM1", ["B1"])["buttons"] == ["B1"]
    assert push_scale_network_lockout_file("WM1", 6)["scale_count"] == 6
    assert verify_hobart_toledo_scale_ack("10.0.0.5", True)["acked"] is True
    assert block_produce_cashier_look_up_menu("4011")["blocked"] is True
    assert prevent_in_store_bar_code_printing("4011")["print_disabled"] is True
    assert archive_deactivated_plu_recipe_text("4011", "SUGAR, RED 3")["plu_code"] == "4011"
    assert monitor_scale_firmware_sync_errors(["10.0.0.9"]) == ["10.0.0.9"]
    assert restore_cleared_plu_price_tables("4011", "QA1")["restored"] is True
    assert audit_unnetworked_standalone_scales("WM1", 1)["manual_update_required"] is True
