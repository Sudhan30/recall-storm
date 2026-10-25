"""Unit tests for recallstorm.rules."""
from __future__ import annotations

from datetime import datetime
from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.rules import evaluate_sku


def _sample_rules() -> list[Rule]:
    return [
        Rule(
            rule_id="CA_AB418_RED3",
            additive="RED3",
            aliases=("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=datetime.fromisoformat("2027-01-01T00:00:00"),
            clause_ref="Cal. Health & Safety Code 109025(a)",
            source_text="California Red 3 ban.",
        ),
        Rule(
            rule_id="FDA_RED3_FOOD",
            additive="RED3",
            aliases=("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"),
            jurisdictions=("US",),
            applies_to=("food",),
            effective=datetime.fromisoformat("2027-01-15T00:00:00"),
            clause_ref="21 CFR 74.303",
            source_text="FDA Red 3 food ban.",
        ),
        Rule(
            rule_id="FDA_RED3_DRUG",
            additive="RED3",
            aliases=("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"),
            jurisdictions=("US",),
            applies_to=("ingested_drug",),
            effective=datetime.fromisoformat("2028-01-18T00:00:00"),
            clause_ref="21 CFR 74.1303",
            source_text="FDA Red 3 drug ban.",
        ),
    ]


def _make_sku(
    sku_id: str = "SKU1",
    ingredients: str = "sugar, FD&C Red No. 3",
    is_food: bool = True,
    is_ingested_drug: bool = False,
) -> Sku:
    return Sku(
        sku_id=sku_id,
        gtin="00012345678905",
        name="Test SKU",
        brand="Brand",
        category="candy",
        ingredients=ingredients,
        is_food=is_food,
        is_ingested_drug=is_ingested_drug,
        case_units=12,
        case_cube_ft3=1.0,
        case_weight_lb=10.0,
    )


def test_pull_food_in_ca_at_effective_date() -> None:
    rules = _sample_rules()
    sku = _make_sku(ingredients="sugar, corn syrup, FD&C Red No. 3, red 40")
    at = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    res = evaluate_sku(sku, rules, "CA", at)
    assert res.verdict == Verdict.PULL
    assert res.additive == "RED3"
    assert res.match_text == "FD&C Red No. 3"
    assert sku.ingredients[res.match_start : res.match_end] == "FD&C Red No. 3"
    assert res.rule_ids == ("CA_AB418_RED3",)
    assert res.decided_by == DecidedBy.RULE


def test_keep_before_effective_date() -> None:
    rules = _sample_rules()
    sku = _make_sku(ingredients="sugar, FD&C Red No. 3")
    at = datetime.fromisoformat("2026-12-31T23:59:59-08:00")
    res = evaluate_sku(sku, rules, "CA", at)
    assert res.verdict == Verdict.KEEP
    assert res.rule_ids == ()


def test_keep_cosmetic_out_of_scope() -> None:
    rules = _sample_rules()
    sku = _make_sku(ingredients="castor oil, red 3", is_food=False, is_ingested_drug=False)
    at = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    res = evaluate_sku(sku, rules, "CA", at)
    assert res.verdict == Verdict.KEEP


def test_keep_drug_before_2028() -> None:
    rules = _sample_rules()
    sku = _make_sku(ingredients="sorbitol, FD&C Red No. 3", is_food=False, is_ingested_drug=True)
    at = datetime.fromisoformat("2027-06-01T00:00:00-08:00")
    res = evaluate_sku(sku, rules, "CA", at)
    assert res.verdict == Verdict.KEEP

    at_2028 = datetime.fromisoformat("2028-01-18T00:00:00-08:00")
    res_2028 = evaluate_sku(sku, rules, "CA", at_2028)
    assert res_2028.verdict == Verdict.PULL
    assert res_2028.rule_ids == ("FDA_RED3_DRUG",)


def test_hold_verify_on_unclear_color() -> None:
    rules = _sample_rules()
    sku = _make_sku(ingredients="sugar, water, color added")
    at = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    res = evaluate_sku(sku, rules, "CA", at)
    assert res.verdict == Verdict.HOLD_VERIFY
    assert res.match_text == "color added"
    assert res.rule_ids == ("CA_AB418_RED3",)


def test_classifier_hook_used_when_provided_on_ambiguous() -> None:
    rules = _sample_rules()
    sku = _make_sku(ingredients="sugar, artificial color")
    at = datetime.fromisoformat("2027-01-01T00:00:00-08:00")

    def fake_classifier(s: Sku, candidates: list[Rule]) -> SkuDecision:
        return SkuDecision(
            sku_id=s.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive="RED3",
            match_text="artificial color",
            match_start=7,
            match_end=23,
            rule_ids=tuple(r.rule_id for r in candidates),
            decided_by=DecidedBy.MODEL,
            rationale="Model flagged uncertain artificial color.",
        )

    res = evaluate_sku(sku, rules, "CA", at, classifier=fake_classifier)
    assert res.verdict == Verdict.HOLD_VERIFY
    assert res.decided_by == DecidedBy.MODEL


def test_us_rule_applies_to_ca_after_jan_15() -> None:
    rules = _sample_rules()
    sku = _make_sku(ingredients="sugar, E127")
    at = datetime.fromisoformat("2027-01-16T00:00:00-08:00")
    res = evaluate_sku(sku, rules, "CA", at)
    assert res.verdict == Verdict.PULL
    assert "CA_AB418_RED3" in res.rule_ids
    assert "FDA_RED3_FOOD" in res.rule_ids
