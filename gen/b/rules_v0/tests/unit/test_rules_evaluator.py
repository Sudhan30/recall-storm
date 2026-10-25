"""Unit tests for recallstorm.rules SKU evaluation."""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.rules import evaluate_sku, find_additive_match, normalize_text


@pytest.fixture
def sample_rules() -> list[Rule]:
    return [
        Rule(
            rule_id="CA_AB418_RED3",
            additive="RED3",
            aliases=("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=datetime(2027, 1, 1, 0, 0, 0),
            clause_ref="Cal. Health & Safety Code 109025(a)",
            source_text="California AB 418 bans Red dye 3 in food starting Jan 1, 2027.",
        ),
        Rule(
            rule_id="FDA_RED3_FOOD",
            additive="RED3",
            aliases=("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"),
            jurisdictions=("US",),
            applies_to=("food",),
            effective=datetime(2027, 1, 15, 0, 0, 0),
            clause_ref="21 CFR 74.303",
            source_text="FDA revokes Red No. 3 in food starting Jan 15, 2027.",
        ),
        Rule(
            rule_id="FDA_RED3_DRUG",
            additive="RED3",
            aliases=("FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"),
            jurisdictions=("US",),
            applies_to=("ingested_drug",),
            effective=datetime(2028, 1, 18, 0, 0, 0),
            clause_ref="21 CFR 74.1303",
            source_text="FDA revokes Red No. 3 in ingested drugs starting Jan 18, 2028.",
        ),
    ]


def _make_sku(
    ingredients: str,
    *,
    sku_id: str = "SKU_TEST",
    is_food: bool = True,
    is_ingested_drug: bool = False,
    category: str = "candy",
) -> Sku:
    return Sku(
        sku_id=sku_id,
        gtin="00078000000009",
        name="Test Product",
        brand="Test Brand",
        category=category,
        ingredients=ingredients,
        is_food=is_food,
        is_ingested_drug=is_ingested_drug,
        case_units=12,
        case_cube_ft3=1.0,
        case_weight_lb=10.0,
    )


@pytest.mark.parametrize(
    "alias_in_text,expected_sub",
    [
        ("FD&C Red No. 3", "FD&C Red No. 3"),
        ("FD&C RED #3", "FD&C RED #3"),
        ("fd&c red no 3", "fd&c red no 3"),
        ("Red No. 3", "Red No. 3"),
        ("Red #3", "Red #3"),
        ("Red 3", "Red 3"),
        ("Red Dye 3", "Red Dye 3"),
        ("Red Dye #3", "Red Dye #3"),
        ("Red Dye No. 3", "Red Dye No. 3"),
        ("Red3", "Red3"),
        ("Red-3", "Red-3"),
        (" erythrosine ", "erythrosine"),
        ("erythros1ne", "erythros1ne"),
        ("3rythrosin3", "3rythrosin3"),
        ("eritrosina", "eritrosina"),
        ("érythrosine", "érythrosine"),
        ("E127", "E127"),
        ("E-127", "E-127"),
        ("E 127", "E 127"),
        ("INS 127", "INS 127"),
        ("rojo 3", "rojo 3"),
        ("Rojo No. 3", "Rojo No. 3"),
        ("CI 45430", "CI 45430"),
        ("C.I. 45430", "C.I. 45430"),
        ("Acid Red 51", "Acid Red 51"),
        ("Food Red 14", "Food Red 14"),
        ("R3d N0. 3", "R3d N0. 3"),
    ],
)
def test_pull_aliases_and_exact_span(
    sample_rules: list[Rule], alias_in_text: str, expected_sub: str
) -> None:
    prefix = "sugar, corn syrup, water, citric acid, "
    suffix = ", natural flavor, red 40"
    full_ingredients = f"{prefix}{alias_in_text}{suffix}"
    sku = _make_sku(full_ingredients)
    at = datetime(2027, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))

    decision = evaluate_sku(sku, sample_rules, state="CA", at=at)

    assert decision.verdict == Verdict.PULL
    assert decision.additive == "RED3"
    assert decision.decided_by == DecidedBy.RULE
    assert decision.rule_ids == ("CA_AB418_RED3",)
    assert decision.match_text == expected_sub
    assert decision.match_start is not None
    assert decision.match_end is not None
    assert full_ingredients[decision.match_start : decision.match_end] == expected_sub


