"""California Food Safety Act (AB 418) covering BVO, potassium bromate, propylparaben, and Red Dye 3."""
from __future__ import annotations

from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.aliases.detect import find_first_match
from recallstorm.rules.potassium_bromate import bromate_rules, evaluate_bromate
from recallstorm.rules.propylparaben import evaluate_propylparaben, paraben_rules
from recallstorm.rules.red3 import evaluate_red3, red3_rules

AB418_ADDITIVES: tuple[str, ...] = ("BVO", "POTASSIUM_BROMATE", "PROPYLPARABEN", "RED3")


def ab418_effective() -> datetime:
    """Return the naive local effective date of California AB 418 (2027-01-01T00:00:00)."""
    return datetime(2027, 1, 1, 0, 0, 0)


def ab418_clause(additive: str) -> str:
    """Return the specific subsection of Cal. Health & Safety Code 109025(a) for additive."""
    mapping = {
        "BVO": "Cal. Health & Safety Code 109025(a)(1)",
        "POTASSIUM_BROMATE": "Cal. Health & Safety Code 109025(a)(2)",
        "PROPYLPARABEN": "Cal. Health & Safety Code 109025(a)(3)",
        "RED3": "Cal. Health & Safety Code 109025(a)(4)",
    }
    return mapping.get(additive.strip().upper(), "Cal. Health & Safety Code 109025(a)")


def ab418_rules() -> list[Rule]:
    """Return all four California AB 418 Rule objects."""
    bvo_ca = Rule(
        rule_id="CA_AB418_BVO",
        additive="BVO",
        aliases=("brominated vegetable oil", "BVO", "E443", "aceite vegetal bromado"),
        jurisdictions=("CA",),
        applies_to=("food",),
        effective=ab418_effective(),
        clause_ref=ab418_clause("BVO"),
        source_text="Commencing January 1, 2027, brominated vegetable oil is prohibited in food in California.",
    )
    red3_ca = [r for r in red3_rules() if r.rule_id == "CA_AB418_RED3"]
    return [bvo_ca] + bromate_rules() + paraben_rules() + red3_ca


def evaluate_bvo(sku: Sku, at: datetime) -> SkuDecision:
    """Evaluate a SKU for BVO under CA AB 418."""
    if not sku.is_food or at.replace(tzinfo=None) < ab418_effective():
        return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "Out of scope or before AB 418 effective date.")
    m = find_first_match(sku.ingredients, "BVO")
    if m is not None:
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.PULL,
            additive="BVO",
            match_text=m.match_text,
            match_start=m.start,
            match_end=m.end,
            rule_ids=("CA_AB418_BVO",),
            decided_by=DecidedBy.RULE,
            rationale=f"Contains prohibited BVO ('{m.match_text}') under {ab418_clause('BVO')}.",
        )
    return SkuDecision(sku.sku_id, Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "No BVO detected.")


def evaluate_potassium_bromate(sku: Sku, at: datetime) -> SkuDecision:
    """Evaluate a SKU for potassium bromate under CA AB 418."""
    return evaluate_bromate(sku, at)


def evaluate_propylparaben(sku: Sku, at: datetime) -> SkuDecision:
    """Evaluate a SKU for propylparaben under CA AB 418."""
    from recallstorm.rules.propylparaben import evaluate_propylparaben as _eval_p
    return _eval_p(sku, at)


def evaluate_red3_ca(sku: Sku, at: datetime) -> SkuDecision:
    """Evaluate a SKU for Red 3 under CA AB 418."""
    ca_only = [r for r in red3_rules() if r.rule_id == "CA_AB418_RED3"]
    return evaluate_red3(sku, ca_only, "CA", at)


def ab418_summary(decisions: list[SkuDecision]) -> dict:
    """Summarize decisions across the four CA AB 418 additives."""
    counts = {add: 0 for add in AB418_ADDITIVES}
    for d in decisions:
        if d.verdict == Verdict.PULL and d.additive in counts:
            counts[d.additive] += 1
    return {"by_additive": counts, "total_pulled": sum(counts.values())}
