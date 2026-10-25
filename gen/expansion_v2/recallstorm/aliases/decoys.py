"""Identify decoy mentions like Red 40, D&C Red 33, Red Pepper, or 3 Peppers."""
from __future__ import annotations

import re

DECOY_PATTERNS: tuple[str, ...] = (
    r"RED\s*(?:NO\.?\s*|#)?40\b",
    r"RED\s*40\s*LAKE\b",
    r"D\s*&\s*C\s*RED\s*(?:NO\.?\s*|#)?(?:30|33|27|28|6|7)\b",
    r"\b3\s+PEPPERS?\b",
    r"\bRED\s+(?:BELL\s+)?PEPPERS?\b",
    r"\bRED\s+(?:BEANS?|LENTILS?|RASPBERR(?:Y|IES)|CHERR(?:Y|IES)|GRAPES?|APPLES?|CABBAGE|ONIONS?|POTATO(?:ES)?|WINE|VINEGAR|YEAST|ALGAE|BEET|RADISH)\b",
    r"\bCOLORED\s+RED\s+WITH\s+(?:CARMINE|BEET|LYCOPENE|PAPRIKA|ANNATTO)\b",
)

_RED40_RE = re.compile(r"\b(?:FD&C\s+)?RED\s*(?:DYE\s*)?(?:NO\.?\s*|#)?40(?:\s+LAKE)?\b", re.IGNORECASE)
_DC_RED_RE = re.compile(r"\b(?:EXT\.?\s*)?D\s*&\s*C\s+RED\s*(?:NO\.?\s*|#)?\d+\b", re.IGNORECASE)
_QTY_RE = re.compile(r"\b3\s+(?:PEPPER|CHEESE|BEAN|BERRY|GRAIN|CITRUS|MEAT|SEED)S?\b", re.IGNORECASE)
_PROD_PHRASE_RE = re.compile(
    r"\bRED\s+(?:PEPPER|BELL|CHILI|BEAN|WINE|VINEGAR|CABBAGE|ONION|BEET|RADISH|RASPBERRY|APPLE|GRAPE|CHERRY|YEAST)\b",
    re.IGNORECASE,
)
_LAKE_RE = re.compile(r"\bRED\s*(?:NO\.?\s*|#)?(?:40|30|33|27|28|7|6)\s+LAKE\b", re.IGNORECASE)


def is_red40(text: str, pos: int = 0) -> bool:
    """Return True if text (from pos) contains a Red 40 mention."""
    if not isinstance(text, str):
        return False
    return bool(_RED40_RE.search(text[max(0, pos) :]))


def is_dc_red_33(text: str, pos: int = 0) -> bool:
    """Return True if text (from pos) contains a D&C Red (e.g., D&C Red 33 or 30) mention."""
    if not isinstance(text, str):
        return False
    return bool(_DC_RED_RE.search(text[max(0, pos) :]))


def is_quantity_phrase(text: str, pos: int = 0) -> bool:
    """Return True if text contains a numeric quantity phrase like '3 Pepper'."""
    if not isinstance(text, str):
        return False
    return bool(_QTY_RE.search(text[max(0, pos) :]))


def is_product_name_phrase(text: str, pos: int = 0) -> bool:
    """Return True if text contains a culinary red ingredient like 'Red Pepper' or 'Red Beet'."""
    if not isinstance(text, str):
        return False
    return bool(_PROD_PHRASE_RE.search(text[max(0, pos) :]))


def is_lake_pigment(text: str, pos: int = 0) -> bool:
    """Return True if text contains a non-Red-3 aluminum lake pigment like 'Red 40 Lake'."""
    if not isinstance(text, str):
        return False
    return bool(_LAKE_RE.search(text[max(0, pos) :]))


def decoy_examples() -> list[str]:
    """Return canonical decoy examples that must NOT trigger a RED3 PULL."""
    return [
        "FD&C RED #40",
        "RED 40 LAKE",
        "D&C RED #33",
        "3 PEPPER JALAPENO",
        "RED PEPPER",
        "COLORED RED WITH CARMINE",
    ]


def classify_red_mention(snippet: str) -> str:
    """Classify a 'Red' mention snippet as RED3, RED40, DC_RED, NATURAL_FOOD, or OTHER."""
    if not isinstance(snippet, str):
        return "OTHER"
    if is_dc_red_33(snippet):
        return "DC_RED"
    if re.search(r"\b(?:FD&C\s+)?RED\s*(?:DYE\s*)?(?:NO\.?\s*|#)?3\b(?!\d)", snippet, re.IGNORECASE):
        return "RED3"
    if is_red40(snippet):
        return "RED40"
    if is_product_name_phrase(snippet) or is_quantity_phrase(snippet):
        return "NATURAL_FOOD"
    return "OTHER"


def near_miss_report(text: str) -> dict:
    """Return a report of decoy near-misses found in text."""
    return {
        "red40": is_red40(text),
        "dc_red": is_dc_red_33(text),
        "quantity_phrase": is_quantity_phrase(text),
        "product_phrase": is_product_name_phrase(text),
        "lake_pigment": is_lake_pigment(text),
    }
