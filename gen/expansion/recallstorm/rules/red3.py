"""FD&C Red No. 3 state (CA AB 418) and federal (21 CFR 74.303 / 74.1303) rules."""
from __future__ import annotations

from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.aliases.unclear import unclear_reason
from recallstorm.core.clock import from_local
from recallstorm.core.ids import make_evidence_id
from recallstorm.rules.dates import effective_at
from recallstorm.rules.jurisdiction import applies_in_state
from recallstorm.rules.scope import sku_in_scope

RED3_RULE_IDS: tuple[str, ...] = ("CA_AB418_RED3", "FDA_RED3_FOOD", "FDA_RED3_DRUG")


def red3_aliases() -> tuple[str, ...]:
    """Return canonical aliases for FD&C Red No. 3."""
    return ("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127")


def red3_rules() -> list[Rule]:
    """Return the three canonical FD&C Red No. 3 rules."""
    return [
        Rule(
            rule_id="CA_AB418_RED3",
            additive="RED3",
            aliases=red3_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=datetime(2027, 1, 1, 0, 0, 0),
            clause_ref="Cal. Health & Safety Code 109025(a)",
            source_text="Commencing January 1, 2027, Red dye 3 is prohibited in food in California.",
        ),
        Rule(
            rule_id="FDA_RED3_FOOD",
            additive="RED3",
            aliases=red3_aliases(),
            jurisdictions=("US",),
            applies_to=("food",),
            effective=datetime(2027, 1, 15, 0, 0, 0),
            clause_ref="21 CFR 74.303 (revoked for food, 90 FR 4628)",
            source_text="Manufacturers who use FD&C Red No. 3 in food have until January 15, 2027 to reformulate.",
        ),
        Rule(
            rule_id="FDA_RED3_DRUG",
            additive="RED3",
            aliases=red3_aliases(),
            jurisdictions=("US",),
            applies_to=("ingested_drug",),
            effective=datetime(2028, 1, 18, 0, 0, 0),
            clause_ref="21 CFR 74.1303 (revoked for ingested drugs, 90 FR 4628)",
            source_text="Manufacturers of ingested drugs have until January 18, 2028 to reformulate.",
        ),
    ]


def red3_clause(rule_id: str) -> str:
    """Return the statutory or regulatory clause reference for a Red 3 rule_id."""
    for r in red3_rules():
        if r.rule_id == rule_id:
            return r.clause_ref
    return "Cal. Health & Safety Code 109025(a)"


def red3_deadline(rule_id: str, tz_name: str = "America/Los_Angeles") -> datetime:
    """Return the tz-aware effective deadline for a Red 3 rule_id."""
    for r in red3_rules():
        if r.rule_id == rule_id:
            return from_local(r.effective, tz_name)
    return from_local(datetime(2027, 1, 1, 0, 0, 0), tz_name)


def red3_scope(sku: Sku, rule: Rule) -> bool:
    """Return True if SKU is in scope for the given Red 3 rule."""
    return sku_in_scope(sku, rule)


def red3_rationale(sku: Sku, match: MatchResult | None, rules: list[Rule]) -> str:
    """Build a human-readable rationale for a Red 3 decision."""
    if match is None:
        return f"No FD&C Red No. 3 detected in {sku.sku_id}."
    rids = ", ".join(r.rule_id for r in rules)
    return (
        f"Detected RED3 alias '{match.match_text}' at span [{match.start}:{match.end}] "
        f"prohibited by {rids}."
    )


def red3_evidence(sku: Sku, rule: Rule, match: MatchResult) -> dict:
    """Build an evidence record dictionary for a Red 3 match."""
    return {
        "evidence_id": make_evidence_id(sku.sku_id, rule.rule_id),
        "sku_id": sku.sku_id,
        "rule_id": rule.rule_id,
        "clause_ref": rule.clause_ref,
        "source_span": [match.start, match.end],
        "rationale": red3_rationale(sku, match, [rule]),
        "src": "recallstorm/rules/red3.py",
    }


def evaluate_red3(sku: Sku, rules: list[Rule] | None, state: str, at: datetime) -> SkuDecision:
    """Evaluate a SKU against Red No. 3 rules for state and timestamp at."""
    rlist = [r for r in (rules or red3_rules()) if r.additive.upper() == "RED3"]
    active = [
        r for r in rlist
        if applies_in_state(r, state) and sku_in_scope(sku, r) and effective_at(r, at)
    ]
    if not active:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.KEEP,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=(),
            decided_by=DecidedBy.RULE,
            rationale="No active Red No. 3 rule applies to this SKU at the given state and time.",
        )

    extra: list[str] = []
    for r in active:
        extra.extend(r.aliases)
    m = find_first_match(sku.ingredients, "RED3", extra)
    if m is not None:
        rids = tuple(sorted(r.rule_id for r in active))
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="RED3",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=rids,
            decided_by=DecidedBy.RULE,
            rationale=red3_rationale(sku, m, active),
        )

    ureason = unclear_reason(sku.ingredients)
    if ureason is not None:
        rids = tuple(sorted(r.rule_id for r in active))
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive="RED3",
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=rids,
            decided_by=DecidedBy.RULE,
            rationale=ureason,
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
        rationale=red3_rationale(sku, None, active),
    )
