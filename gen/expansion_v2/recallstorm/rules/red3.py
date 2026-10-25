"""FD&C Red No. 3 federal and state rules."""
from __future__ import annotations

from datetime import datetime

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import MatchResult, find_first_match
from recallstorm.core.ids import make_evidence_id
from recallstorm.rules.scope import applies_to_sku, sku_in_scope

RED3_RULE_IDS: tuple[str, ...] = ("CA_AB418_RED3", "FDA_RED3_FOOD", "FDA_RED3_DRUG")


def red3_aliases() -> tuple[str, ...]:
    """Return canonical FD&C Red No. 3 aliases."""
    return ("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127")


def red3_rules() -> list[Rule]:
    """Return the three core FD&C Red No. 3 rules (CA AB 418, FDA food, FDA ingested drug)."""
    return [
        Rule(
            rule_id="CA_AB418_RED3",
            additive="RED3",
            aliases=red3_aliases(),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=datetime(2027, 1, 1, 0, 0, 0),
            clause_ref="Cal. Health & Safety Code 109025(a)",
            source_text="Commencing January 1, 2027, a person or entity shall not manufacture, sell, deliver, distribute, hold, or offer for sale, in commerce a food product for human consumption that contains any of the following substances: (1) Brominated vegetable oil. (2) Potassium bromate. (3) Propylparaben. (4) Red dye 3.",
        ),
        Rule(
            rule_id="FDA_RED3_FOOD",
            additive="RED3",
            aliases=red3_aliases(),
            jurisdictions=("US",),
            applies_to=("food",),
            effective=datetime(2027, 1, 15, 0, 0, 0),
            clause_ref="21 CFR 74.303 (revoked for food, 90 FR 4628)",
            source_text="FDA is revoking the authorization for the use of FD&C Red No. 3 in food and ingested drugs. Manufacturers who use FD&C Red No. 3 in food have until January 15, 2027 to reformulate their products.",
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
    """Return statutory/CFR clause reference for a Red 3 rule_id."""
    for r in red3_rules():
        if r.rule_id == rule_id:
            return r.clause_ref
    return "21 CFR 74.303"


def red3_scope(sku: Sku, rule: Rule) -> bool:
    """Return True if sku is within the product scope of rule."""
    return sku_in_scope(sku, rule)


def red3_deadline(state: str, is_drug: bool = False) -> datetime:
    """Return the naive local effective deadline for Red No. 3 in state."""
    if is_drug:
        return datetime(2028, 1, 18, 0, 0, 0)
    if state.upper().strip() == "CA":
        return datetime(2027, 1, 1, 0, 0, 0)
    return datetime(2027, 1, 15, 0, 0, 0)


def red3_rationale(sku: Sku, match: MatchResult | None, rule_ids: tuple[str, ...]) -> str:
    """Build rationale string for a Red No. 3 decision."""
    if match and rule_ids:
        return f"SKU {sku.sku_id} contains FD&C Red No. 3 ({match.match_text!r}) prohibited by {', '.join(rule_ids)}."
    return f"SKU {sku.sku_id} does not violate active FD&C Red No. 3 rules."


def red3_evidence(sku: Sku, rule: Rule, match: MatchResult) -> dict:
    """Build an evidence record for a Red No. 3 match."""
    return {
        "type": "evidence",
        "evidence_id": make_evidence_id(sku.sku_id, rule.rule_id),
        "sku_id": sku.sku_id,
        "rule_id": rule.rule_id,
        "clause_ref": rule.clause_ref,
        "source_span": {"start": match.start, "end": match.end, "text": match.match_text},
        "rationale": red3_rationale(sku, match, (rule.rule_id,)),
        "src": "recallstorm/rules/red3.py",
    }


def evaluate_red3(sku: Sku, rules: list[Rule], state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against active Red No. 3 rules in state at time 'at'."""
    active_rules = [r for r in rules if r.additive.upper() == "RED3" and applies_to_sku(r, sku, state, at)]
    if not active_rules:
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "No active RED3 rule applies")
    combined_aliases: list[str] = []
    for r in active_rules:
        for al in r.aliases:
            if al not in combined_aliases:
                combined_aliases.append(al)
    m = find_first_match(sku.ingredients, tuple(combined_aliases), additive="RED3")
    if m:
        rids = tuple(r.rule_id for r in active_rules)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="RED3",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=rids,
            decided_by=DecidedBy.RULE,
            rationale=red3_rationale(sku, m, rids),
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, red3_rationale(sku, None, ()))
