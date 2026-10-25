"""Core rule evaluation logic for ingredient compliance."""
from __future__ import annotations

from datetime import datetime
import re
from zoneinfo import ZoneInfo

from contract import Classifier, DecidedBy, Rule, Sku, SkuDecision, Verdict

_STATE_DEFAULT_TZ: dict[str, str] = {
    "CA": "America/Los_Angeles",
    "WA": "America/Los_Angeles",
    "OR": "America/Los_Angeles",
    "NV": "America/Los_Angeles",
    "NY": "America/New_York",
    "FL": "America/New_York",
    "TX": "America/Chicago",
    "IL": "America/Chicago",
    "AZ": "America/Phoenix",
}

_RED3_BuiltIn_PATTERNS: list[re.Pattern[str]] = [
    # FD&C Red No. 3 / Red No. 3 / Red #3 / Red Dye 3 / Red 3 (with Lake/Powder/Dye variants & OCR noise)
    # Negative lookbehind rejects D&C / Ext. D&C decoys (e.g. D&C Red No. 3)
    re.compile(
        r"(?<![A-Za-z0-9])(?!(?:EXT\.?\s*)?D\s*(?:&|AND)\s*C\b)"
        r"(?:F\s*D\s*(?:&|AND|\+)?\s*C\s+)?"
        r"R\s*[E3]\s*D"
        r"(?:\s+D\s*Y\s*[E3])?"
        r"(?:\s*(?:N\s*[O0]\.?|N\s*U\s*M\s*B\s*[E3]\s*R|#))?"
        r"[\s.\-:]*3(?![0-9])"
        r"(?:\s+(?:L\s*A\s*K\s*[E3]|D\s*Y\s*[E3]|P\s*[O0]\s*W\s*D\s*[E3]\s*R))?"
        r"(?![A-Za-z0-9])"
        r"(?!\s*(?:%|P\s*E\s*P\s*P\s*E\s*R|A\s*P\s*P\s*L\s*E|B\s*E\s*A\s*N|B\s*E\s*R\s*R|"
        r"C\s*H\s*I\s*L\s*I|P\s*O\s*T\s*A\s*T\s*O|O\s*N\s*I\s*O\s*N|T\s*O\s*M\s*A\s*T\s*O|"
        r"C\s*A\s*B\s*B\s*A\s*G\s*E|G\s*R\s*A\s*P\s*E|C\s*H\s*E\s*R\s*R|P\s*I\s*M\s*I\s*E\s*N\s*T|"
        r"B\s*E\s*L\s*L\b|J\s*A\s*L\s*A\s*P|H\s*A\s*B\s*A\s*N|R\s*A\s*D\s*I\s*S\s*H|B\s*E\s*E\s*T|"
        r"L\s*E\s*N\s*T\s*I\s*L|Q\s*U\s*I\s*N\s*O\s*A|R\s*I\s*C\s*E|C\s*O\s*R\s*N|W\s*I\s*N\s*E|"
        r"V\s*I\s*N\s*E\s*G\s*A\s*R|S\s*A\s*U\s*C\s*E|M\s*E\s*A\s*T))",
        re.IGNORECASE,
    ),
    # E127 / E-127 / E 127 / INS 127 with OCR noise (E->3, 1->I/l, 2->Z, 7->T)
    re.compile(
        r"(?<![A-Za-z0-9])(?:[E3]|I\s*N\s*S)[\s.\-]*[1Il][2Z]7(?![0-9A-Za-z])",
        re.IGNORECASE,
    ),
    # Erythrosine / Erythrosin / Eritrosina / Érythrosine with OCR noise
    re.compile(
        r"(?<![A-Za-z0-9])[EÉÈÊ3]\s*R\s*[YI1l]\s*T\s*H?\s*R\s*[O0]\s*[S5]\s*[I1l]\s*N\s*[EA3]?(?![A-Za-z0-9])",
        re.IGNORECASE,
    ),
    # Spanish / French / Portuguese / German / Italian / CI names for Red 3
    re.compile(
        r"(?<![A-Za-z0-9])(?:"
        r"R\s*[O0]\s*J\s*[O0]\s*(?:F\s*D\s*&?\s*C\s*)?(?:N\s*[O0]\.?|#)?\s*3|"
        r"C\s*[O0]\s*L\s*[O0]\s*R\s*A\s*N\s*T\s*[E3]\s+R\s*[O0]\s*J\s*[O0]\s*(?:N\s*[O0]\.?|#)?\s*3|"
        r"R\s*[O0]\s*U\s*G\s*[E3]\s*(?:N\s*[O0]\.?|#)?\s*3|"
        r"V\s*[E3]\s*R\s*M\s*[E3]\s*L\s*H\s*[O0]\s*(?:N\s*[O0]\.?|#)?\s*3|"
        r"R\s*[O0]\s*S\s*S\s*[O0]\s*(?:N\s*[O0]\.?|#)?\s*3|"
        r"C\s*\.?\s*I\s*\.?\s*4\s*5\s*4\s*3\s*0|"
        r"A\s*C\s*[I1l]\s*D\s+R\s*[E3]\s*D\s+5\s*1"
        r")(?![0-9A-Za-z])",
        re.IGNORECASE,
    ),
]

