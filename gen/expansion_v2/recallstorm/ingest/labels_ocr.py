"""Parse OCR label payloads and extract ingredient blocks."""
from __future__ import annotations

from dataclasses import dataclass
import re

from recallstorm.core.errors import DataValidationError

_ING_HEADER_RE = re.compile(r"\b(?:ingredients?|contains|ingredientes)\s*[:\-]?\s*", re.IGNORECASE)


@dataclass(frozen=True)
class OcrLabel:
    """Parsed OCR label representation."""

    sku_id: str
    text: str
    ingredients: str
    confidence: float
    language: str


def ocr_text_blocks(payload: dict) -> list[str]:
    """Extract text block strings from an OCR payload dictionary."""
    if not isinstance(payload, dict):
        raise DataValidationError("OCR payload must be a dict")
    blocks = payload.get("blocks") or payload.get("lines") or []
    if isinstance(blocks, str):
        return [blocks.strip()] if blocks.strip() else []
    out: list[str] = []
    for b in blocks:
        if isinstance(b, dict):
            txt = str(b.get("text", "")).strip()
        else:
            txt = str(b).strip()
        if txt:
            out.append(txt)
    if not out and payload.get("text"):
        out.append(str(payload["text"]).strip())
    return out


def join_ocr_lines(lines: list[str]) -> str:
    """Join OCR lines resolving hyphenated line wraps."""
    cleaned: list[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if cleaned and cleaned[-1].endswith("-"):
            cleaned[-1] = cleaned[-1][:-1] + s
        else:
            cleaned.append(s)
    return " ".join(cleaned)


def ocr_confidence(payload: dict) -> float:
    """Compute average OCR confidence in [0.0, 1.0]."""
    if not isinstance(payload, dict):
        raise DataValidationError("OCR payload must be a dict")
    if "confidence" in payload:
        return max(0.0, min(1.0, float(payload["confidence"])))
    blocks = payload.get("blocks", [])
    confs = [float(b["confidence"]) for b in blocks if isinstance(b, dict) and "confidence" in b]
    if not confs:
        return 1.0
    return max(0.0, min(1.0, sum(confs) / len(confs)))


def detect_ingredient_block(text: str) -> str:
    """Extract the ingredient statement from full package OCR text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    m = _ING_HEADER_RE.search(text)
    if m:
        return text[m.end() :].strip()
    return text.strip()


def ocr_to_ingredients(payload: dict) -> str:
    """Convert an OCR payload directly to an extracted ingredient string."""
    full_text = join_ocr_lines(ocr_text_blocks(payload))
    return detect_ingredient_block(full_text)


def flag_low_confidence(payload: dict, threshold: float = 0.75) -> bool:
    """Return True if the OCR confidence is strictly below threshold."""
    return ocr_confidence(payload) < threshold


def ocr_language(payload: dict) -> str:
    """Detect or extract the ISO language code for the OCR payload."""
    if isinstance(payload, dict) and payload.get("lang"):
        return str(payload["lang"]).lower().strip()
    txt = join_ocr_lines(ocr_text_blocks(payload)).lower()
    if "ingredientes" in txt or "azucar" in txt or "rojo" in txt:
        return "es"
    return "en"


def parse_ocr_payload(payload: dict) -> OcrLabel:
    """Parse an OCR dictionary into an OcrLabel dataclass."""
    if not isinstance(payload, dict) or not payload.get("sku_id"):
        raise DataValidationError("OCR payload requires sku_id")
    blocks = ocr_text_blocks(payload)
    full_text = join_ocr_lines(blocks)
    return OcrLabel(
        sku_id=str(payload["sku_id"]),
        text=full_text,
        ingredients=detect_ingredient_block(full_text),
        confidence=ocr_confidence(payload),
        language=ocr_language(payload),
    )
