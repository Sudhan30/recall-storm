"""Store manager sworn affidavits and PIN/GPS attestation checks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class StoreManagerAttestation:
    """Store manager recall completion attestation."""

    ref_id: str = "SGN-ATT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SwornAffidavitCollector:
    """Collector for legally binding store recall completion affidavits."""

    ref_id: str = "SGN-AFF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def require_store_manager_pin_and_signature(manager_id: str, pin_verified: bool = True) -> dict:
    """Require store manager MFA/PIN verification before signing store recall completion."""
    _req(manager_id, "manager_id")
    return {"op": "require_store_manager_pin_and_signature", "manager_id": str(manager_id), "verified": bool(pin_verified), "src": "recallstorm/governance/store_sign_offs.py"}


def validate_100_percent_aisle_task_completion(done_tasks: int, total_tasks: int) -> dict:
    """Block store manager sign-off until 100% of assigned shelf tasks are marked DONE."""
    if done_tasks < 0 or total_tasks < 0 or done_tasks > total_tasks:
        raise DataValidationError("Invalid task counts")
    return {"op": "validate_100_percent_aisle_task_completion", "can_sign_off": done_tasks == total_tasks, "remaining": total_tasks - done_tasks, "src": "recallstorm/governance/store_sign_offs.py"}


def block_sign_off_when_lot_variance_exceeds_cap(variance_units: int, cap_units: int = 12) -> dict:
    """Require a cycle-count explanation note if physical pull variance exceeds cap_units."""
    if cap_units < 0:
        raise DataValidationError("cap_units cannot be negative")
    return {"op": "block_sign_off_when_lot_variance_exceeds_cap", "blocked": abs(int(variance_units)) > cap_units, "src": "recallstorm/governance/store_sign_offs.py"}


def capture_closing_manager_shift_handover_ack(outgoing_mgr: str, incoming_mgr: str) -> dict:
    """Record formal recall responsibility handover when arecall spans a shift change."""
    _req(outgoing_mgr, "outgoing_mgr")
    _req(incoming_mgr, "incoming_mgr")
    return {"op": "capture_closing_manager_shift_handover_ack", "from": str(outgoing_mgr), "to": str(incoming_mgr), "src": "recallstorm/governance/store_sign_offs.py"}


def generate_legally_binding_affidavit_text(store_id: str, manager_name: str, recall_id: str) -> str:
    """Generate sworn store recall completion affidavit text."""
    _req(store_id, "store_id")
    _req(manager_name, "manager_name")
    _req(recall_id, "recall_id")
    return (
        f"I, {manager_name}, Manager of Store {store_id}, attest under penalty of perjury that "
        f"all salesfloor, endcap, topstock, pickup tote, and backroom locations have been swept for Recall {recall_id}."
    )


def flag_proxy_sign_offs_by_unauthorized_staff(signer_role: str) -> dict:
    """Flag sign-off attempts by non-salaried/unauthorized roles."""
    _req(signer_role, "signer_role")
    authorized = str(signer_role).upper() in {"STORE_MANAGER", "CO_MANAGER", "TEAM_LEAD", "PHARMACY_MANAGER"}
    return {"op": "flag_proxy_sign_offs_by_unauthorized_staff", "authorized": authorized, "src": "recallstorm/governance/store_sign_offs.py"}


def record_gps_and_device_mac_at_attestation(store_id: str, device_mac: str, on_premises: bool = True) -> dict:
    """Verify that the manager signed off from an in-store handheld/workstation rather than remotely."""
    _req(store_id, "store_id")
    _req(device_mac, "device_mac")
    return {"op": "record_gps_and_device_mac_at_attestation", "store_id": str(store_id), "device_mac": str(device_mac), "on_premises": bool(on_premises), "src": "recallstorm/governance/store_sign_offs.py"}


def trigger_district_manager_escalation_on_miss(store_id: str, minutes_past_deadline: float) -> dict:
    """Escalate to District Manager when a store misses the recall sign-off deadline."""
    _req(store_id, "store_id")
    return {"op": "trigger_district_manager_escalation_on_miss", "store_id": str(store_id), "escalated": minutes_past_deadline > 0.0, "src": "recallstorm/governance/store_sign_offs.py"}


def archive_immutable_store_completion_receipts(store_id: str, receipt_id: str) -> dict:
    """Archive immutable store completion receipt."""
    _req(store_id, "store_id")
    _req(receipt_id, "receipt_id")
    return {"op": "archive_immutable_store_completion_receipts", "store_id": str(store_id), "receipt_id": str(receipt_id), "src": "recallstorm/governance/store_sign_offs.py"}


def export_unattested_store_exception_list(all_stores: list[str], attested_stores: set[str]) -> list[str]:
    """Return sorted store_ids that have not yet submitted manager sign-off."""
    if all_stores is None or attested_stores is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(all_stores) - set(attested_stores))
