"""Unit tests for recallstorm.store.signage."""
from contract import Facing, Location, Sku, StoreFormat
from recallstorm.store.signage import (
    SignPrinter,
    printer_queue,
    shelf_tag_for_sku,
    sign_language,
    sign_summary,
    sign_template,
    tag_flash_text,
    tag_to_record,
    tags_for_store,
)


def test_signage_functions():
    sku = Sku("S1", "00012345678905", "Candy", "Brand", "candy", "RED 3", True, False, 12, 1.0, 5.0)
    loc = Location("A01", 1, 2, 3)
    assert "Brand Candy" in tag_flash_text(sku, ["CA_AB418_RED3"])
    assert sign_template(StoreFormat.SAMS) == "PALLET_PLACARD"
    assert sign_language("CA") == "en/es"
    tag = shelf_tag_for_sku("WM1", sku, loc)
    assert tag_to_record(tag)["sku_id"] == "S1"
    tags = tags_for_store("WM1", [Facing("WM1", "S1", loc, 10)], {"S1": sku}, {"S1"})
    q = printer_queue(tags)
    assert len(q) == 1
    assert sign_summary(q)["total_tags"] == 1
    sp = SignPrinter("WM1")
    assert sp.store_id == "WM1"
