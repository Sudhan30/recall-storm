"""Ingredient normalization, alias detection, decoy rejection, and SKU evaluation."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

from contract import Classifier, DecidedBy, Rule, Sku, SkuDecision, Verdict

STATE_DEFAULT_TZ: dict[str, str] = {
    "CA": "America/Los_Angeles",
    "OR": "America/Los_Angeles",
    "WA": "America/Los_Angeles",
    "NV": "America/Los_Angeles",
    "AZ": "America/Phoenix",
    "CO": "America/Denver",
    "UT": "America/Denver",
    "NM": "America/Denver",
    "TX": "America/Chicago",
    "IL": "America/Chicago",
    "NY": "America/New_York",
    "FL": "America/New_York",
    "PA": "America/New_York",
    "OH": "America/New_York",
    "GA": "America/New_York",
    "NC": "America/New_York",
    "MI": "America/New_York",
    "NJ": "America/New_York",
    "VA": "America/New_York",
    "MA": "America/New_York",
}

_OCR_CHAR_MAP: dict[str, str] = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "@": "a",
    "$": "s",
}

# Patterns for Red No. 3 and its aliases (English, multilingual, OCR-noisy, INS/E-numbers, CI numbers).
# Decoys like "D&C Red No. 3" (external drug/cosmetic without F), "Red 33", "Red 30", "Red 40",
# "3 red apples" are avoided via negative lookarounds and explicit token structure.
_RED3_PATTERNS: tuple[re.Pattern[str], ...] = (
    # FD&C Red No. 3 / Red No. 3 / Red #3 / Red Dye #3 / Red Lake 3 / Food Red 3 (with OCR support)
    re.compile(
        r"(?<![a-z0-9])"
        r"(?<!\bd\s&\s)(?<!\bd&)"
        r"(?:f\s*d\s*(?:&\s*|\+\s*|a\s*n\s*d\s+)?c\s+|f\s*[o0]\s*[o0]\s*d\s+)?"
        r"r\s*[e3]\s*d"
        r"(?:\s+(?:d\s*[y1i]\s*[e3]|l\s*[a4]\s*k\s*[e3]|c\s*[o0]\s*l\s*[o0]\s*u?\s*r))*"
        r"(?:[\s.\-:/()]*(?:n\s*[o0]\.?|n\s*u\s*m(?:b\s*[e3]\s*r)?\.?|#))?"
        r"[\s.\-:/()]*0*3(?!\s*r\s*[e3]\s*d)(?![0-9a-z])",
        re.IGNORECASE,
    ),
    # Erythrosine / Erythrosin / Eritrosina / Erythrosinum (with OCR digit-for-letter noise and diacritics)
    re.compile(
        r"(?<![a-z0-9])"
        r"[e3]\s*r\s*[y1i]\s*t\s*h?\s*r\s*[o0]\s*[s5$]\s*[i1l!|]\s*n\s*(?:[e3]|[a4]|u\s*m|b)?"
        r"(?![a-z0-9])",
        re.IGNORECASE,
    ),
    # E127 / E-127 / E 127 / INS 127 (with OCR noise like E-l27 or E-I27)
    re.compile(
        r"(?<![a-z0-9])"
        r"(?:[e3]|i\s*n\s*[s5])\s*[\-.:/()]*\s*[1il|]\s*2\s*7"
        r"(?![0-9a-z])",
        re.IGNORECASE,
    ),
    # Spanish / French / Italian / Portuguese / German / C.I. names for Red 3
    re.compile(
        r"(?<![a-z0-9])"
        r"(?:"
        r"r\s*[o0]\s*j\s*[o0]\s+(?:c\s*[o0]\s*l\s*[o0]\s*r\s*[a4]\s*n\s*t\s*[e3]\s+|"
        r"a\s*l\s*[i1l]\s*m\s*[e3]\s*n\s*t\s*[a4]\s*r\s*[i1l]\s*[o0]\s+)?"
        r"(?:n\s*[o0u]\.?|#)?\s*0*3"
        r"|r\s*[o0]\s*u\s*g\s*[e3]\s+(?:n\s*[o0]\.?|#)?\s*0*3"
        r"|r\s*[o0]\s*s\s*s\s*[o0]\s+(?:n\s*[o0]\.?|#)?\s*0*3"
        r"|v\s*[e3]\s*r\s*m\s*[e3]\s*l\s*h\s*[o0]\s+(?:n\s*[o0]\.?|#)?\s*0*3"
        r"|a\s*c\s*[i1l]\s*d\s+r\s*[e3]\s*d\s+5\s*1"
        r"|f\s*[o0]\s*[o0]\s*d\s+r\s*[e3]\s*d\s+1\s*4"
        r"|c\s*\.?\s*[i1l]\.?\s*4\s*5\s*4\s*3\s*0"
        r")"
        r"(?![0-9a-z])",
        re.IGNORECASE,
    ),
)

_AMBIGUOUS_COLOR_PATTERN = re.compile(
    r"(?<![a-z0-9])"
    r"(?:"
    r"a\s*r\s*t\s*[i1l]\s*f\s*[i1l]\s*c\s*[i1l]\s*[a4]\s*l\s+c\s*[o0]\s*l\s*[o0]\s*u?\s*r\s*(?:s|[i1l]\s*n\s*g)?"
    r"|c\s*[o0]\s*l\s*[o0]\s*u?\s*r\s+a\s*d\s*d\s*[e3]\s*d"
    r"|a\s*d\s*d\s*[e3]\s*d\s+c\s*[o0]\s*l\s*[o0]\s*u?\s*r\s*s?"
    r"|f\s*d\s*(?:&\s*|\+\s*)?c\s+c\s*[o0]\s*l\s*[o0]\s*u?\s*r\s*s?"
    r"|c\s*[e3]\s*r\s*t\s*[i1l]\s*f\s*[i1l]\s*[e3]\s*d\s+c\s*[o0]\s*l\s*[o0]\s*u?\s*r\s*s?"
    r"|u\s*n\s*s\s*p\s*[e3]\s*c\s*[i1l]\s*f\s*[i1l]\s*[e3]\s*d\s+(?:r\s*[e3]\s*d\s+)?(?:d\s*[y1i]\s*[e3]|c\s*[o0]\s*l\s*[o0]\s*u?\s*r)"
    r"|r\s*[e3]\s*d\s+(?:d\s*[y1i]\s*[e3]|c\s*[o0]\s*l\s*[o0]\s*u?\s*r(?:\s*[i1l]\s*n\s*g)?)(?!\s*(?:n\s*[o0]\.?|n\s*u\s*m|#)?\s*[0-9])"
    r"|c\s*[o0]\s*l\s*[o0]\s*r\s*[a4]\s*n\s*t\s*[e3]\s*s?\s+a\s*r\s*t\s*[i1l]\s*f\s*[i1l]\s*c\s*[i1l]\s*[a4]\s*l\s*(?:e\s*s)?"
    r")"
    r"(?![a-z0-9])",
    re.IGNORECASE,
)

_UNREADABLE_TOKENS: tuple[str, ...] = (
    "unreadable",
    "illegible",
    "smudged",
    "obscured",
    "missing",
    "torn",
    "damaged",
    "corrupted",
    "???",
    "***",
    "###",
    "[?]",
    "<unreadable>",
    "n/a",
    "tbd",
    "unknown",
)


def normalize_text(text: str) -> str:
    """Normalize text by stripping diacritics, converting to lowercase, and mapping OCR character noise."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = stripped.lower()
    ocr_cleaned = "".join(_OCR_CHAR_MAP.get(ch, ch) for ch in lowered)
    return re.sub(r"\s+", " ", ocr_cleaned).strip()


