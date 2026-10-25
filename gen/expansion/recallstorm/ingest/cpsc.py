"""CPSC consumer product recall parser."""
from __future__ import annotations

import re
from recallstorm.core.errors import DataValidationError


def cpsc_product_names(raw: dict) -> list[str]:
    """Extract product names from a CPSC recall record."""
    prods = raw.get("Products", [])
    if isinstance(prods, list):
        return [str(p.get("Name", "")).strip() for p in prods if isinstance(p, dict) and p.get("Name")]
    if raw.get("title"):
        return [str(raw["title"]).strip()]
    return []


def cpsc_upcs(raw: dict) -> list[str]:
    """Extract 12-to-14 digit UPCs from a CPSC recall record normalized to 14 digits."""
    upcs: list[str] = []
    for p in raw.get("Products", []):
        if isinstance(p, dict) and p.get("UPC"):
            for m in re.findall(r"\d{12,14}", str(p["UPC"])):
                upcs.append(m.zfill(14)[:14])
    for m in re.findall(r"\d{12,14}", str(raw.get("Description", ""))):
        g = m.zfill(14)[:14]
        if g not in upcs:
            upcs.append(g)
    return upcs


def cpsc_hazard_text(raw: dict) -> str:
    """Extract hazard description from a CPSC recall record."""
    hazards = raw.get("Hazards", [])
    if isinstance(hazards, list) and hazards:
        return "; ".join(str(h.get("Name", "")).strip() for h in hazards if isinstance(h, dict))
    return str(raw.get("hazard", "")).strip()


def cpsc_remedy(raw: dict) -> str:
    """Extract consumer remedy text from a CPSC recall record."""
    remedies = raw.get("Remedies", [])
    if isinstance(remedies, list) and remedies:
        return "; ".join(str(r.get("Name", "")).strip() for r in remedies if isinstance(r, dict))
    return str(raw.get("remedy", "Return for refund")).strip()


def cpsc_dates(raw: dict) -> tuple[str | None, str | None]:
    """Return (recall_date, last_publish_date) from a CPSC record."""
    r_date = str(raw["RecallDate"])[:10] if raw.get("RecallDate") else None
    p_date = str(raw["LastPublishDate"])[:10] if raw.get("LastPublishDate") else None
    return r_date, p_date


def cpsc_units(raw: dict) -> int:
    """Parse approximate affected unit count from CPSC record."""
    for p in raw.get("Products", []):
        if isinstance(p, dict) and p.get("NumberOfUnits"):
            digits = "".join(ch for ch in str(p["NumberOfUnits"]) if ch.isdigit())
            if digits:
                return int(digits)
    return int(raw.get("units", 0))


def cpsc_is_food_contact(raw: dict) -> bool:
    """Return True if the CPSC product is cookware, juvenile feeding, or food contact."""
    text = (" ".join(cpsc_product_names(raw)) + " " + str(raw.get("Description", ""))).lower()
    keywords = ("cookware", "pan", "skillet", "bottle", "cup", "food", "kitchen", "utensil")
    return any(k in text for k in keywords)


def parse_cpsc_recall(raw: dict) -> dict:
    """Validate and parse a CPSC recall JSON object."""
    if not isinstance(raw, dict) or not (raw.get("RecallNumber") or raw.get("recall_id")):
        raise DataValidationError("CPSC recall requires RecallNumber or recall_id")
    rid = str(raw.get("RecallNumber") or raw["recall_id"]).strip()
    r_date, p_date = cpsc_dates(raw)
    return {
        "recall_id": f"CPSC-{rid}" if not rid.startswith("CPSC-") else rid,
        "product_names": cpsc_product_names(raw),
        "upcs": cpsc_upcs(raw),
        "hazard": cpsc_hazard_text(raw),
        "remedy": cpsc_remedy(raw),
        "recall_date": r_date or "2026-01-01",
        "publish_date": p_date,
        "units": cpsc_units(raw),
        "is_food_contact": cpsc_is_food_contact(raw),
    }


def cpsc_to_recall(raw: dict) -> dict:
    """Convert a CPSC recall into a standard Recall Storm recall dictionary."""
    p = parse_cpsc_recall(raw)
    return {
        "recall_id": p["recall_id"],
        "source": "CPSC",
        "title": ", ".join(p["product_names"]) or p["recall_id"],
        "date": p["recall_date"],
        "states": ["US"],
        "reason": p["hazard"],
        "gtins": p["upcs"],
    }
