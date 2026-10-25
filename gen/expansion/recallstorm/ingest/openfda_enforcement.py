"""openFDA food/drug enforcement report parser for lot codes, GTINs, and jurisdictions."""
from __future__ import annotations

import re
from typing import Iterator
from recallstorm.core.errors import DataValidationError

_LOT_TOKEN_RE = re.compile(r"\b(?:LOT|BATCH|CODE)[#:\s\-]*([A-Z0-9\-]{3,20})\b", re.IGNORECASE)
_RANGE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\s+(?:to|through|-)\s+(\d{4}-\d{2}-\d{2})\b", re.IGNORECASE)
_UPC_RE = re.compile(r"\b(\d{12,14})\b")
_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY",
}


def extract_lot_codes(code_info: str) -> list[str]:
    """Extract lot or batch codes from openFDA code_info text."""
    if not isinstance(code_info, str) or not code_info.strip():
        return []
    matches = [m.upper() for m in _LOT_TOKEN_RE.findall(code_info)]
    if not matches:
        for tok in re.split(r"[,;\s]+", code_info.strip()):
            t = tok.strip().upper()
            if len(t) >= 4 and any(c.isdigit() for c in t) and any(c.isalpha() for c in t):
                matches.append(t)
    seen: list[str] = []
    for m in matches:
        if m not in seen:
            seen.append(m)
    return seen


def extract_date_ranges(code_info: str) -> list[tuple[str, str]]:
    """Extract (start_date, end_date) ISO date ranges from code_info text."""
    if not isinstance(code_info, str):
        return []
    return [(a, b) for a, b in _RANGE_RE.findall(code_info)]


def extract_product_gtins(desc: str) -> list[str]:
    """Extract 12-to-14 digit UPC/GTINs from product_description and normalize to 14 digits."""
    if not isinstance(desc, str):
        return []
    out: list[str] = []
    for m in _UPC_RE.findall(desc):
        g = m.zfill(14)[:14]
        if g not in out:
            out.append(g)
    return out


def classify_recall_reason(reason: str) -> str:
    """Classify recall_for_initiation into a high-level category."""
    if not isinstance(reason, str):
        return "OTHER"
    r = reason.lower()
    if "red" in r or "erythrosine" in r or "e127" in r or "bvo" in r or "bromate" in r or "paraben" in r:
        return "PROHIBITED_ADDITIVE"
    if "allergen" in r or "undeclared" in r or "milk" in r or "peanut" in r:
        return "UNDECLARED_ALLERGEN"
    if "salmonella" in r or "listeria" in r or "coli" in r:
        return "PATHOGEN"
    return "OTHER"


def recall_jurisdictions(dist_pattern: str) -> list[str]:
    """Extract applicable US state codes or ['US'] from distribution_pattern."""
    if not isinstance(dist_pattern, str) or not dist_pattern.strip():
        return ["US"]
    if "nationwide" in dist_pattern.lower() or "united states" in dist_pattern.lower():
        return ["US"]
    found: list[str] = []
    for tok in re.findall(r"\b[A-Z]{2}\b", dist_pattern.upper()):
        if tok in _STATE_CODES and tok not in found:
            found.append(tok)
    return found or ["US"]


def recall_status(raw: dict) -> str:
    """Return normalized recall status (ONGOING, TERMINATED, COMPLETED)."""
    st = str(raw.get("status", "Ongoing")).strip().upper()
    return st if st in {"ONGOING", "TERMINATED", "COMPLETED"} else "ONGOING"


def parse_enforcement_report(raw: dict) -> dict:
    """Validate and parse an openFDA enforcement report dictionary."""
    if not isinstance(raw, dict) or not raw.get("recall_number"):
        raise DataValidationError("openFDA report requires recall_number")
    code_info = str(raw.get("code_info", ""))
    desc = str(raw.get("product_description", ""))
    reason = str(raw.get("reason_for_recall", ""))
    dist = str(raw.get("distribution_pattern", "Nationwide"))
    return {
        "recall_id": str(raw["recall_number"]).strip(),
        "status": recall_status(raw),
        "classification": str(raw.get("classification", "Class II")).strip(),
        "product_description": desc,
        "gtins": extract_product_gtins(desc),
        "lot_codes": extract_lot_codes(code_info),
        "date_ranges": extract_date_ranges(code_info),
        "reason": reason,
        "reason_category": classify_recall_reason(reason),
        "jurisdictions": recall_jurisdictions(dist),
        "report_date": str(raw.get("report_date", "20261201")).strip(),
    }


def enforcement_to_recall(raw: dict) -> dict:
    """Convert an openFDA enforcement report into a standard recall dict."""
    parsed = parse_enforcement_report(raw)
    return {
        "recall_id": parsed["recall_id"],
        "source": "OPENFDA",
        "title": parsed["product_description"][:80],
        "date": parsed["report_date"],
        "states": parsed["jurisdictions"],
        "reason": parsed["reason"],
        "gtins": parsed["gtins"],
        "lot_codes": parsed["lot_codes"],
        "date_ranges": parsed["date_ranges"],
    }


def iter_enforcement_pages(pages: list[dict]) -> Iterator[dict]:
    """Yield parsed enforcement reports across multiple openFDA API pages."""
    for page in pages:
        results = page.get("results", []) if isinstance(page, dict) else []
        for r in results:
            yield enforcement_to_recall(r)