@pytest.mark.parametrize(
    "decoy_ingredients",
    [
        "sugar, corn syrup, water, Red 40, Yellow 5",
        "sugar, water, FD&C Red No. 40, citric acid",
        "sugar, water, D&C Red 33, natural flavor",
        "sugar, water, D&C Red No. 33, salt",
        "sugar, water, D&C Red No. 3, salt",
        "sugar, water, Red 30, Red 33, Red 300",
        "sugar, corn syrup, 3 red apples, cinnamon",
        "organic 3 red bell peppers, vinegar, salt",
        "water, vitamin B3, red beet juice, salt",
        "sugar, E129, E124, E122, salt",
        "sugar, corn syrup, water, citric acid, natural flavor, salt",
    ],
)
def test_reject_decoys(sample_rules: list[Rule], decoy_ingredients: str) -> None:
    sku = _make_sku(decoy_ingredients)
    at = datetime(2027, 1, 2, 12, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))

    decision = evaluate_sku(sku, sample_rules, state="CA", at=at)

    assert decision.verdict == Verdict.KEEP
    assert decision.additive is None
    assert decision.match_text is None
    assert decision.match_start is None
    assert decision.match_end is None
    assert decision.rule_ids == ()
    assert decision.decided_by == DecidedBy.RULE


@pytest.mark.parametrize(
    "unclear_ingredients",
    [
        "sugar, corn syrup, water, artificial color",
        "sugar, water, artificial colors, natural flavor",
        "sugar, corn syrup, color added",
        "sugar, water, artificial coloring",
        "sugar, FD&C colors, citric acid",
        "sugar, red dye, water",
        "",
        "   ",
        "unreadable label smudged",
        "sugar, corn syrup, ???",
        "$$$###***@@@",
    ],
)
def test_hold_verify_without_classifier(
    sample_rules: list[Rule], unclear_ingredients: str
) -> None:
    sku = _make_sku(unclear_ingredients)
    at = datetime(2027, 1, 1, 8, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))

    decision = evaluate_sku(sku, sample_rules, state="CA", at=at, classifier=None)

    assert decision.verdict == Verdict.HOLD_VERIFY
    assert decision.additive is None
    assert decision.match_text is None
    assert decision.match_start is None
    assert decision.match_end is None
    assert decision.rule_ids == ("CA_AB418_RED3",)
    assert decision.decided_by == DecidedBy.RULE


def test_classifier_called_only_when_undecided(sample_rules: list[Rule]) -> None:
    calls: list[tuple[str, list[str]]] = []

    def fake_classifier(sku: Sku, candidates: list[Rule]) -> SkuDecision:
        calls.append((sku.sku_id, [r.rule_id for r in candidates]))
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive=None,
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=tuple(r.rule_id for r in candidates),
            decided_by=DecidedBy.MODEL,
            rationale="Model could not confirm specific dye from 'color added'.",
        )

    at = datetime(2027, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))

    # 1. Definite PULL -> classifier NOT called
    pull_sku = _make_sku("sugar, FD&C Red No. 3", sku_id="SKU_PULL")
    res_pull = evaluate_sku(pull_sku, sample_rules, state="CA", at=at, classifier=fake_classifier)
    assert res_pull.verdict == Verdict.PULL
    assert res_pull.decided_by == DecidedBy.RULE
    assert len(calls) == 0

    # 2. Definite KEEP -> classifier NOT called
    keep_sku = _make_sku("sugar, water, salt, Red 40", sku_id="SKU_KEEP")
    res_keep = evaluate_sku(keep_sku, sample_rules, state="CA", at=at, classifier=fake_classifier)
    assert res_keep.verdict == Verdict.KEEP
    assert res_keep.decided_by == DecidedBy.RULE
    assert len(calls) == 0

    # 3. Out-of-scope KEEP (even with unclear ingredients) -> classifier NOT called
    cosmetic_sku = _make_sku(
        "castor oil, artificial color",
        sku_id="SKU_COSMETIC",
        is_food=False,
        is_ingested_drug=False,
        category="cosmetic",
    )
    res_cos = evaluate_sku(cosmetic_sku, sample_rules, state="CA", at=at, classifier=fake_classifier)
    assert res_cos.verdict == Verdict.KEEP
    assert len(calls) == 0

    # 4. Ambiguous in-scope item -> classifier IS called
    unclear_sku = _make_sku("sugar, water, color added", sku_id="SKU_UNCLEAR")
    res_unclear = evaluate_sku(
        unclear_sku, sample_rules, state="CA", at=at, classifier=fake_classifier
    )
    assert res_unclear.verdict == Verdict.HOLD_VERIFY
    assert res_unclear.decided_by == DecidedBy.MODEL
    assert calls == [("SKU_UNCLEAR", ["CA_AB418_RED3"])]


