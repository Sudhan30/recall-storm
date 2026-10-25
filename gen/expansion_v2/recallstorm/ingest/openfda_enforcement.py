"""Parse openFDA enforcement reports, lot codes, and GTINs."""
from __future__ import annotations

import re

from recallstorm.core.errors import DataValidationError

_LOT_RE = re.compile(r"\b(?:LOT|BATCH|CODE)[S#:\-\s]+([A-Z0-9\-]{3,20})", re.IGNORECASE)
_DATE_RANGE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*(?:to|through|-)\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
_GTIN_RE = re.compile(r"\b(\d{12,14})\b")


def extract_lot_codes(code_info: str) -> list[str]:
    """Extract alphanumeric lot codes from openFDA code_info text."""
    if not isinstance(code_info, str) or not code_info.strip():
        return []
    matches = [m.group(1).upper().strip("-") for m in _LOT_RE.finditer(code_info)]
    if not matches:
        tokens = [t.strip(",.;:") for t in code_info.split()]
        matches = [t.upper() for t in tokens if any(c.isdigit() for c in t) and len(t) >= 4]
    seen: list[str] = []
    for m in matches:
        if m not in seen:
            seen.append(m)
    return seen


def extract_date_ranges(code_info: str) -> list[tuple[str, str]]:
    """Extract (start_iso, end_iso) date ranges from openFDA code_info text."""
    if not isinstance(code_info, str):
        return []
    return [(m.group(1), m.group(2)) for m in _DATE_RANGE_RE.finditer(code_info)]


def extract_product_gtins(text: str) -> list[str]:
    """Extract 12-to-14 digit UPC/GTIN strings normalized to 14 digits."""
    if not isinstance(text, str):
        return []
    out: list[str] = []
    for m in _GTIN_RE.finditer(text):
        g = m.group(1).zfill(14)
        if g not in out:
            out.append(g)
    return out


def classify_recall_reason(reason: str) -> str:
    """Classify recall reason text into ALLERGEN, MICROBIAL, ADDITIVE, FOREIGN_MATERIAL, or OTHER."""
    r = (reason or "").lower()
    if any(k in r for k in ("undeclared", "allergen", "peanut", "milk", "soy", "wheat", "egg")):
        return "ALLERGEN"
    if any(k in r for k in ("listeria", "salmonella", "e. coli", "botulinum")):
        return "MICROBIAL"
    if any(k in r for k in ("red 3", "red no. 3", "erythrosine", "bromate", "bvo", "dye", "additive")):
        return "ADDITIVE"
    if any(k in r for k in ("metal", "plastic", "glass", "foreign")):
        return "FOREIGN_MATERIAL"
    return "OTHER"


def recall_jurisdictions(dist_pattern: str) -> list[str]:
    """Extract two-letter US state codes or ['US'] from openFDA distribution_pattern."""
    if not isinstance(dist_pattern, str) or not dist_pattern.strip():
        return ["US"]
    if "nationwide" in dist_pattern.lower() or "united states" in dist_pattern.lower():
        return ["US"]
    codes = re.findall(r"\b([A-Z]{2})\b", dist_pattern.upper())
    return codes if codes else ["US"]


def recall_status(rep: dict) -> str:
    """Normalize openFDA enforcement report status."""
    return str(rep.get("status", "Ongoing")).strip()


def parse_enforcement_report(rep: dict) -> dict:
    """Parse a raw openFDA food/drug enforcement report dictionary."""
    if not isinstance(rep, dict) or not rep.get("recall_number"):
        raise DataValidationError("openFDA report requires recall_number")
    code_info = str(rep.get("code_info", ""))
    desc = str(rep.get("product_description", ""))
    reason = str(rep.get("reason_for_recall", ""))
    return {
        "recall_number": str(rep["recall_number"]).strip(),
        "classification": str(rep.get("classification", "Class II")).strip(),
        "status": recall_status(rep),
        "product_description": desc,
        "reason_class": classify_recall_reason(reason),
        "lots": extract_lot_codes(code_info),
        "date_ranges": extract_date_ranges(code_info),
        "gtins": extract_product_gtins(f"{desc} {code_info}"),
        "jurisdictions": recall_jurisdictions(str(rep.get("distribution_pattern", "Nationwide"))),
    }


def enforcement_to_recall(rep: dict) -> dict:
    """Convert an openFDA report to a standard Recall Storm recall dictionary."""
    parsed = parse_enforcement_report(rep)
    return {
        "recall_id": parsed["recall_number"],
        "source": "OPENFDA",
        "title": parsed["product_description"],
        "lots": parsed["lots"],
        "gtins": parsed["gtins"],
        "states": parsed["jurisdictions"],
        "reason": parsed["reason_class"],
    }


def iter_enforcement_pages(pages: list[dict]) -> list[dict]:
    """Iterate across openFDA API pages with 'results' arrays."""
    out: list[dict] = []
    for p in pages:
        for r in p.get("results", []):
            out.append(enforcement_to_recall(r))
    return out
