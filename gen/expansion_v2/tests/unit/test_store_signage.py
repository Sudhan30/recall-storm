"""Unit tests for recallstorm.store.signage."""
from contract import DecidedBy, Facing, Location, Sku, SkuDecision, Store, StoreFormat, Verdict
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


def test_store_signage():
    st = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    sku = Sku("S1", "00012345678905", "Candy", "B", "candy", "RED 3", True, False, 12, 1.0, 5.0)
    loc = Location("A01", 1, 1, 1)
    dec = SkuDecision("S1", Verdict.PULL, "RED3", "RED 3", 0, 5, ("CA_AB418_RED3",), DecidedBy.RULE, "r")

    assert sign_language(st) == "en-es"
    assert "RECALLED" in sign_template(Verdict.PULL, "en-es")
    assert "S1" in tag_flash_text(sku, Verdict.PULL)
    tag = shelf_tag_for_sku(sku, loc, Verdict.PULL)
    assert tag["action"] == "TAG_FLASH"
    tags = tags_for_store(st, [Facing("WM1", "S1", loc, 10)], {"S1": sku}, {"S1": dec})
    assert len(tags) == 1
    q = printer_queue(tags)
    assert len(q) == 1
    assert tag_to_record(tag)["src"] == "recallstorm/store/signage.py"
    assert sign_summary(tags)["total_tags"] == 1
    sp = SignPrinter("WM1", q)
    assert len(sp.jobs) == 1
