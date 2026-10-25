"""Parse CPSC consumer product recalls and food-contact items."""
from __future__ import annotations

from recallstorm.core.errors import DataValidationError


def cpsc_product_names(item: dict) -> list[str]:
    """Extract product names from a CPSC recall record."""
    prods = item.get("Products") or []
    out = [str(p.get("Name", "")).strip() for p in prods if isinstance(p, dict) and p.get("Name")]
    if not out and item.get("Title"):
        out.append(str(item["Title"]).strip())
    return out


def cpsc_upcs(item: dict) -> list[str]:
    """Extract 14-digit normalized UPCs from a CPSC recall record."""
    upcs = item.get("UPCs") or []
    out: list[str] = []
    for u in upcs:
        raw = str(u.get("UPC") if isinstance(u, dict) else u).strip()
        digits = "".join(c for c in raw if c.isdigit())
        if digits:
            out.append(digits[:14].zfill(14))
    return out


def cpsc_hazard_text(item: dict) -> str:
    """Extract hazard descriptions from a CPSC recall record."""
    hazards = item.get("Hazards") or []
    texts = [str(h.get("Name", "") if isinstance(h, dict) else h).strip() for h in hazards]
    return "; ".join(t for t in texts if t) or str(item.get("Description", "")).strip()


def cpsc_remedy(item: dict) -> str:
    """Extract consumer remedy instructions from a CPSC recall record."""
    remedies = item.get("Remedies") or []
    texts = [str(r.get("Name", "") if isinstance(r, dict) else r).strip() for r in remedies]
    return "; ".join(t for t in texts if t) or "Refund or replacement"


def cpsc_dates(item: dict) -> tuple[str | None, str | None]:
    """Return (recall_date, last_publish_date) from a CPSC record."""
    d1 = str(item["RecallDate"]).strip() if item.get("RecallDate") else None
    d2 = str(item["LastPublishDate"]).strip() if item.get("LastPublishDate") else None
    return (d1, d2)


def cpsc_units(item: dict) -> int:
    """Extract approximate number of affected units from a CPSC record."""
    prods = item.get("Products") or []
    for p in prods:
        if isinstance(p, dict) and p.get("NumberOfUnits"):
            digits = "".join(c for c in str(p["NumberOfUnits"]) if c.isdigit())
            if digits:
                return int(digits)
    return int(item.get("units", 0))


def cpsc_is_food_contact(item: dict) -> bool:
    """Return True if the CPSC recall involves cookware, bottles, or food-contact ware."""
    blob = " ".join(cpsc_product_names(item) + [cpsc_hazard_text(item)]).lower()
    return any(k in blob for k in ("cookware", "pan", "pot", "bottle", "mug", "cup", "plate", "bowl", "food", "pfas", "lead"))


def parse_cpsc_recall(item: dict) -> dict:
    """Parse a raw CPSC recall JSON object."""
    if not isinstance(item, dict) or not item.get("RecallNumber"):
        raise DataValidationError("CPSC recall requires RecallNumber")
    d1, d2 = cpsc_dates(item)
    return {
        "recall_number": str(item["RecallNumber"]).strip(),
        "products": cpsc_product_names(item),
        "upcs": cpsc_upcs(item),
        "hazard": cpsc_hazard_text(item),
        "remedy": cpsc_remedy(item),
        "recall_date": d1 or "2026-01-01",
        "last_publish_date": d2,
        "units": cpsc_units(item),
        "is_food_contact": cpsc_is_food_contact(item),
    }


def cpsc_to_recall(item: dict) -> dict:
    """Convert a CPSC recall object into a standard Recall Storm recall dictionary."""
    p = parse_cpsc_recall(item)
    return {
        "recall_id": f"CPSC-{p['recall_number']}",
        "source": "CPSC",
        "title": ", ".join(p["products"]) or p["recall_number"],
        "gtins": p["upcs"],
        "date": p["recall_date"],
        "states": ["US"],
        "reason": p["hazard"],
        "is_food_contact": p["is_food_contact"],
    }