_UNREADABLE_MARKERS: tuple[str, ...] = (
    "UNREADABLE",
    "ILLEGIBLE",
    "SMUDGED",
    "FADED",
    "OBSCURED",
    "TORN",
    "MISSING INGREDIENT",
    "MISSING LABEL",
    "OCR ERROR",
    "OCR_ERROR",
    "OCR FAILED",
    "SCAN FAILED",
    "CORRUPTED",
    "[???]",
    "???",
    "***",
    "###",
    "N/A",
    "NONE PROVIDED",
    "UNKNOWN",
)

# Matches generic/unspecified artificial color statements when no specific color is named nearby
_VAGUE_COLOR_PATTERN = re.compile(
    r"\b(?:"
    r"ARTIFICIAL\s+COLO(?:U)?RS?(?:\s+ADDED)?|"
    r"ARTIFICIALLY\s+COLO(?:U)?RED|"
    r"COLO(?:U)?R\s+ADDED|"
    r"ADDED\s+COLO(?:U)?RS?|"
    r"CERTIFIED\s+COLO(?:U)?RS?|"
    r"FD&C\s+COLO(?:U)?RS?|"
    r"U\.?S\.?\s+CERTIFIED\s+COLO(?:U)?RS?|"
    r"FOOD\s+COLO(?:U)?RING"
    r")\b"
    r"(?!\s*(?:\(|\s*\[|\s*:|\s*-|\s*INCLUDING|\s*FD&C|\s*RED|\s*YELLOW|\s*BLUE|\s*GREEN|"
    r"\s*CARAMEL|\s*ANNATTO|\s*BETA|\s*TITANIUM|\s*CARMINE|\s*TURMERIC|\s*PAPRIKA|\s*BEET))",
    re.IGNORECASE,
)

# Specific named colors: if an ingredient list only says "ARTIFICIAL COLOR (RED 40, BLUE 1)" it is NOT vague.
# Wait: what if a product has "RED 40, COLOR ADDED" (like FDC2655277 in sample data)?
# Notice FDC2655277 has: "RED 40 LAKE, RED 40, COLOR ADDED."
# Let's check whether FDC2655277 is KEEP or HOLD_VERIFY!
# In FDC2655277 ("Gummy Clusters Candy", _real: true), FDA labels often say "RED 40, COLOR ADDED" or "ARTIFICIAL COLORS".
# Wait: the prompt specifically says:
# `HOLD_VERIFY when the label says only "artificial color" or the text is unreadable`
# Look at the phrasing: `when the label says only "artificial color" or the text is unreadable`!
_SPECIFIC_COLOR_MENTION = re.compile(
    r"\b(?:"
    r"RED\s*(?:NO\.?\s*|#\s*|DYE\s*)?\d+|"
    r"YELLOW\s*(?:NO\.?\s*|#\s*|DYE\s*)?\d+|"
    r"BLUE\s*(?:NO\.?\s*|#\s*|DYE\s*)?\d+|"
    r"GREEN\s*(?:NO\.?\s*|#\s*|DYE\s*)?\d+|"
    r"E\s*1\d\d|"
    r"CARAMEL\s+COLO(?:U)?R|"
    r"ANNATTO|"
    r"CARMINE|"
    r"TITANIUM\s+DIOXIDE|"
    r"TURMERIC|"
    r"BETA[\s\-]*CAROTENE|"
    r"PAPRIKA|"
    r"BEET\s+(?:JUICE|POWDER|COLOR)|"
    r"SPIRULINA"
    r")\b",
    re.IGNORECASE,
)


def _local_naive_time(at: datetime, state: str) -> datetime:
    """Convert tz-aware `at` to naive wall-clock datetime for comparison with rule.effective."""
    if at.tzinfo is None:
        return at
    tz_name = _STATE_DEFAULT_TZ.get(state.upper())
    if tz_name:
        return at.astimezone(ZoneInfo(tz_name)).replace(tzinfo=None)
    return at.replace(tzinfo=None)


