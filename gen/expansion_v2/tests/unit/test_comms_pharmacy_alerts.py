"""Unit tests for recallstorm.comms.pharmacy_alerts."""
from recallstorm.comms.pharmacy_alerts import (
    NDCQuarantineNotice,
    PharmacyPatientOutreach,
    alert_prescribing_physician_via_efax,
    audit_controlled_substance_recall_dea,
    check_compounding_bulk_ingredient_lots,
    coordinate_medwatch_adverse_event_filing,
    flag_automated_pill_counter_cassettes,
    generate_patient_prescription_recall_letter,
    log_pharmacist_patient_counseling_calls,
    match_recalled_ndc_to_dispensing_log,
    process_central_fill_intercept_requests,
    quarantine_will_call_waiting_bin_bags,
)


def test_pharmacy_alerts():
    assert PharmacyPatientOutreach().status == "ACTIVE"
    assert NDCQuarantineNotice().status == "ACTIVE"
    assert match_recalled_ndc_to_dispensing_log([{"rx_id": "RX1", "ndc": "12345-678-90"}], "12345-678-90") == ["RX1"]
    assert generate_patient_prescription_recall_letter("RX1", "Syrup")["rx_id"] == "RX1"
    assert alert_prescribing_physician_via_efax("NPI1", "RX1")["sent"] is True
    assert quarantine_will_call_waiting_bin_bags("WM1", ["RX1"])["rx_ids"] == ["RX1"]
    assert flag_automated_pill_counter_cassettes("WM1", "CAS1")["locked"] is True
    assert check_compounding_bulk_ingredient_lots("L1", ["RX1", "RX2"])["rx_count"] == 2
    assert log_pharmacist_patient_counseling_calls("RPH1", "RX1")["pharmacist_id"] == "RPH1"
    assert coordinate_medwatch_adverse_event_filing("RX1", "Rash")["filed"] is True
    assert process_central_fill_intercept_requests("CF1", ["RX1"])["intercepted"] == 1
    assert audit_controlled_substance_recall_dea("12345-678-90")["form_222_required"] is True