def _strip_diacritics_keep_length(text: str) -> str:
    """Strip diacritics while preserving exact 1-to-1 character indexing with original string."""
    out: list[str] = []
    for ch in text:
        decomposed = unicodedata.normalize("NFD", ch)
        base = "".join(c for c in decomposed if not unicodedata.combining(c))
        out.append(base if len(base) == 1 else ch)
    return "".join(out)


def _compile_generic_alias_pattern(alias: str) -> re.Pattern[str]:
    """Build a regex pattern for a general rule alias that tolerates OCR noise and punctuation."""
    norm_alias = _strip_diacritics_keep_length(alias.strip()).lower()
    tokens = re.findall(r"[a-z0-9]+|&|#", norm_alias)
    if not tokens:
        return re.compile(re.escape(alias), re.IGNORECASE)

    reverse_ocr: dict[str, str] = {
        "o": "[o0]",
        "i": "[i1l|!]",
        "l": "[l1i|!]",
        "e": "[e3]",
        "a": "[a4@]",
        "s": "[s5$]",
        "t": "[t7]",
        "b": "[b8]",
    }

    token_regexes: list[str] = []
    for tok in tokens:
        if tok == "&":
            token_regexes.append(r"(?:&|\+|and)")
        elif tok == "#":
            token_regexes.append(r"(?:#|no\.?|num(?:ber)?\.?)")
        elif tok in ("no", "num", "number"):
            token_regexes.append(r"(?:no\.?|num(?:ber)?\.?|#)?")
        elif tok.isdigit():
            token_regexes.append(r"0*" + re.escape(tok))
        else:
            char_pats = [reverse_ocr.get(c, re.escape(c)) for c in tok]
            token_regexes.append(r"\s*".join(char_pats))

    joined = r"[\s.\-:/()#]*".join(token_regexes)
    return re.compile(rf"(?<![a-z0-9]){joined}(?![a-z0-9])", re.IGNORECASE)


