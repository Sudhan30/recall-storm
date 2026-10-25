"""Multi-component bundle, variety pack, and seasonal kit ingredient parsing."""
from __future__ import annotations

import re
from recallstorm.aliases.detect import MatchResult, find_first_match

_KIT_KEYWORDS: tuple[str, ...] = (
    "KIT CONTAINS:",
    "ASSORTMENT:",
    "VARIETY PACK:",
    "BUNDLE CONTAINS:",
)


def kit_keywords() -> tuple[str, ...]:
    """Return tuple of bundle/kit header keywords."""
    return _KIT_KEYWORDS


def is_bundle(text: str, category: str = "") -> bool:
    """Return True if the ingredient text or category represents a multi-component bundle/kit."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    up = text.upper()
    if "|" in text or any(k in up for k in _KIT_KEYWORDS):
        return True
    if "kit" in category.lower() or "bundle" in category.lower() or "assortment" in category.lower():
        return True
    return len(re.findall(r"\b[A-Z][A-Z\s]{2,20}:\s+[A-Z]", text)) >= 2


def split_bundle(text: str) -> list[tuple[str, str]]:
    """Split a bundle ingredient statement into (component_name, component_ingredients) pairs."""
    if not isinstance(text, str) or not text.strip():
        return []
    cleaned = re.sub(r"^(?:KIT CONTAINS|ASSORTMENT|VARIETY PACK|BUNDLE CONTAINS)\s*:\s*", "", text.strip(), flags=re.IGNORECASE)
    if "|" in cleaned:
        raw_parts = [p.strip() for p in cleaned.split("|") if p.strip()]
    else:
        raw_parts = [cleaned]
    out: list[tuple[str, str]] = []
    for idx, part in enumerate(raw_parts):
        if ":" in part:
            comp, ing = part.split(":", 1)
            out.append((comp.strip(), ing.strip()))
        else:
            out.append((f"Component_{idx + 1}", part.strip()))
    return out


def bundle_components(text: str) -> list[str]:
    """Return the list of component names in a bundle."""
    return [name for name, _ in split_bundle(text)]


def component_ingredients(text: str, component_name: str) -> str:
    """Return the ingredient string for a specific named component in a bundle."""
    for name, ing in split_bundle(text):
        if name.lower() == component_name.strip().lower():
            return ing
    return ""


def bundle_contains(text: str, additive: str = "RED3") -> bool:
    """Return True if any sub-component of the bundle contains additive."""
    return find_first_match(text, additive) is not None


def bundle_match_path(text: str, additive: str = "RED3") -> tuple[str, MatchResult] | None:
    """Locate the first component containing additive and return (component_name, full_text_match)."""
    m = find_first_match(text, additive)
    if m is None:
        return None
    comp_name = "Bundle"
    for name, ing in split_bundle(text):
        if find_first_match(ing, additive) is not None:
            comp_name = name
            break
    return comp_name, m


def flatten_bundle(text: str) -> str:
    """Flatten a bundle ingredient string into a single comma-separated statement."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return ", ".join(ing for _, ing in split_bundle(text))


def bundle_summary(text: str) -> dict:
    """Summarize bundle structure and component count."""
    comps = split_bundle(text)
    return {
        "is_bundle": is_bundle(text),
        "component_count": len(comps),
        "components": [c[0] for c in comps],
    }
