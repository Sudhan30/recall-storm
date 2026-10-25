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


def test_epcis_functions():
    gtin = epc_to_gtin("urn:epc:id:sgtin:0736210.007017.1001")
    assert len(gtin) == 14
    raw = {
        "epcList": ["urn:epc:id:sgtin:0736210.007017.1001"],
        "ilmd": {"lotNumber": "L2601"},
        "readPoint": "DC_NORTH",
        "eventTime": "2026-12-29T10:00:00Z",
    }
    assert epcis_lot(raw) == "L2601"
    assert epcis_location(raw) == "DC_NORTH"
    ev = parse_epcis_event(raw)
    ev2 = epcis_object_event(gtin, "L2601", "WM1575", "2026-12-30T10:00:00Z")
    movs = epcis_to_movements([ev2, ev])
    assert movs[0]["location"] == "DC_NORTH"
    assert len(filter_epcis_by_gtin(movs, gtin)) == 2
    doc = EpcisDoc(tuple(movs))
    assert len(doc.events) == 2
    assert epcis_summary(movs)["event_count"] == 2
