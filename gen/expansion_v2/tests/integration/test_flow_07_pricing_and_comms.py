"""Integration test 07: core -> aliases -> store -> pricing -> comms."""
from contract import Sku, Store, StoreFormat, Verdict
from recallstorm.aliases.translations import translate_alias
from recallstorm.comms.customer_notifications import provide_self_service_lot_checker_url
from recallstorm.comms.store_notices import compile_single_page_store_action_sheet
from recallstorm.core.logging_setup import redact_text
from recallstorm.pricing.pos_sale_blocks import compile_pos_stop_sale_xml_payload
from recallstorm.pricing.substitute_pricing import authorize_equal_or_lesser_sub_price
from recallstorm.store.signage import shelf_tag_for_sku
from contract import Location


def test_flow_pricing_and_comms():
    st = Store("WM1563", StoreFormat.SUPERCENTER, "CA", "Lancaster", 34.6, -118.1, "D06", "DC_CENTRAL", "America/Los_Angeles")
    sku = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "baking", "SUGAR, E127", True, False, 6, 2.0, 10.0)
    assert translate_alias("E127", "en") == "FD&C Red No. 3"
    tag = shelf_tag_for_sku(sku, Location("A01", 1, 1, 1), Verdict.PULL)
    assert tag["action"] == "TAG_FLASH"
    xml = compile_pos_stop_sale_xml_payload(sku.gtin, "CA_AB418_RED3")
    assert sku.gtin in xml
    assert authorize_equal_or_lesser_sub_price(2.50, 3.25) == 2.50
    sheet = compile_single_page_store_action_sheet(st.store_id, [sku.sku_id])
    assert sheet["sku_count"] == 1
    url = provide_self_service_lot_checker_url("CA_AB418_RED3", sku.gtin)
    assert redact_text(f"Check {url} or email test@example.com").endswith("[REDACTED_EMAIL]")
