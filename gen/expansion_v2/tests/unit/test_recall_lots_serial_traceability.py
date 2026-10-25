"""Unit tests for recallstorm.recall_lots.serial_traceability."""
from recallstorm.gs1.gtin import gtin_check_digit
from recallstorm.recall_lots.serial_traceability import (
    CaseSerialTracker,
    SerialShippingContainerCode,
    build_serial_custody_chain,
    calculate_serial_recovery_rate,
    detect_duplicate_counterfeit_serials,
    export_unaccounted_serial_list,
    flag_orphan_serial_scans,
    match_sscc18_pallet_labels,
    query_serialized_receiving_logs,
    resolve_mixed_pallet_parent_child,
    trace_serialized_case_to_aisle,
    verify_epcis_commissioning_event,
)


def test_serial_traceability():
    assert SerialShippingContainerCode().status == "ACTIVE"
    assert CaseSerialTracker().status == "ACTIVE"
    body17 = "00073621000000001"
    sscc = f"{body17}{gtin_check_digit(body17)}"
    assert match_sscc18_pallet_labels(sscc)["valid"] is True
    assert trace_serialized_case_to_aisle("SER1", "A04")["aisle"] == "A04"
    assert resolve_mixed_pallet_parent_child(sscc, ["S2", "S1"])["children"] == ["S1", "S2"]
    assert verify_epcis_commissioning_event("SER1", True)["valid"] is True
    assert flag_orphan_serial_scans(["S1", "S2"], {"S1"}) == ["S2"]
    assert query_serialized_receiving_logs("WM1", ["S1"])["found"] == 1
    assert build_serial_custody_chain("S1", ["DC1", "WM1"])["hops"] == ["DC1", "WM1"]
    assert detect_duplicate_counterfeit_serials(["S1", "S2", "S1"]) == ["S1"]
    assert calculate_serial_recovery_rate(8, 10) == 80.0
    assert export_unaccounted_serial_list({"S1", "S2"}, {"S1"}) == ["S2"]
