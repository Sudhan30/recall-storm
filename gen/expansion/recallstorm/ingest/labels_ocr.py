"""OCR label parsing, ingredient block detection, and confidence checks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class OcrLabel:
    """Parsed OCR label result for a product package."""

    sku_id: str
    blocks: tuple[str, ...]
    confidence: float
    language: str = "en"


def parse_ocr_payload(payload: dict) -> OcrLabel:
    """Parse a raw OCR dictionary payload into an OcrLabel."""
    if not isinstance(payload, dict) or not payload.get("sku_id"):
        raise DataValidationError("OCR payload requires sku_id")
    blocks_raw = payload.get("blocks", [])
    if isinstance(blocks_raw, str):
        blocks = (blocks_raw,)
    elif isinstance(blocks_raw, list):
        blocks = tuple(str(b) for b in blocks_raw)
    else:
        raise DataValidationError("OCR blocks must be list or str")
    conf = float(payload.get("confidence", 0.9))
    if not (0.0 <= conf <= 1.0):
        raise DataValidationError("OCR confidence must be in [0.0, 1.0]")
    lang = str(payload.get("language", "en")).strip() or "en"
    return OcrLabel(sku_id=str(payload["sku_id"]).strip(), blocks=blocks, confidence=conf, language=lang)


def ocr_text_blocks(label: OcrLabel) -> list[str]:
    """Return the list of non-empty text blocks from an OcrLabel."""
    if not isinstance(label, OcrLabel):
        raise TypeError("label must be an OcrLabel")
    return [b.strip() for b in label.blocks if b.strip()]


def ocr_confidence(label: OcrLabel) -> float:
    """Return the OCR confidence score."""
    if not isinstance(label, OcrLabel):
        raise TypeError("label must be an OcrLabel")
    return label.confidence


def join_ocr_lines(blocks: list[str] | tuple[str, ...]) -> str:
    """Join OCR lines, repairing hyphenated line breaks."""
    cleaned: list[str] = []
    for b in blocks:
        s = b.strip()
        if not s:
            continue
        if cleaned and cleaned[-1].endswith("-"):
            cleaned[-1] = cleaned[-1][:-1] + s
        else:
            cleaned.append(s)
    return " ".join(cleaned)


def detect_ingredient_block(text: str) -> str:
    """Extract the ingredient statement from joined OCR text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    m = re.search(r"(?:ingredients|ingredientes|ingrédients)\s*[:\-]?\s*(.+)", text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def ocr_to_ingredients(label: OcrLabel) -> str:
    """Extract the full ingredient string from an OcrLabel."""
    joined = join_ocr_lines(ocr_text_blocks(label))
    return detect_ingredient_block(joined)


def flag_low_confidence(label: OcrLabel, threshold: float = 0.75) -> bool:
    """Return True if label confidence is below threshold or text is empty."""
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("threshold must be between 0 and 1")
    return label.confidence < threshold or not ocr_to_ingredients(label)


def ocr_language(label: OcrLabel) -> str:
    """Detect or return the primary language of the OCR label."""
    text = join_ocr_lines(label.blocks).lower()
    if "ingredientes" in text:
        return "es"
    if "ingrédients" in text or "colorant" in text:
        return "fr"
    return label.language
