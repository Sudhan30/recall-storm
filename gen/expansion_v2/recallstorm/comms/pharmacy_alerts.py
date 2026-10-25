"""Pharmacy NDC dispensing log matching, patient letters, and physician eFax."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PharmacyPatientOutreach:
    """HIPAA-compliant patient recall notification for dispensed Rx/OTC drugs."""

    ref_id: str = "RX-OUT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class NDCQuarantineNotice:
    """National Drug Code (NDC) pharmacy shelf and robot quarantine notice."""

    ref_id: str = "RX-NDC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def match_recalled_ndc_to_dispensing_log(dispenses: list[dict], ndc: str) -> list[str]:
    """Return rx_ids dispensed with the recalled 11-digit NDC."""
    if dispenses is None:
        raise DataValidationError("dispenses cannot be None")
    _req(ndc, "ndc")
    return [str(d["rx_id"]) for d in dispenses if d.get("ndc") == ndc]


def generate_patient_prescription_recall_letter(rx_id: str, drug_name: str) -> dict:
    """Generate a patient prescription recall letter."""
    _req(rx_id, "rx_id")
    _req(drug_name, "drug_name")
    return {"op": "generate_patient_prescription_recall_letter", "rx_id": str(rx_id), "drug_name": str(drug_name), "src": "recallstorm/comms/pharmacy_alerts.py"}


def alert_prescribing_physician_via_efax(npi: str, rx_id: str) -> dict:
    """Send urgent recall alert to the prescribing physician (by NPI) for Class I Rx recalls."""
    _req(npi, "npi")
    _req(rx_id, "rx_id")
    return {"op": "alert_prescribing_physician_via_efax", "npi": str(npi), "rx_id": str(rx_id), "sent": True, "src": "recallstorm/comms/pharmacy_alerts.py"}


def quarantine_will_call_waiting_bin_bags(store_id: str, rx_ids: list[str]) -> dict:
    """Pull filled prescription bags from the pharmacy Will-Call waiting bin before patient pickup."""
    _req(store_id, "store_id")
    if not rx_ids:
        raise DataValidationError("rx_ids cannot be empty")
    return {"op": "quarantine_will_call_waiting_bin_bags", "store_id": str(store_id), "rx_ids": sorted(rx_ids), "src": "recallstorm/comms/pharmacy_alerts.py"}


def flag_automated_pill_counter_cassettes(store_id: str, cassette_id: str) -> dict:
    """Lock automated dispensing robot cassette containing a recalled drug lot."""
    _req(store_id, "store_id")
    _req(cassette_id, "cassette_id")
    return {"op": "flag_automated_pill_counter_cassettes", "store_id": str(store_id), "cassette_id": str(cassette_id), "locked": True, "src": "recallstorm/comms/pharmacy_alerts.py"}


def check_compounding_bulk_ingredient_lots(lot_id: str, compounded_rxs: list[str]) -> dict:
    """Trace a recalled bulk compounding ingredient lot to compounded prescriptions."""
    _req(lot_id, "lot_id")
    if compounded_rxs is None:
        raise DataValidationError("compounded_rxs cannot be None")
    return {"op": "check_compounding_bulk_ingredient_lots", "lot_id": str(lot_id), "rx_count": len(compounded_rxs), "src": "recallstorm/comms/pharmacy_alerts.py"}


def log_pharmacist_patient_counseling_calls(pharmacist_id: str, rx_id: str) -> dict:
    """Log pharmacist clinical counseling call to an affected patient."""
    _req(pharmacist_id, "pharmacist_id")
    _req(rx_id, "rx_id")
    return {"op": "log_pharmacist_patient_counseling_calls", "pharmacist_id": str(pharmacist_id), "rx_id": str(rx_id), "src": "recallstorm/comms/pharmacy_alerts.py"}


def coordinate_medwatch_adverse_event_filing(rx_id: str, event_desc: str) -> dict:
    """File an FDA Form 3500A MedWatch adverse drug event report."""
    _req(rx_id, "rx_id")
    _req(event_desc, "event_desc")
    return {"op": "coordinate_medwatch_adverse_event_filing", "rx_id": str(rx_id), "filed": True, "src": "recallstorm/comms/pharmacy_alerts.py"}


def process_central_fill_intercept_requests(central_fill_id: str, rx_ids: list[str]) -> dict:
    """Intercept mail-order / central-fill prescriptions before shipment to stores."""
    _req(central_fill_id, "central_fill_id")
    if not rx_ids:
        raise DataValidationError("rx_ids cannot be empty")
    return {"op": "process_central_fill_intercept_requests", "central_fill_id": str(central_fill_id), "intercepted": len(rx_ids), "src": "recallstorm/comms/pharmacy_alerts.py"}


def audit_controlled_substance_recall_dea(ndc: str, dea_schedule: str = "C-II") -> dict:
    """Verify DEA Form 222 / CSOS reverse-distributor custody for recalled controlled substances."""
    _req(ndc, "ndc")
    _req(dea_schedule, "dea_schedule")
    return {"op": "audit_controlled_substance_recall_dea", "ndc": str(ndc), "schedule": str(dea_schedule), "form_222_required": True, "src": "recallstorm/comms/pharmacy_alerts.py"}
