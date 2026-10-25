"""GS1 EPCIS 2.0 supply chain event parser for lot and movement tracking."""
from __future__ import annotations

import re
from dataclasses import dataclass
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import gtin_check_digit, normalize_gtin

_SGTIN_RE = re.compile(r"urn:epc:id:sgtin:(\d+)\.(\d+)\.([A-Za-z0-9\-]+)")


@dataclass(frozen=True)
class EpcisDoc:
    """Parsed EPCIS document containing supply chain events."""

    events: tuple[dict, ...]


def epc_to_gtin(epc_uri: str) -> str:
    """Convert a GS1 SGTIN EPC URI (urn:epc:id:sgtin:CompanyPrefix.IndicatorItemRef.Serial) to GTIN-14."""
    if not isinstance(epc_uri, str) or not epc_uri.strip():
        raise DataValidationError("epc_uri must be a non-empty string")
    m = _SGTIN_RE.search(epc_uri.strip())
    if m:
        prefix, item_ref = m.group(1), m.group(2)
        indicator = item_ref[0]
        body = (indicator + prefix + item_ref[1:]).zfill(13)[:13]
        chk = gtin_check_digit(body)
        return body + str(chk)
    digits = "".join(c for c in epc_uri if c.isdigit())
    if len(digits) >= 12:
        return normalize_gtin(digits[:14])
    raise DataValidationError(f"Cannot extract GTIN from EPC URI: {epc_uri}")


def epcis_lot(event: dict) -> str | None:
    """Extract lot/batch number from an EPCIS event."""
    if not isinstance(event, dict):
        return None
    if event.get("lot"):
        return str(event["lot"]).strip()
    ilmd = event.get("ilmd", {})
    if isinstance(ilmd, dict) and ilmd.get("lotNumber"):
        return str(ilmd["lotNumber"]).strip()
    return None


def epcis_location(event: dict) -> str:
    """Extract readPoint or bizLocation from an EPCIS event."""
    if not isinstance(event, dict):
        raise TypeError("event must be a dict")
    return str(event.get("readPoint") or event.get("bizLocation") or "UNKNOWN_LOC").strip()


def parse_epcis_event(raw: dict) -> dict:
    """Validate and normalize an EPCIS ObjectEvent dictionary."""
    if not isinstance(raw, dict):
        raise DataValidationError("EPCIS event must be a dict")
    epc_list = raw.get("epcList", [])
    gtin = str(raw.get("gtin") or "")
    if not gtin and epc_list:
        gtin = epc_to_gtin(str(epc_list[0]))
    if not gtin:
        raise DataValidationError("EPCIS event requires gtin or epcList")
    return {
        "type": str(raw.get("type", "ObjectEvent")),
        "gtin": normalize_gtin(gtin),
        "lot": epcis_lot(raw),
        "location": epcis_location(raw),
        "eventTime": str(raw.get("eventTime", "2026-12-30T00:00:00Z")),
        "bizStep": str(raw.get("bizStep", "shipping")),
    }


def epcis_object_event(gtin: str, lot: str | None, location: str, event_time: str) -> dict:
    """Construct a normalized EPCIS ObjectEvent dictionary."""
    return parse_epcis_event({"gtin": gtin, "lot": lot, "readPoint": location, "eventTime": event_time})


def epcis_to_movements(events: list[dict]) -> list[dict]:
    """Convert EPCIS events into sorted movement records."""
    parsed = [parse_epcis_event(e) for e in events]
    return sorted(parsed, key=lambda e: e["eventTime"])


def filter_epcis_by_gtin(events: list[dict], gtin: str) -> list[dict]:
    """Filter EPCIS events matching a normalized GTIN-14."""
    target = normalize_gtin(gtin)
    return [e for e in epcis_to_movements(events) if e["gtin"] == target]


def epcis_summary(events: list[dict]) -> dict:
    """Summarize EPCIS event counts, unique GTINs, and locations."""
    movs = epcis_to_movements(events)
    return {
        "event_count": len(movs),
        "gtins": sorted({m["gtin"] for m in movs}),
        "locations": sorted({m["location"] for m in movs}),
    }
