"""Unit tests for recallstorm.inventory.ecommerce_dark_stores."""
from recallstorm.inventory.ecommerce_dark_stores import (
    MicroFulfillmentHold,
    OrderPickInterceptor,
    audit_locker_pickup_compartments,
    cancel_unfulfilled_bopis_line_items,
    flag_in_flight_last_mile_couriers,
    halt_autostore_bin_presentation,
    intercept_staged_curbside_totes,
    process_automatic_digital_refunds,
    purge_recalled_sku_from_web_search,
    quarantine_dark_store_decant_totes,
    reroute_instacart_shopper_pick_path,
    sync_virtual_inventory_availability,
)


def test_ecommerce_dark_stores():
    assert MicroFulfillmentHold().status == "ACTIVE"
    assert OrderPickInterceptor().status == "ACTIVE"
    assert purge_recalled_sku_from_web_search("S1")["delisted"] is True
    assert cancel_unfulfilled_bopis_line_items([{"order_id": "O1", "skus": ["S1"]}], "S1") == ["O1"]
    assert intercept_staged_curbside_totes("WM1", ["TOTE1"])["totes"] == ["TOTE1"]
    assert halt_autostore_bin_presentation("MFC1", "BIN9")["halted"] is True
    assert reroute_instacart_shopper_pick_path("O1", "SUB1")["sub_sku_id"] == "SUB1"
    assert flag_in_flight_last_mile_couriers(["D2", "D1"]) == ["D1", "D2"]
    assert process_automatic_digital_refunds(["O1", "O2"], 5.0) == 10.0
    assert quarantine_dark_store_decant_totes("DS1", 4)["tote_count"] == 4
    assert audit_locker_pickup_compartments("WM1", ["C1"])["compartments"] == ["C1"]
    assert sync_virtual_inventory_availability("S1", 0)["atp"] == 0
