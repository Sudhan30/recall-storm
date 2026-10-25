"""Unit tests for recallstorm.comms.store_notices."""
from recallstorm.comms.store_notices import (
    StoreActionBulletin,
    UrgentRecallFlash,
    archive_superseded_bulletin_versions,
    compile_single_page_store_action_sheet,
    embed_product_package_reference_photos,
    generate_printable_backroom_poster_pdf,
    highlight_affected_lot_visual_callouts,
    push_urgent_banner_to_zebra_handhelds,
    route_notice_by_store_department_scope,
    track_store_manager_read_receipt_ack,
    translate_bulletin_for_multilingual_crews,
    version_control_amended_recall_notices,
)


def test_store_notices():
    assert StoreActionBulletin().status == "ACTIVE"
    assert UrgentRecallFlash().status == "ACTIVE"
    assert compile_single_page_store_action_sheet("WM1", ["S1", "S2"])["sku_count"] == 2
    assert "L2601" in highlight_affected_lot_visual_callouts("L2601")
    assert len(embed_product_package_reference_photos("S1", ["u1"])["photos"]) == 1
    assert "es" in translate_bulletin_for_multilingual_crews("Pull S1")["langs"]
    assert route_notice_by_store_department_scope("grocery", ["WM1"])["dept"] == "GROCERY"
    assert track_store_manager_read_receipt_ack("WM1", 10.0)["within_sla"] is True
    assert version_control_amended_recall_notices("REC1", 2) == "REC1-REV02"
    assert generate_printable_backroom_poster_pdf("WM1", "REC1")["store_id"] == "WM1"
    assert push_urgent_banner_to_zebra_handhelds("WM1", "Urgent")["pushed"] is True
    assert archive_superseded_bulletin_versions(["REV01"])["archived_count"] == 1
