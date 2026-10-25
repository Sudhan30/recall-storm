"""Parse GS1 EPCIS supply chain movement events and SGTIN/LGTIN URNs."""
from __future__ import annotations

from dataclasses import dataclass, field
import re

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import gtin_check_digit, normalize_gtin

_SGTIN_RE = re.compile(r"urn:epc:(?:id:sgtin|class:lgtin):(\d+)\.(\d+)\.([^\s/]+)")


@dataclass
class EpcisDoc:
    """Parsed EPCIS document containing supply chain events."""

    events: list[dict] = field(default_factory=list)


def epc_to_gtin(epc_uri: str) -> str:
    """Convert a GS1 SGTIN or LGTIN EPC URN ('urn:epc:id:sgtin:Company.ItemRef.Serial') to a 14-digit GTIN."""
    if not isinstance(epc_uri, str):
        raise DataValidationError("epc_uri must be a string")
    if epc_uri.isdigit() and len(epc_uri) in {8, 12, 13, 14}:
        return normalize_gtin(epc_uri)
    m = _SGTIN_RE.search(epc_uri)
    if not m:
        raise DataValidationError(f"Invalid SGTIN/LGTIN EPC URN: {epc_uri!r}")
    comp, item_ref, _ = m.groups()
    indicator = item_ref[0]
    body13 = f"{indicator}{comp}{item_ref[1:]}"
    if len(body13) != 13:
        body13 = body13[:13].zfill(13)
    chk = gtin_check_digit(body13)
    return f"{body13}{chk}"


def epcis_lot(ev: dict) -> str | None:
    """Extract lot/batch number from an EPCIS event."""
    if "lot" in ev:
        return str(ev["lot"])
    ilmd = ev.get("ilmd") or {}
    if "lotNumber" in ilmd:
        return str(ilmd["lotNumber"])
    for u in ev.get("epcList", []) + ev.get("childEPCs", []):
        m = _SGTIN_RE.search(str(u))
        if m and "class:lgtin" in str(u):
            return m.group(3)
    return None


def epcis_location(ev: dict) -> str:
    """Extract business location from an EPCIS event."""
    return str(ev.get("bizLocation") or ev.get("readPoint") or "UNKNOWN")


def parse_epcis_event(ev: dict) -> dict:
    """Normalize a raw EPCIS ObjectEvent dictionary."""
    if not isinstance(ev, dict):
        raise DataValidationError("EPCIS event must be a dict")
    epcs = ev.get("epcList") or []
    gtins = [epc_to_gtin(str(u)) for u in epcs] if epcs else ([normalize_gtin(str(ev["gtin"]))] if ev.get("gtin") else [])
    return {
        "event_time": str(ev.get("eventTime", "2026-12-30T00:00:00Z")),
        "biz_step": str(ev.get("bizStep", "shipping")),
        "location": epcis_location(ev),
        "gtins": gtins,
        "lot": epcis_lot(ev),
    }


def epcis_object_event(gtin: str, lot: str, biz_location: str, event_time: str) -> dict:
    """Construct a normalized EPCIS ObjectEvent dictionary."""
    return parse_epcis_event(
        {
            "gtin": normalize_gtin(gtin),
            "lot": lot,
            "bizLocation": biz_location,
            "eventTime": event_time,
            "bizStep": "receiving",
        }
    )


def epcis_to_movements(events: list[dict]) -> list[dict]:
    """Convert raw EPCIS events into normalized movement records."""
    return [parse_epcis_event(e) for e in events]


def filter_epcis_by_gtin(events: list[dict], gtin: str) -> list[dict]:
    """Filter EPCIS movement records by 14-digit GTIN."""
    target = normalize_gtin(gtin)
    movements = [e if "gtins" in e else parse_epcis_event(e) for e in events]
    return [m for m in movements if target in m.get("gtins", [])]


def epcis_summary(events: list[dict]) -> dict:
    """Summarize EPCIS movement events."""
    movements = [e if "gtins" in e else parse_epcis_event(e) for e in events]
    locs = sorted({m["location"] for m in movements})
    return {"event_count": len(movements), "locations": locs}
