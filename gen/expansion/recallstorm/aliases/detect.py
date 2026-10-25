"""Precision additive detection with exact character spans and decoy rejection."""
from __future__ import annotations

import re
from dataclasses import dataclass
from recallstorm.aliases.decoys import (
    is_dc_red_33,
    is_product_name_phrase,
    is_quantity_phrase,
    is_red40,
)
from recallstorm.aliases.lexicon import Lexicon, aliases_for, load_lexicon
from recallstorm.aliases.normalize import fold_unicode
from recallstorm.aliases.spans import Span


@dataclass(frozen=True)
class MatchResult:
    """A verified additive match with exact character offsets into the original text."""

    additive: str
    match_text: str
    start: int
    end: int
    confidence: float = 1.0


_ADDITIVE_PATTERNS: dict[str, list[re.Pattern]] = {
    "RED3": [
        re.compile(
            r"(?<![A-Za-z0-9])(?:FD\s*&\s*C\s+Red\s+(?:Dye\s+)?(?:No\.?\s*|#)?\s*0?3(?:\s+(?:Lake|Powder|Aluminum\s+Lake))?)(?![0-9])",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?<![A-Za-z0-9&])(?:Red\s+Dye\s+(?:No\.?\s*|#)?\s*0?3(?:\s+(?:Lake|Powder))?)(?![0-9])",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?<![A-Za-z0-9&])(?:Red\s+(?:No\.?\s*|#)\s*0?3(?:\s+(?:Lake|Powder))?)(?![0-9])",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?<![A-Za-z0-9&])(?:Red\s+0?3(?:\s+(?:Lake|Powder))?)(?![0-9])",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?<![A-Za-z0-9])(?:erythrosine?|eritrosina|E[\s\-]?127|C\.?I\.?\s*45430|INS\s*127|rojo\s+(?:no\.?\s*)?0?3|rouge\s+0?3)(?![A-Za-z0-9])",
            re.IGNORECASE,
        ),
    ],
    "BVO": [
        re.compile(
            r"(?<![A-Za-z0-9])(?:brominated\s+vegetable\s+oil|BVO|E[\s\-]?443|aceite\s+vegetal\s+bromado|huile\s+vegetale\s+bromee)(?![A-Za-z0-9])",
            re.IGNORECASE,
        ),
    ],
    "POTASSIUM_BROMATE": [
        re.compile(
            r"(?<![A-Za-z0-9])(?:potassium\s+bromate|bromated\s+(?:wheat\s+)?flour|E[\s\-]?924a?|bromato\s+de\s+potasio|bromate\s+de\s+potassium)(?![A-Za-z0-9])",
            re.IGNORECASE,
        ),
    ],
    "PROPYLPARABEN": [
        re.compile(
            r"(?<![A-Za-z0-9])(?:propyl\s*paraben|propyl\s+p-hydroxybenzoate|E[\s\-]?21[67]|propilparabeno|propylparabene)(?![A-Za-z0-9])",
            re.IGNORECASE,
        ),
    ],
    "PFAS": [
        re.compile(
            r"(?<![A-Za-z0-9])(?:PTFE|polytetrafluoroethylene|PFOA|PFOS|perfluoroalkyl|fluoroalkyl|PFAS)(?![A-Za-z0-9])",
            re.IGNORECASE,
        ),
    ],
}


def decoy_reason(text: str, start: int, end: int) -> str | None:
    """Return a reason string if the span [start, end) in text is a decoy, else None."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    before = text[max(0, start - 8):start]
    if re.search(r"D\s*&\s*C\s+$", before, re.IGNORECASE) and not re.search(r"FD\s*&\s*C\s+$", before, re.IGNORECASE):
        return "D&C cosmetic dye, not FD&C Red No. 3"
    if is_quantity_phrase(text, start, end):
        return "Quantity/food phrase (e.g., peppers), not dye"
    if is_product_name_phrase(text, start, end):
        return "Botanical/food name phrase, not dye"
    matched = text[start:end]
    if re.search(r"\b40\b|\b33\b|\b30\b|\b28\b", matched):
        return "Different dye number (Red 40/33/30/28)"
    return None


def is_decoy(text: str, start: int, end: int, additive: str = "RED3") -> bool:
    """Return True if the candidate span is a decoy for additive."""
    if additive.upper() == "RED3":
        if decoy_reason(text, start, end) is not None:
            return True
        if is_red40(text, start) and "3" not in text[start:end]:
            return True
        if is_dc_red_33(text, start) and re.search(r"33|30|28", text[start:end]):
            return True
    return False


def find_matches(
    text: str,
    additive: str = "RED3",
    extra_aliases: tuple[str, ...] | list[str] | None = None,
) -> list[MatchResult]:
    """Find all non-decoy matches of additive in text with exact character spans."""
    if not isinstance(text, str) or not text:
        return []
    add = additive.strip().upper()
    folded = fold_unicode(text)
    patterns = list(_ADDITIVE_PATTERNS.get(add, []))
    for alias in extra_aliases or ():
        a_clean = fold_unicode(alias.strip())
        if a_clean:
            patterns.append(
                re.compile(r"(?<![A-Za-z0-9])" + re.escape(a_clean) + r"(?![A-Za-z0-9])", re.IGNORECASE)
            )
    if not patterns:
        for alias in aliases_for(add):
            a_clean = fold_unicode(alias.strip())
            if a_clean:
                patterns.append(
                    re.compile(r"(?<![A-Za-z0-9])" + re.escape(a_clean) + r"(?![A-Za-z0-9])", re.IGNORECASE)
                )

    raw_hits: list[MatchResult] = []
    for pat in patterns:
        for m in pat.finditer(folded):
            s, e = m.start(), m.end()
            if is_decoy(text, s, e, add):
                continue
            raw_hits.append(MatchResult(additive=add, match_text=text[s:e], start=s, end=e, confidence=1.0))

    raw_hits.sort(key=lambda r: (r.start, -(r.end - r.start)))
    deduped: list[MatchResult] = []
    for hit in raw_hits:
        if deduped and hit.start < deduped[-1].end:
            continue
        deduped.append(hit)
    return deduped


def find_first_match(
    text: str,
    additive: str = "RED3",
    extra_aliases: tuple[str, ...] | list[str] | None = None,
) -> MatchResult | None:
    """Return the earliest highest-priority match of additive in text, or None."""
    matches = find_matches(text, additive, extra_aliases)
    return matches[0] if matches else None


def match_span(match: MatchResult) -> Span:
    """Convert a MatchResult to a Span."""
    if not isinstance(match, MatchResult):
        raise TypeError("match must be a MatchResult")
    return Span(start=match.start, end=match.end, label=match.additive)


def match_confidence(match: MatchResult) -> float:
    """Return the confidence score of a MatchResult."""
    if not isinstance(match, MatchResult):
        raise TypeError("match must be a MatchResult")
    return match.confidence


def detect_all_additives(text: str, lexicon: Lexicon | None = None) -> list[MatchResult]:
    """Detect all known additives from the lexicon in text."""
    lx = lexicon or load_lexicon()
    out: list[MatchResult] = []
    for add in sorted(lx.entries.keys()):
        out.extend(find_matches(text, add, lx.entries[add]))
    out.sort(key=lambda r: (r.start, r.additive))
    return out


def explain_match(match: MatchResult) -> str:
    """Format a human-readable explanation of a MatchResult."""
    if not isinstance(match, MatchResult):
        raise TypeError("match must be a MatchResult")
    return f"Matched {match.additive} alias '{match.match_text}' at span [{match.start}:{match.end}]"
