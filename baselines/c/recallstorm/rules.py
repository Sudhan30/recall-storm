"""OURS. Baseline C (copied from D) rules: hand-written regex matcher for Red No. 3, no LLM.

evaluate_sku(sku, rules, state, at, classifier=None) -> SkuDecision (contract signature).
"""
from __future__ import annotations

import re
from datetime import datetime

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict

from ._src import src_of
SRC = src_of(__file__)

# --- alias patterns, matched on the ORIGINAL text so spans point into the ingredients ---
_O = "[o0]"          # OCR: o <-> 0
_I = "[i1l]"         # OCR: i <-> 1 <-> l
# erythrosine / erythrosin / eritrosina, tolerant of OCR digit swaps
_ERY = rf"\be[r]?[yi]th?r{_O}s{_I}n[ea]?\b"
# E127, E-127, E 127
_E127 = r"\bE\s*-?\s*127\b"
# [FD&C | F.D.&C. | F D & C] (Red|Rojo) [Dye] [No.|#|Number] 3, also RED3; not 30/33/40, not "3-bean"
_FDC = r"(?:F\.?\s*D\.?\s*&\s*C\.?\s*|D\.?\s*&\s*C\.?\s*)?"
_RED3 = (rf"\b{_FDC}(?:red|rojo)\s*(?:dye\s*)?(?:n{_O}\.?\s*|#\s*|number\s*)?3"
         r"(?!\s*\.?\d)(?!\s*-?\s*bean)")
ALIAS_RE = re.compile(rf"{_ERY}|{_E127}|{_RED3}", re.I)

# --- unclear labels ---
ILLEGIBLE_RE = re.compile(r"#{3,}|▒|\?{3,}|\billegible\b|\bunreadable\b|\bsmudged\b", re.I)
_DYE_NAME = r"(?:fd\s*&\s*c|yellow|blue|red|green|carmine|caramel|annatto|turmeric|titanium|beet|paprika|e\s*1\d\d)"
GENERIC_COLOR_RE = re.compile(
    r"\b(?:artificial\s+colou?rs?|colou?rs?\s+added|added\s+colou?rs?|certified\s+colou?rs?|colou?rings?)\b"
    rf"(?!\s*[\(\[:])(?!\s*{_DYE_NAME})", re.I)


def _scopes(sku: Sku) -> set[str]:
    s = set()
    if sku.is_food:
        s.add("food")
    if sku.is_ingested_drug:
        s.add("ingested_drug")
    if not s:
        s.add("cosmetic")
    return s


def _wall(at: datetime) -> datetime:
    """Rule.effective is naive local time; compare against the local wall clock of `at`."""
    return at.replace(tzinfo=None) if at.tzinfo is not None else at


def applicable_rules(sku: Sku, rules: list[Rule], state: str) -> list[Rule]:
    sc = _scopes(sku)
    return [r for r in rules
            if (state in r.jurisdictions or "US" in r.jurisdictions) and sc & set(r.applies_to)]


def find_alias(text: str):
    return ALIAS_RE.search(text or "")


def evaluate_sku(sku: Sku, rules: list[Rule], state: str, at: datetime, classifier=None) -> SkuDecision:
    app = applicable_rules(sku, rules, state)
    t = _wall(at)
    in_force = sorted((r for r in app if t >= r.effective), key=lambda r: r.rule_id)
    ing = sku.ingredients or ""
    m = find_alias(ing)

    def dec(verdict, rule_ids, why, match=None, by=DecidedBy.RULE):
        return SkuDecision(sku_id=sku.sku_id, verdict=verdict,
                           additive="RED3" if (match is not None or verdict == Verdict.PULL) else None,
                           match_text=match.group(0) if match else None,
                           match_start=match.start() if match else None,
                           match_end=match.end() if match else None,
                           rule_ids=tuple(rule_ids), decided_by=by, rationale=why)

    if not app:
        return dec(Verdict.KEEP, (), f"out of scope: {sorted(_scopes(sku))} not covered by any rule in {state}", m)
    if not in_force:
        return dec(Verdict.KEEP, (), f"no applicable rule in force at {t.isoformat()}", m)
    if m:
        return dec(Verdict.PULL, [r.rule_id for r in in_force],
                   f"ingredient {m.group(0)!r} is Red No. 3; prohibited by {', '.join(r.rule_id for r in in_force)}", m)
    unclear = ILLEGIBLE_RE.search(ing) or GENERIC_COLOR_RE.search(ing)
    if unclear:
        if classifier is not None:
            return classifier(sku, in_force)
        return SkuDecision(sku_id=sku.sku_id, verdict=Verdict.HOLD_VERIFY, additive=None,
                           match_text=unclear.group(0), match_start=unclear.start(), match_end=unclear.end(),
                           rule_ids=tuple(r.rule_id for r in in_force), decided_by=DecidedBy.RULE,
                           rationale=f"label unclear ({unclear.group(0)!r}); verify by hand")
    return dec(Verdict.KEEP, (), "no Red No. 3 alias in ingredients")
