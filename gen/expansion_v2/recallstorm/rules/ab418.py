"""California AB 418 (California Food Safety Act) four additives."""
from __future__ import annotations

from datetime import datetime

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import find_first_match
from recallstorm.rules.potassium_bromate import bromate_rules, evaluate_bromate
from recallstorm.rules.propylparaben import evaluate_propylparaben, paraben_rules
from recallstorm.rules.red3 import evaluate_red3, red3_rules

AB418_ADDITIVES: tuple[str, ...] = ("BVO", "POTASSIUM_BROMATE", "PROPYLPARABEN", "RED3")


def ab418_effective() -> datetime:
    """Return the naive local effective date for CA AB 418 (2027-01-01T00:00:00)."""
    return datetime(2027, 1, 1, 0, 0, 0)


def ab418_clause() -> str:
    """Return the statutory citation for CA AB 418."""
    return "Cal. Health & Safety Code 109025(a)"


def ab418_rules() -> list[Rule]:
    """Return all four CA AB 418 additive rules."""
    bvo_rule = Rule(
        rule_id="CA_AB418_BVO",
        additive="BVO",
        aliases=("brominated vegetable oil", "BVO", "E443"),
        jurisdictions=("CA",),
        applies_to=("food",),
        effective=ab418_effective(),
        clause_ref="Cal. Health & Safety Code 109025(a)(1)",
        source_text="Prohibits food products containing brominated vegetable oil commencing January 1, 2027.",
    )
    ca_red3 = [r for r in red3_rules() if r.rule_id == "CA_AB418_RED3"]
    return [bvo_rule] + bromate_rules() + paraben_rules() + ca_red3


def evaluate_bvo(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against CA AB 418 BVO prohibition."""
    wall = at.replace(tzinfo=None)
    if state.upper() != "CA" or not sku.is_food or wall < ab418_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or pre-effective")
    m = find_first_match(sku.ingredients, ("brominated vegetable oil", "BVO", "E443"), additive="BVO")
    if m:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="BVO",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("CA_AB418_BVO",),
            decided_by=DecidedBy.RULE,
            rationale=f"SKU {sku.sku_id} contains BVO ({m.match_text!r}) prohibited under CA AB 418.",
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "No BVO detected")


def evaluate_potassium_bromate(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against CA AB 418 potassium bromate prohibition."""
    return evaluate_bromate(sku, state, at)


def evaluate_propylparaben(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against CA AB 418 propylparaben prohibition."""
    from recallstorm.rules.propylparaben import evaluate_propylparaben as _eval_pp

    return _eval_pp(sku, state, at)


def evaluate_red3_ca(sku: Sku, state: str, at: datetime) -> SkuDecision:
    """Evaluate a Sku against CA AB 418 Red Dye 3 prohibition."""
    ca_rules = [r for r in red3_rules() if r.rule_id == "CA_AB418_RED3"]
    return evaluate_red3(sku, ca_rules, state, at)


def ab418_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize decisions across the four CA AB 418 additives."""
    by_add = {a: 0 for a in AB418_ADDITIVES}
    for d in decisions:
        if d.verdict == Verdict.PULL and d.additive in by_add:
            by_add[d.additive] += 1
    return {"by_additive": by_add, "total_pulled": sum(by_add.values())}
