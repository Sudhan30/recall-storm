"""Parse multi-component kits and variety bundles."""
from __future__ import annotations

import re

from recallstorm.aliases.detect import MatchResult, find_first_match

_KIT_KEYWORDS: tuple[str, ...] = ("KIT CONTAINS:", "BUNDLE CONTAINS:", "VARIETY PACK:", "ASSORTMENT:")


def kit_keywords() -> tuple[str, ...]:
    """Return tuple of header keywords indicating a multi-item bundle or kit."""
    return _KIT_KEYWORDS


def is_bundle(text: str, category: str = "") -> bool:
    """Return True if text or category represents a multi-component kit or bundle."""
    if not isinstance(text, str):
        return False
    up = text.upper()
    if "|" in text or any(k in up for k in _KIT_KEYWORDS):
        return True
    cat_low = (category or "").lower()
    return "kit" in cat_low or "bundle" in cat_low or "variety" in cat_low


def split_bundle(text: str) -> list[tuple[str, str]]:
    """Split a bundle ingredient string into (component_name, component_ingredients) pairs."""
    if not isinstance(text, str) or not text.strip():
        return []
    cleaned = re.sub(r"^(?:KIT|BUNDLE)\s+CONTAINS\s*:\s*", "", text.strip(), flags=re.IGNORECASE)
    segments = [s.strip() for s in cleaned.split("|") if s.strip()]
    out: list[tuple[str, str]] = []
    for idx, seg in enumerate(segments):
        if ":" in seg:
            name, ings = seg.split(":", 1)
            out.append((name.strip(), ings.strip()))
        else:
            out.append((f"Component_{idx + 1}", seg))
    return out


def bundle_components(text: str) -> list[str]:
    """Return the list of component names in a bundle."""
    return [name for name, _ in split_bundle(text)]


def component_ingredients(text: str) -> dict[str, str]:
    """Return a dict mapping component_name -> component_ingredients."""
    return dict(split_bundle(text))


def bundle_match_path(
    text: str, aliases: tuple[str, ...], additive: str = "RED3"
) -> tuple[str, MatchResult] | None:
    """Find the first component containing additive and return (component_name, MatchResult_in_original_text)."""
    if not isinstance(text, str) or not text:
        return None
    overall_match = find_first_match(text, aliases, additive=additive)
    if overall_match is None:
        return None
    for comp_name, comp_ings in split_bundle(text):
        if find_first_match(comp_ings, aliases, additive=additive) is not None:
            return (comp_name, overall_match)
    return ("Bundle", overall_match)


def bundle_contains(text: str, aliases: tuple[str, ...], additive: str = "RED3") -> bool:
    """Return True if any component in the bundle contains the target additive."""
    return bundle_match_path(text, aliases, additive=additive) is not None


def bundle_summary(text: str) -> dict:
    """Return a summary of bundle components and whether it is a multi-item kit."""
    comps = split_bundle(text)
    return {"is_bundle": is_bundle(text), "component_count": len(comps), "components": [c[0] for c in comps]}


def flatten_bundle(text: str) -> str:
    """Flatten bundle component ingredients into a single comma-separated string."""
    return ", ".join(ings for _, ings in split_bundle(text))
