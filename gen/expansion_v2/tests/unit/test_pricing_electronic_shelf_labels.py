"""Unit tests for recallstorm.pricing.electronic_shelf_labels."""
from recallstorm.pricing.electronic_shelf_labels import (
    DigitalTagBlanker,
    EslFlashController,
    audit_esl_update_latency_sla,
    batch_update_aisle_esl_templates,
    detect_unresponsive_low_battery_tags,
    flash_esl_led_for_associate_pull,
    lock_esl_from_planogram_price_push,
    map_esl_mac_address_to_shelf_position,
    overwrite_esl_screen_with_recall_notice,
    restore_normal_price_display_layout,
    trigger_high_contrast_out_of_stock_view,
    verify_esl_gateway_transmission_ack,
)


def test_electronic_shelf_labels():
    assert EslFlashController().status == "ACTIVE"
    assert DigitalTagBlanker().status == "ACTIVE"
    assert flash_esl_led_for_associate_pull("AA:BB:CC", "RED", 300)["color"] == "RED"
    assert overwrite_esl_screen_with_recall_notice("AA:BB:CC", "S1")["overwritten"] is True
    assert verify_esl_gateway_transmission_ack("GW1", True)["acked"] is True
    assert detect_unresponsive_low_battery_tags([{"mac": "M1", "low_battery": True}]) == ["M1"]
    assert batch_update_aisle_esl_templates("WM1", "A01", 4)["count"] == 4
    assert lock_esl_from_planogram_price_push("M1")["locked"] is True
    assert map_esl_mac_address_to_shelf_position("M1", "A01-1-1-1")["loc_code"] == "A01-1-1-1"
    assert trigger_high_contrast_out_of_stock_view("M1")["inverted"] is True
    assert audit_esl_update_latency_sla(25.0, 60.0)["within_sla"] is True
    assert restore_normal_price_display_layout("M1")["restored"] is True
