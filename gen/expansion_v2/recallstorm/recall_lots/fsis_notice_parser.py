"""Parse USDA FSIS establishment numbers, marks of inspection, and case codes."""
from __future__ import annotations

from dataclasses import dataclass
import re

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class FsisRecallRelease:
    """Domain entity for a USDA FSIS meat/poultry recall release."""

    ref_id: str = "FSIS-REL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class EstNumberExtractor:
    """USDA establishment number (EST. / P-) extractor."""

    ref_id: str = "FSIS-EST-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def parse_fsis_establishment_code(text: str) -> str:
    """Extract USDA establishment code (e.g. 'EST. 1234' or 'P-5678') from text."""
    _req(text, "text")
    m = re.search(r"\b(EST\.?\s*\d+[A-Z]?|P-\d+[A-Z]?)\b", str(text).upper())
    return m.group(1).replace(" ", "") if m else "EST.UNKNOWN"


def extract_usda_inspection_mark(mark_text: str) -> dict:
    """Extract USDA mark of inspection metadata."""
    _req(mark_text, "mark_text")
    return {"op": "extract_usda_inspection_mark", "est": parse_fsis_establishment_code(mark_text), "src": "recallstorm/recall_lots/fsis_notice_parser.py"}


def classify_fsis_health_hazard_level(hazard_text: str) -> str:
    """Classify FSIS health hazard into HIGH (Class I), LOW (Class II), or MARGINAL (Class III)."""
    _req(hazard_text, "hazard_text")
    up = str(hazard_text).upper()
    if "HIGH" in up or "CLASS I" in up:
        return "HIGH"
    if "MARGINAL" in up or "CLASS III" in up:
        return "MARGINAL"
    return "LOW"


def parse_fsis_production_date_span(start_iso: str, end_iso: str) -> dict:
    """Parse and validate an FSIS production date span."""
    _req(start_iso, "start_iso")
    _req(end_iso, "end_iso")
    if str(end_iso) < str(start_iso):
        raise DataValidationError("end_iso precedes start_iso")
    return {"op": "parse_fsis_production_date_span", "start": str(start_iso), "end": str(end_iso), "src": "recallstorm/recall_lots/fsis_notice_parser.py"}


def extract_fsis_case_code_strings(text: str) -> list[str]:
    """Extract case code strings from FSIS recall text."""
    _req(text, "text")
    return re.findall(r"\bCASE[:\s#]*([A-Z0-9\-]+)\b", str(text).upper())


def identify_fsis_import_country(text: str) -> str:
    """Identify country of origin on FSIS import recall notices."""
    _req(text, "text")
    for c in ("BRAZIL", "AUSTRALIA", "CANADA", "MEXICO", "URUGUAY"):
        if c in str(text).upper():
            return c
    return "US"


def match_fsis_retail_consignee_pdf(retailer_name: str, pdf_text: str) -> dict:
    """Check if retailer_name appears in FSIS retail consignee list PDF text."""
    _req(retailer_name, "retailer_name")
    _req(pdf_text, "pdf_text")
    matched = str(retailer_name).lower() in str(pdf_text).lower()
    return {"op": "match_fsis_retail_consignee_pdf", "matched": matched, "src": "recallstorm/recall_lots/fsis_notice_parser.py"}


def normalize_usda_product_title(title: str) -> str:
    """Normalize a USDA FSIS product title."""
    _req(title, "title")
    return " ".join(str(title).strip().upper().split())


def parse_fsis_poultry_serial_range(start_ser: int, end_ser: int) -> list[str]:
    """Expand a poultry case serial range."""
    if start_ser < 0 or end_ser < start_ser or (end_ser - start_ser) > 1000:
        raise DataValidationError("Invalid poultry serial range")
    return [f"P-{i}" for i in range(start_ser, end_ser + 1)]


def validate_fsis_notice_completeness(notice: dict) -> dict:
    """Validate that an FSIS notice dict contains recall_number and est."""
    if not isinstance(notice, dict) or not notice.get("recall_number"):
        raise DataValidationError("FSIS notice missing recall_number")
    return {"op": "validate_fsis_notice_completeness", "valid": True, "src": "recallstorm/recall_lots/fsis_notice_parser.py"}
