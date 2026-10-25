"""Unit tests for recallstorm.comms.shelf_signage_gen."""
from recallstorm.comms.shelf_signage_gen import (
    PublicNoticePlacard,
    RecallShelfTalker,
    audit_expired_placard_removal,
    check_state_mandated_signage_font_size,
    flag_missing_checklane_recall_mat,
    format_service_counter_allergen_notice,
    generate_qr_code_to_fda_press_release,
    map_placard_count_to_aisle_facings,
    print_bilingual_consumer_warning_cards,
    render_fda_compliant_shelf_placard_pdf,
    schedule_fourteen_day_sign_takedown,
    verify_sign_placement_via_photo_upload,
)


def test_shelf_signage_gen():
    assert RecallShelfTalker().status == "ACTIVE"
    assert PublicNoticePlacard().status == "ACTIVE"
    assert render_fda_compliant_shelf_placard_pdf("Sprinkles", "R1")["header"] == "URGENT PRODUCT RECALL"
    assert check_state_mandated_signage_font_size(28, 24)["compliant"] is True
    assert "fda.gov" in generate_qr_code_to_fda_press_release("R1")
    assert map_placard_count_to_aisle_facings(3) == 3
    assert schedule_fourteen_day_sign_takedown("2027-01-01", 14) == "2027-01-15"
    assert "RETIRO" in print_bilingual_consumer_warning_cards("Sprinkles")["es"]
    assert verify_sign_placement_via_photo_upload("WM1", "h1")["verified"] is True
    assert flag_missing_checklane_recall_mat("WM1", False)["flagged"] is True
    assert "PEANUT" in format_service_counter_allergen_notice("Bakery", "Peanut")
    assert audit_expired_placard_removal("2027-01-15", "2027-01-20")["remove_now"] is True