def find_additive_match(text: str, rule: Rule) -> tuple[int, int, str] | None:
    """Return the earliest (start, end, matched_substring) in `text` for `rule`, or None."""
    if not text:
        return None

    clean_indexed = _strip_diacritics_keep_length(text)
    candidates: list[tuple[int, int]] = []

    if rule.additive.upper() == "RED3" or any("red" in a.lower() and "3" in a for a in rule.aliases):
        for pat in _RED3_PATTERNS:
            for m in pat.finditer(clean_indexed):
                candidates.append((m.start(), m.end()))

    for alias in rule.aliases:
        # Avoid matching bare "Red 3" generic pattern if it's preceded by "D&C" without "F"
        pat = _compile_generic_alias_pattern(alias)
        for m in pat.finditer(clean_indexed):
            prefix = clean_indexed[max(0, m.start() - 6) : m.start()].lower()
            if re.search(r"(?<![f])d\s*&\s*c\s*$", prefix):
                continue
            # Also reject "<number> red" reversal decoys if any
            candidates.append((m.start(), m.end()))

    if not candidates:
        return None

    # Sort by earliest start, then longest span
    candidates.sort(key=lambda span: (span[0], -(span[1] - span[0])))
    start, end = candidates[0]
    return start, end, text[start:end]


def _is_unreadable_or_ambiguous(text: str) -> tuple[bool, str]:
    """Detect whether the ingredient text is unreadable/corrupted or lists only ambiguous artificial color."""
    if not text or not text.strip():
        return True, "Ingredient text is empty or missing."

    stripped = text.strip()
    lower = stripped.lower()

    if "\ufffd" in stripped:
        return True, "Ingredient text contains replacement characters indicating corruption."

    for tok in _UNREADABLE_TOKENS:
        if tok in lower:
            return True, f"Ingredient text contains unreadable/unclear marker ({tok!r})."

    alpha_count = sum(1 for ch in stripped if ch.isalpha())
    non_space_count = sum(1 for ch in stripped if not ch.isspace())
    if non_space_count > 0 and (alpha_count / non_space_count) < 0.4:
        return True, "Ingredient text has excessive non-alphabetic noise and is unreadable."

    if len(stripped) < 3:
        return True, "Ingredient text is too short to be a valid ingredient list."

    clean_indexed = _strip_diacritics_keep_length(stripped)
    ambig_match = _AMBIGUOUS_COLOR_PATTERN.search(clean_indexed)
    if ambig_match:
        matched_str = stripped[ambig_match.start() : ambig_match.end()]
        return True, f"Label lists ambiguous coloring ({matched_str!r}) without specifying dye number."

    return False, ""


