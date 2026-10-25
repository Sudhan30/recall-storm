"""Integration test 02: core -> ingest -> gs1 -> store -> scenario_gs1."""
from datetime import datetime
from recallstorm.core.clock import iso_with_offset
from recallstorm.gs1.digital_link import build_digital_link, digital_link_gtin, digital_link_lot
from recallstorm.ingest.openfda_enforcement import parse_enforcement_report
from recallstorm.ingest.planogram import parse_planogram_row
from recallstorm.ingest.store_list import store_from_row
from recallstorm.scenario_gs1.lot_pull import lot_pull_tasks
from recallstorm.store.layout import build_layout


def test_flow_gs1_store_scenario():
    rep = {
        "recall_number": "F-2026-09",
        "product_description": "Rainbow Sprinkles 07502264930572",
        "code_info": "Lot: L2601A",
        "reason_for_recall": "Contains FD&C Red No. 3",
        "distribution_pattern": "CA",
    }
    parsed = parse_enforcement_report(rep)
    uri = build_digital_link(parsed["gtins"][0], lot=parsed["lots"][0])
    assert digital_link_gtin(uri) == "07502264930572"
    assert digital_link_lot(uri) == "L2601A"

    store = store_from_row({"store_id": "WM1563", "format": "SUPERCENTER", "state": "CA", "lat": 34.69, "lon": -118.17})
    facing = parse_planogram_row({"store_id": "WM1563", "sku_id": "FDC1034191", "loc_code": "A01-1-1-1", "units": 12})
    layout = build_layout(store, [facing])
    assert len(layout.locations) == 1

    win = [
        iso_with_offset(datetime.fromisoformat("2026-12-30T22:00:00-08:00")),
        iso_with_offset(datetime.fromisoformat("2026-12-30T22:15:00-08:00")),
    ]
    tasks = lot_pull_tasks(store, [facing], parsed["lots"], {"FDC1034191": ["L2601A"]}, "WM1563-A01", win)
    assert len(tasks) == 1 and tasks[0]["action"] == "PULL"
