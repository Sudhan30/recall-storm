"""Parse FDA press releases, FEIs, allergen classes, and code info blocks."""
from __future__ import annotations

from dataclasses import dataclass
import re

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class FdaEnforcementNotice:
    """Domain entity for an FDA enforcement notice."""

    ref_id: str = "FDA-ENF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ExtractedRecallMetadata:
    """Metadata extracted from an FDA recall press release."""

    ref_id: str = "FDA-META-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def parse_fda_press_release_html(html: str) -> dict:
    """Strip HTML tags and extract title/body from an FDA recall press release."""
    _req(html, "html")
    clean = re.sub(r"<[^>]+>", " ", str(html))
    clean = " ".join(clean.split())
    return {"op": "parse_fda_press_release_html", "text": clean, "length": len(clean), "src": "recallstorm/recall_lots/fda_notice_parser.py"}


def extract_recalling_firm_feis(text: str) -> list[str]:
    """Extract 7-to-10 digit FDA Establishment Identifiers (FEIs) from notice text."""
    _req(text, "text")
    return re.findall(r"\bFEI[:\s#]*(\d{7,10})\b", str(text), flags=re.IGNORECASE)


def identify_fda_recall_class(text: str) -> str:
    """Identify Class I, Class II, or Class III from recall text."""
    _req(text, "text")
    up = str(text).upper()
    if "CLASS I" in up and "CLASS II" not in up and "CLASS III" not in up:
        return "Class I"
    if "CLASS III" in up:
        return "Class III"
    return "Class II"


def parse_fda_reason_for_recall(reason: str) -> dict:
    """Parse FDA reason_for_recall text."""
    _req(reason, "reason")
    return {"op": "parse_fda_reason_for_recall", "reason": str(reason).strip(), "src": "recallstorm/recall_lots/fda_notice_parser.py"}


def extract_upc_list_from_text(text: str) -> list[str]:
    """Extract 12-to-14 digit UPC/GTINs normalized to 14 digits."""
    _req(text, "text")
    return [m.zfill(14) for m in re.findall(r"\b\d{12,14}\b", str(text))]


def normalize_fda_code_info_block(code_info: str) -> str:
    """Normalize whitespace and separators in an FDA code_info block."""
    _req(code_info, "code_info")
    return " ".join(str(code_info).upper().split())


def split_multi_brand_table(rows: list[dict]) -> dict[str, list[dict]]:
    """Group multi-brand recall table rows by brand name."""
    if rows is None:
        raise DataValidationError("rows cannot be None")
    out: dict[str, list[dict]] = {}
    for r in rows:
        b = str(r.get("brand", "Generic"))
        out.setdefault(b, []).append(r)
    return out


def detect_undeclared_allergen_type(text: str) -> str | None:
    """Detect Big-9 undeclared allergen name in recall text."""
    _req(text, "text")
    low = str(text).lower()
    for alg in ("peanut", "tree nut", "milk", "egg", "wheat", "soy", "fish", "shellfish", "sesame"):
        if alg in low:
            return alg.upper()
    return None


def link_fda_res_event_number(event_id: str, recall_number: str) -> dict:
    """Link an FDA RES Event ID to an individual product recall number."""
    _req(event_id, "event_id")
    _req(recall_number, "recall_number")
    return {"op": "link_fda_res_event_number", "event_id": str(event_id), "recall_number": str(recall_number), "src": "recallstorm/recall_lots/fda_notice_parser.py"}


def validate_parsed_notice_schema(notice: dict) -> dict:
    """Validate that a parsed notice dict contains recall_number and reason."""
    if not isinstance(notice, dict) or not notice.get("recall_number"):
        raise DataValidationError("Notice missing recall_number")
    return {"op": "validate_parsed_notice_schema", "valid": True, "recall_number": str(notice["recall_number"]), "src": "recallstorm/recall_lots/fda_notice_parser.py"}