def _sku_applies_to_rule(sku: Sku, rule: Rule) -> bool:
    """Check if the SKU's product type falls under the rule's applies_to categories."""
    for category in rule.applies_to:
        cat_lower = category.lower()
        if cat_lower == "food" and sku.is_food:
            return True
        if cat_lower == "ingested_drug" and sku.is_ingested_drug:
            return True
        if cat_lower == "cosmetic" and (
            sku.category.lower() == "cosmetic" or (not sku.is_food and not sku.is_ingested_drug)
        ):
            return True
    return False


def _rule_in_jurisdiction(rule: Rule, state: str) -> bool:
    """Check if the rule applies in the given state (matches state code or 'US')."""
    state_upper = state.upper()
    rule_jurisdictions = {j.upper() for j in rule.jurisdictions}
    return state_upper in rule_jurisdictions or "US" in rule_jurisdictions


def _rule_is_effective(rule: Rule, at: datetime, state: str) -> bool:
    """Compare `at` in the state's local timezone against naive `rule.effective`."""
    if at.tzinfo is not None:
        tz_name = STATE_DEFAULT_TZ.get(state.upper())
        if tz_name:
            local_at = at.astimezone(ZoneInfo(tz_name)).replace(tzinfo=None)
        else:
            local_at = at.replace(tzinfo=None)
    else:
        local_at = at
    return local_at >= rule.effective


def evaluate_sku(
    sku: Sku,
    rules: list[Rule],
    state: str,
    at: datetime,
    classifier: Classifier | None = None,
) -> SkuDecision:
    """Evaluate a SKU against compliance rules for a given state and timestamp."""
    if not rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale="No rules provided; item is out of scope.",
        )

    jurisdiction_rules = [r for r in rules if _rule_in_jurisdiction(r, state)]
    if not jurisdiction_rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale=f"No rules apply to jurisdiction {state!r}.",
        )

    type_rules = [r for r in jurisdiction_rules if _sku_applies_to_rule(sku, r)]
    if not type_rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale=f"SKU category ({sku.category!r}, is_food={sku.is_food}, is_ingested_drug={sku.is_ingested_drug}) is out of scope for applicable rules.",
        )

    active_rules = [r for r in type_rules if _rule_is_effective(r, at, state)]
    if not active_rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale="Evaluation timestamp is before the effective date of all applicable rules.",
        )

    matched_rules: list[Rule] = []
    best_match: tuple[int, int, str, str] | None = None  # (start, end, match_text, additive)

    for rule in active_rules:
        res = find_additive_match(sku.ingredients, rule)
        if res is not None:
            start, end, m_text = res
            matched_rules.append(rule)
            if best_match is None or (start, -(end - start)) < (
                best_match[0],
                -(best_match[1] - best_match[0]),
            ):
                best_match = (start, end, m_text, rule.additive)

    if matched_rules and best_match is not None:
        start, end, m_text, additive = best_match
        rule_ids = tuple(r.rule_id for r in matched_rules)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive=additive,
            match_text=m_text,
            match_start=start,
            match_end=end,
            rule_ids=rule_ids,
            decided_by=DecidedBy.RULE,
            rationale=f"Detected banned additive {additive} ({m_text!r}) at span [{start}:{end}] under rules {', '.join(rule_ids)}.",
        )

    is_unclear, unclear_reason = _is_unreadable_or_ambiguous(sku.ingredients)
    if is_unclear:
        if classifier is not None:
            return classifier(sku, active_rules)
        rule_ids = tuple(r.rule_id for r in active_rules)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=rule_ids,
            decided_by=DecidedBy.RULE,
            rationale=unclear_reason,
        )

    return SkuDecision(
        sku_id=sku.sku_id,
        verdict=Verdict.KEEP,
        additive=None,
        match_text=None,
        match_start=None,
        match_end=None,
        rule_ids=(),
        decided_by=DecidedBy.RULE,
        rationale="Ingredients are clear and contain no prohibited additives under active rules.",
    )
