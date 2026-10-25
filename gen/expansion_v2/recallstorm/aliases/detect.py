"""Exact and fuzzy span detection for regulated food/drug additives."""
from __future__ import annotations

from dataclasses import dataclass
import re

from recallstorm.aliases.decoys import is_dc_red_33
from recallstorm.aliases.lexicon import Lexicon, aliases_for, load_lexicon
from recallstorm.aliases.normalize import fold_unicode, ocr_fix
from recallstorm.aliases.spans import Span, span_from_match


@dataclass(frozen=True)
class MatchResult:
    """Detected additive match with exact character offsets in the original text."""

    additive: str
    alias: str
    match_text: str
    start: int
    end: int
    confidence: float = 1.0


def _alias_regex(alias: str, additive: str) -> re.Pattern:
    clean = alias.strip()
    upper = clean.upper()
    if additive.upper() == "RED3" and upper in {
        "FD&C RED NO. 3",
        "FD&C RED #3",
        "FD&C RED 3",
        "RED NO. 3",
        "RED #3",
        "RED 3",
        "RED DYE 3",
        "RED DYE NO. 3",
        "RED DYE #3",
    }:
        return re.compile(
            r"(?<![A-Za-z0-9&#])(?:FD\s*&\s*C\s+)?RED(?:\s+DYE)?(?:\s*(?:NO\.?|#))?\s*3(?![0-9A-Za-z])(?:\s+(?:LAKE|POWDER|ALUMINUM\s+LAKE))?",
            re.IGNORECASE,
        )
    escaped = re.escape(fold_unicode(clean))
    escaped = re.sub(r"\\\s+", r"\\s+", escaped)
    return re.compile(r"(?<![A-Za-z0-9])" + escaped + r"(?![A-Za-z0-9])", re.IGNORECASE)


def decoy_reason(text: str, start: int, end: int, additive: str = "RED3") -> str | None:
    """Return a reason string if the match at [start, end) is a false-positive decoy."""
    if not isinstance(text, str):
        return None
    ctx_start = max(0, start - 15)
    ctx_end = min(len(text), end + 15)
    ctx = text[ctx_start:ctx_end]
    matched = text[start:end]
    if additive.upper() == "RED3":
        if is_dc_red_33(ctx):
            return "D&C Red cosmetic dye, not FD&C Red No. 3"
        if re.search(r"^\s*\d", text[end : end + 2]):
            return "Followed by digit (e.g. Red 30/33/40)"
        if re.search(r"D\s*&\s*C\s*$", text[max(0, start - 6) : start], re.IGNORECASE) and not re.search(
            r"FD\s*&\s*C\s*$", text[max(0, start - 7) : start], re.IGNORECASE
        ):
            return "Preceded by D&C rather than FD&C"
        if re.search(r"\bRED\s+3\s+(?:PEPPER|BEAN|CHEESE|BERRY)", ctx, re.IGNORECASE):
            return "Quantity/culinary phrase"
    if not matched.strip():
        return "Empty match"
    return None


def is_decoy(text: str, start: int, end: int, additive: str = "RED3") -> bool:
    """Return True if the candidate span [start, end) is a decoy."""
    return decoy_reason(text, start, end, additive=additive) is not None


def find_matches(text: str, aliases: tuple[str, ...], additive: str = "RED3") -> list[MatchResult]:
    """Find all non-decoy matches of aliases in text with exact original character spans."""
    if not isinstance(text, str) or not text.strip():
        return []
    searchable = ocr_fix(fold_unicode(text))
    all_aliases = list(aliases)
    for extra in aliases_for(additive):
        if extra not in all_aliases:
            all_aliases.append(extra)

    raw_hits: list[MatchResult] = []
    seen_spans: set[tuple[int, int]] = set()

    # Check specific/longer aliases first so 'FD&C Red #3' wins over 'Red #3'
    ordered_aliases = sorted(set(all_aliases), key=lambda s: (-len(s), s))
    for al in ordered_aliases:
        pat = _alias_regex(al, additive)
        for m in pat.finditer(searchable):
            s, e = m.start(), m.end()
            if e > len(text):
                continue
            if is_decoy(searchable, s, e, additive=additive):
                continue
            if any(not (e <= ps or s >= pe) for ps, pe in seen_spans):
                continue
            seen_spans.add((s, e))
            orig_slice = text[s:e]
            conf = 1.0 if orig_slice.upper() == searchable[s:e].upper() else 0.92
            raw_hits.append(
                MatchResult(
                    additive=additive.upper(),
                    alias=al,
                    match_text=orig_slice,
                    start=s,
                    end=e,
                    confidence=conf,
                )
            )
    return sorted(raw_hits, key=lambda r: (r.start, -r.end))


def find_first_match(text: str, aliases: tuple[str, ...], additive: str = "RED3") -> MatchResult | None:
    """Return the earliest non-decoy MatchResult in text, or None."""
    matches = find_matches(text, aliases, additive=additive)
    return matches[0] if matches else None


def match_span(res: MatchResult) -> Span:
    """Convert a MatchResult into a Span."""
    return Span(start=res.start, end=res.end, text=res.match_text, label=res.additive)


def match_confidence(res: MatchResult) -> float:
    """Return the confidence score of a MatchResult."""
    return res.confidence


def detect_all_additives(text: str, lexicon: Lexicon | None = None) -> list[MatchResult]:
    """Detect all known additives from lexicon in text."""
    lex = lexicon or load_lexicon()
    out: list[MatchResult] = []
    for add, als in lex.by_additive.items():
        out.extend(find_matches(text, als, additive=add))
    return sorted(out, key=lambda r: (r.start, r.additive))


def explain_match(res: MatchResult) -> str:
    """Return a human-readable explanation of a MatchResult."""
    return f"Matched {res.additive} via {res.match_text!r} at [{res.start}:{res.end}] (confidence={res.confidence:.2f})"