def _rule_applies_to_sku(rule: Rule, sku: Sku) -> bool:
    """Return True if the SKU product type falls within rule.applies_to."""
    for kind in rule.applies_to:
        k = kind.lower()
        if k == "food" and sku.is_food:
            return True
        if k == "ingested_drug" and sku.is_ingested_drug:
            return True
        if k == "cosmetic" and not sku.is_food and not sku.is_ingested_drug:
            return True
    return False


def _rule_applies_in_state(rule: Rule, state: str) -> bool:
    """Return True if rule applies in `state` (includes exact state match or 'US' when state is a US state)."""
    state_up = state.upper()
    rule_jurisdictions = {j.upper() for j in rule.jurisdictions}
    if state_up in rule_jurisdictions:
        return True
    if "US" in rule_jurisdictions and len(state_up) == 2 and state_up.isalpha():
        return True
    return False


def _compile_custom_alias_pattern(alias: str) -> re.Pattern[str]:
    """Compile a flexible regex pattern for any custom alias provided on a Rule."""
    tokens = re.split(r"[\s.\-#]+", alias.strip())
    tokens = [t for t in tokens if t]
    if not tokens:
        return re.compile(r"(?!x)x")
    parts: list[str] = []
    for tok in tokens:
        escaped = ""
        for ch in tok:
            u = ch.upper()
            if u == "E":
                escaped += "[E3ÉÈÊ]"
            elif u == "O":
                escaped += "[O0]"
            elif u == "I":
                escaped += "[I1l]"
            elif u == "S":
                escaped += "[S5]"
            elif u == "1":
                escaped += "[1Il]"
            elif u == "2":
                escaped += "[2Z]"
            else:
                escaped += re.escape(ch)
        parts.append(escaped)
    sep = r"[\s.\-#]*"
    body = sep.join(parts)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.IGNORECASE)


def _find_additive_match(text: str, rules: list[Rule]) -> tuple[re.Match[str], str, list[Rule]] | None:
    """Search ingredient text for any prohibited additive in active rules.

    Returns the earliest (and longest on tie) match, the additive code, and the matching rules.
    """
    best_match: re.Match[str] | None = None
    best_additive: str | None = None
    best_rules: list[Rule] = []

    by_additive: dict[str, list[Rule]] = {}
    for r in rules:
        by_additive.setdefault(r.additive, []).append(r)

    for additive, add_rules in by_additive.items():
        patterns: list[re.Pattern[str]] = []
        if additive.upper() in ("RED3", "RED_3", "FD&C RED NO. 3"):
            patterns.extend(_RED3_BuiltIn_PATTERNS)
        seen_aliases: set[str] = set()
        for r in add_rules:
            for alias in r.aliases:
                norm_a = alias.strip().upper()
                if norm_a not in seen_aliases:
                    seen_aliases.add(norm_a)
                    # Built-in patterns already handle standard Red 3 aliases with strict decoy protection
                    if additive.upper() == "RED3" and norm_a in {
                        "FD&C RED NO. 3",
                        "RED NO. 3",
                        "RED 3",
                        "RED DYE 3",
                        "ERYTHROSINE",
                        "E127",
                    }:
                        continue
                    patterns.append(_compile_custom_alias_pattern(alias))

        for pat in patterns:
            for m in pat.finditer(text):
                if best_match is None:
                    best_match = m
                    best_additive = additive
                    best_rules = add_rules
                else:
                    # Prefer earliest start, then longest span
                    if (m.start(), -(m.end() - m.start())) < (
                        best_match.start(),
                        -(best_match.end() - best_match.start()),
                    ):
                        best_match = m
                        best_additive = additive
                        best_rules = add_rules

    if best_match is not None and best_additive is not None:
        return best_match, best_additive, best_rules
    return None


def _is_unreadable(text: str) -> tuple[bool, str]:
    """Check whether the ingredient text is missing, corrupted, or unreadable."""
    if not text or not text.strip():
        return True, "Ingredient text is empty or missing."
    stripped = text.strip()
    upper = stripped.upper()

    if "\ufffd" in stripped:
        return True, "Ingredient text contains replacement characters indicating corrupted encoding."

    for marker in _UNREADABLE_MARKERS:
        if marker in upper:
            return True, f"Ingredient text contains unreadable/unclear marker ({marker})."

    # Check if there are too few alphabetic characters overall
    alpha_count = sum(1 for c in stripped if c.isalpha())
    if alpha_count < 3:
        return True, "Ingredient text contains insufficient readable alphabetic characters."

    non_space = sum(1 for c in stripped if not c.isspace())
    weird_chars = sum(
        1 for c in stripped if not (c.isalnum() or c.isspace() or c in ",.;:()[]{}&/'\"-%+#*!|")
    )
    if non_space > 0 and (weird_chars / non_space) > 0.15:
        return True, "Ingredient text has high ratio of garbled/unreadable symbols."

    return False, ""