def test_scope_product_type_and_jurisdiction_and_effective_time(
    sample_rules: list[Rule],
) -> None:
    red3_food = _make_sku("sugar, FD&C Red No. 3", sku_id="FOOD_RED3", is_food=True)
    red3_cosmetic = _make_sku(
        "castor oil, red 3",
        sku_id="COS_RED3",
        is_food=False,
        is_ingested_drug=False,
        category="cosmetic",
    )
    red3_drug = _make_sku(
        "acetaminophen, FD&C Red No. 3",
        sku_id="DRUG_RED3",
        is_food=False,
        is_ingested_drug=True,
        category="otc_drug",
    )

    # Before CA effective date: 2026-12-31 23:59:59 PST -> KEEP
    before_ca = datetime(2026, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("America/Los_Angeles"))
    assert evaluate_sku(red3_food, sample_rules, state="CA", at=before_ca).verdict == Verdict.KEEP

    # Exactly at CA effective instant in UTC (2027-01-01 08:00:00Z == 2027-01-01 00:00:00 PST) -> PULL
    at_ca_utc = datetime(2027, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    dec_ca = evaluate_sku(red3_food, sample_rules, state="CA", at=at_ca_utc)
    assert dec_ca.verdict == Verdict.PULL
    assert dec_ca.rule_ids == ("CA_AB418_RED3",)

    # On 2027-01-02 in TX, CA rule does not apply and US food rule (2027-01-15) is not yet effective -> KEEP
    jan2_utc = datetime(2027, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    assert evaluate_sku(red3_food, sample_rules, state="TX", at=jan2_utc).verdict == Verdict.KEEP

    # On 2027-01-16 in CA, both CA_AB418_RED3 and FDA_RED3_FOOD are effective -> PULL with both rule_ids
    jan16_la = datetime(2027, 1, 16, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    dec_both = evaluate_sku(red3_food, sample_rules, state="CA", at=jan16_la)
    assert dec_both.verdict == Verdict.PULL
    assert dec_both.rule_ids == ("CA_AB418_RED3", "FDA_RED3_FOOD")

    # Cosmetic is never covered by food/ingested_drug rules -> KEEP
    assert evaluate_sku(red3_cosmetic, sample_rules, state="CA", at=jan16_la).verdict == Verdict.KEEP

    # Ingested drug before 2028-01-18 -> KEEP; on/after 2028-01-18 -> PULL under FDA_RED3_DRUG
    assert evaluate_sku(red3_drug, sample_rules, state="CA", at=jan16_la).verdict == Verdict.KEEP
    jan19_2028 = datetime(2028, 1, 19, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    dec_drug = evaluate_sku(red3_drug, sample_rules, state="CA", at=jan19_2028)
    assert dec_drug.verdict == Verdict.PULL
    assert dec_drug.rule_ids == ("FDA_RED3_DRUG",)


def test_normalize_text_and_find_additive_match(sample_rules: list[Rule]) -> None:
    assert normalize_text("  Érythr0s1ne   #3 ") == "erythrosine #e"
    rule = sample_rules[0]
    match = find_additive_match("Ingredients: sugar, Érythrosine, water", rule)
    assert match == (20, 31, "Érythrosine")
