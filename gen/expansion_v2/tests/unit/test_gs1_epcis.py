"""Unit tests for recallstorm.gs1.epcis."""
from recallstorm.gs1.epcis import (
    EpcisDoc,
    epc_to_gtin,
    epcis_location,
    epcis_lot,
    epcis_object_event,
    epcis_summary,
    epcis_to_movements,
    filter_epcis_by_gtin,
    parse_epcis_event,
)


def test_epcis_events():
    urn = "urn:epc:class:lgtin:0073621.000701.LOT99"
    gtin = epc_to_gtin(urn)
    assert gtin == "00073621007017"
    raw = {"epcList": [urn], "bizLocation": "WM1563", "eventTime": "2026-12-29T10:00:00Z"}
    assert epcis_lot(raw) == "LOT99"
    assert epcis_location(raw) == "WM1563"
    parsed = parse_epcis_event(raw)
    assert parsed["gtins"] == [gtin]
    ev2 = epcis_object_event(gtin, "LOT100", "DC_NORTH", "2026-12-28T10:00:00Z")
    movs = epcis_to_movements([raw, ev2])
    assert len(filter_epcis_by_gtin(movs, gtin)) == 2
    assert epcis_summary(movs)["event_count"] == 2
    doc = EpcisDoc(movs)
    assert len(doc.events) == 2