def _has_only_vague_artificial_color(text: str) -> tuple[re.Match[str] | None, str]:
    """Detect when a label states only 'artificial color' (or equivalent) without specifying which color."""
    vague_match = _VAGUE_COLOR_PATTERN.search(text)
    if not vague_match:
        return None, ""
    if _SPECIFIC_COLOR_MENTION.search(text):
        return None, ""
    return (
        vague_match,
        f"Ingredient label specifies vague '{vague_match.group(0)}' without naming specific color additives.",
    )


def evaluate_sku(
    sku: Sku,
    rules: list[Rule],
    state: str,
    at: datetime,
    classifier: Classifier | None = None,
) -> SkuDecision:
    """Evaluate a SKU against regulatory rules in a given state and time.

    Args:
        sku: The SKU to evaluate.
        rules: Candidate regulatory rules.
        state: Two-letter state code (e.g., "CA").
        at: Timezone-aware evaluation timestamp.
        classifier: Optional fallback classifier for ambiguous items.

    Returns:
        SkuDecision with verdict, matched span, applicable rule IDs, and rationale.
    """
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
            rationale="No rules provided.",
        )

    # 1. Check product type scope
    type_matched_rules = [r for r in rules if _rule_applies_to_sku(r, sku)]
    if not type_matched_rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale="SKU product type is out of scope for all candidate rules.",
        )

    # 2. Check jurisdiction scope
    jurisdiction_matched_rules = [
        r for r in type_matched_rules if _rule_applies_in_state(r, state)
    ]
    if not jurisdiction_matched_rules:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale=f"No rules apply in jurisdiction '{state}'.",
        )

    # 3. Check effective timestamp in local wall-clock time
    local_at = _local_naive_time(at, state)
    active_rules = [r for r in jurisdiction_matched_rules if local_at >= r.effective]
    if not active_rules:
        earliest = min(r.effective for r in jurisdiction_matched_rules)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale=f"Evaluation time {local_at.isoformat()} is before rule effective time {earliest.isoformat()}.",
        )

    ingredients = sku.ingredients or ""

    # 4. Search for explicit banned additive match first
    match_info = _find_additive_match(ingredients, active_rules)
    if match_info is not None:
        m, additive, matched_rules = match_info
        rule_ids = tuple(r.rule_id for r in matched_rules)
        span_text = ingredients[m.start() : m.end()]
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive=additive,
            match_text=span_text,
            match_start=m.start(),
            match_end=m.end(),
            rule_ids=rule_ids,
            decided_by=DecidedBy.RULE,
            rationale=f"Matched banned additive {additive} ('{span_text}') under rules {', '.join(rule_ids)}.",
        )

    # 5. Check for unreadable text or vague "artificial color" requiring HOLD_VERIFY (or classifier fallback)
    unreadable, unreadable_reason = _is_unreadable(ingredients)
    vague_match, vague_reason = _has_only_vague_artificial_color(ingredients)

    if unreadable or vague_match is not None:
        if classifier is not None:
            return classifier(sku, active_rules)

        rule_ids = tuple(r.rule_id for r in active_rules)
        if vague_match is not None and not unreadable:
            span_text = ingredients[vague_match.start() : vague_match.end()]
            return SkuDecision(
                sku_id=sku.sku_id,
                verdict=Verdict.HOLD_VERIFY,
                additive=active_rules[0].additive,
                match_text=span_text,
                match_start=vague_match.start(),
                match_end=vague_match.end(),
                rule_ids=rule_ids,
                decided_by=DecidedBy.RULE,
                rationale=vague_reason,
            )

        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive=active_rules[0].additive,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=rule_ids,
            decided_by=DecidedBy.RULE,
            rationale=unreadable_reason,
        )

    # 6. Ingredient text is clear and does not contain the prohibited additive
    return SkuDecision(
        sku_id=sku.sku_id,
        verdict=Verdict.KEEP,
        additive=None,
        match_text=None,
        match_start=None,
        match_end=None,
        rule_ids=(),
        decided_by=DecidedBy.RULE,
        rationale="No prohibited additives detected in ingredients.",
    )
