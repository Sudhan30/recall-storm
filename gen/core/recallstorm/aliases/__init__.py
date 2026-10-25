"""Alias normalization and ingredient matching for Recall Storm."""
from __future__ import annotations

from recallstorm.aliases.detector import (
    AliasMatch,
    find_additive_match,
    is_unclear_or_generic_color,
    normalize_text,
)

__all__ = [
    "AliasMatch",
    "find_additive_match",
    "is_unclear_or_generic_color",
    "normalize_text",
]
