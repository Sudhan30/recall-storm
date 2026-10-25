"""Evaluate SKUs against additive bans and jurisdiction/effective-time scopes."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from contract import Classifier, DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases import find_additive_match, is_unclear_or_generic_color


def _sku_applies_to_rule(sku: Sku, rule: Rule) -> bool:
    for scope in rule.applies_to:
        s = scope.lower()
        if s == "food" and sku.is_food:
            return True
        if s == "ingested_drug" and sku.is_ingested_drug:
            return True
        if s == "cosmetic" and not sku.is_food and not sku.is_ingested_drug:
            return True
    return False


def _jurisdiction_matches(state: str, rule: Rule) -> bool:
    state_up = state.upper()
    rule_juris = {j.upper() for j in rule.jurisdictions}
    return state_up in rule_juris or "US" in rule_juris


def _is_effective(at: datetime, rule: Rule, store_tz: str | None = None) -> bool:
    if at.tzinfo is not None:
        if store_tz:
            local_naive = at.astimezone(ZoneInfo(store_tz)).replace(tzinfo=None)
        else:
            local_naive = at.replace(tzinfo=None)
    else:
        local_naive = at
    rule_eff = rule.effective.replace(tzinfo=None) if rule.effective.tzinfo is not None else rule.effective
    return local_naive >= rule_eff


def applicable_rules(
    sku: Sku,
    rules: list[Rule],
    state: str,
    at: datetime,
    store_tz: str | None = None,
) -> list[Rule]:
    """Return all rules that apply to this SKU, jurisdiction, and timestamp."""
    matched: list[Rule] = []
    for r in rules:
        if not _jurisdiction_matches(state, r):
            continue
        if not _sku_applies_to_rule(sku, r):
            continue
        if not _is_effective(at, r, store_tz=store_tz):
            continue
        matched.append(r)
    return matched


def evaluate_sku(
    sku: Sku,
    rules: list[Rule],
    state: str,
    at: datetime,
    classifier: Classifier | None = None,
) -> SkuDecision:
    """Evaluate a SKU against active rules as specified in contract.py."""
    active_rules = applicable_rules(sku, rules, state, at)
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
            rationale="SKU is out of scope for active rules in jurisdiction/timeframe.",
        )

    matched_rules: list[Rule] = []
    first_match = None

    for r in active_rules:
        m = find_additive_match(sku.ingredients, r.aliases, r.additive)
        if m is not None:
            matched_rules.append(r)
            if first_match is None:
                first_match = m

    if matched_rules and first_match is not None:
        r_ids = tuple(r.rule_id for r in matched_rules)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive=first_match.additive,
            match_text=first_match.match_text,
            match_start=first_match.start,
            match_end=first_match.end,
            rule_ids=r_ids,
            decided_by=DecidedBy.RULE,
            rationale=f"Matched banned additive {first_match.additive} via '{first_match.match_text}' under {', '.join(r_ids)}.",
        )

    unclear, u_text, u_start, u_end = is_unclear_or_generic_color(sku.ingredients)
    if unclear:
        if classifier is not None:
            return classifier(sku, active_rules)
        r_ids = tuple(r.rule_id for r in active_rules)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive=active_rules[0].additive,
            match_text=u_text,
            match_start=u_start,
            match_end=u_end,
            rule_ids=r_ids,
            decided_by=DecidedBy.RULE,
            rationale="Ingredient label is ambiguous or declares generic color; manual verification required.",
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
        rationale="No prohibited additive detected in ingredients.",
    )
