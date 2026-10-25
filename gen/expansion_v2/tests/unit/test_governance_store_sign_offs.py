"""Unit tests for recallstorm.governance.store_sign_offs."""
from recallstorm.governance.store_sign_offs import (
    StoreManagerAttestation,
    SwornAffidavitCollector,
    archive_immutable_store_completion_receipts,
    block_sign_off_when_lot_variance_exceeds_cap,
    capture_closing_manager_shift_handover_ack,
    export_unattested_store_exception_list,
    flag_proxy_sign_offs_by_unauthorized_staff,
    generate_legally_binding_affidavit_text,
    record_gps_and_device_mac_at_attestation,
    require_store_manager_pin_and_signature,
    trigger_district_manager_escalation_on_miss,
    validate_100_percent_aisle_task_completion,
)


def test_store_sign_offs():
    assert StoreManagerAttestation().status == "ACTIVE"
    assert SwornAffidavitCollector().status == "ACTIVE"
    assert require_store_manager_pin_and_signature("MGR1", True)["verified"] is True
    assert validate_100_percent_aisle_task_completion(10, 10)["can_sign_off"] is True
    assert block_sign_off_when_lot_variance_exceeds_cap(20, 12)["blocked"] is True
    assert capture_closing_manager_shift_handover_ack("M1", "M2")["to"] == "M2"
    assert "penalty of perjury" in generate_legally_binding_affidavit_text("WM1", "Jane Doe", "R1")
    assert flag_proxy_sign_offs_by_unauthorized_staff("STORE_MANAGER")["authorized"] is True
    assert record_gps_and_device_mac_at_attestation("WM1", "AA:BB", True)["on_premises"] is True
    assert trigger_district_manager_escalation_on_miss("WM1", 15.0)["escalated"] is True
    assert archive_immutable_store_completion_receipts("WM1", "RCP1")["receipt_id"] == "RCP1"
    assert export_unattested_store_exception_list(["WM1", "WM2"], {"WM1"}) == ["WM2"]
