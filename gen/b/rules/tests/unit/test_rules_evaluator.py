"""Unit tests for recallstorm.rules.evaluate_sku."""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from contract import DecidedBy, Rule, Sku, SkuDecision, Verdict
from recallstorm.rules import evaluate_sku


@pytest.fixture
def sample_rules() -> list[Rule]:
    return [
        Rule(
            rule_id="CA_AB418_RED3",
            additive="RED3",
            aliases=(
                "FD&C Red No. 3",
                "Red No. 3",
                "Red 3",
                "Red Dye 3",
                "erythrosine",
                "E127",
            ),
            jurisdictions=("CA",),
            applies_to=("food",),
            effective=datetime(2027, 1, 1, 0, 0, 0),
            clause_ref="Cal. Health & Safety Code 109025(a)",
            source_text="Bans Red dye 3 in food starting Jan 1, 2027.",
        ),
        Rule(
            rule_id="FDA_RED3_FOOD",
            additive="RED3",
            aliases=(
                "FD&C Red No. 3",
                "Red No. 3",
                "Red 3",
                "Red Dye 3",
                "erythrosine",
                "E127",
            ),
            jurisdictions=("US",),
            applies_to=("food",),
            effective=datetime(2027, 1, 15, 0, 0, 0),
            clause_ref="21 CFR 74.303",
            source_text="FDA revokes Red No. 3 in food starting Jan 15, 2027.",
        ),
        Rule(
            rule_id="FDA_RED3_DRUG",
            additive="RED3",
            aliases=(
                "FD&C Red No. 3",
                "Red No. 3",
                "Red 3",
                "Red Dye 3",
                "erythrosine",
                "E127",
            ),
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
    sku_id: str = "SKU001",
    is_food: bool = True,
    is_ingested_drug: bool = False,
) -> Sku:
    return Sku(
        sku_id=sku_id,
        gtin="00012345678905",
        name="Test Product",
        brand="Test Brand",
        category="candy",
        ingredients=ingredients,
        is_food=is_food,
        is_ingested_drug=is_ingested_drug,
        case_units=12,
        case_cube_ft3=1.0,
        case_weight_lb=5.0,
    )


@pytest.mark.parametrize(
    "ingredients,expected_match",
    [
        ("SUGAR, FD&C RED #3, SALT.", "FD&C RED #3"),
        ("SUGAR, FD&C Red No. 3, WATER.", "FD&C Red No. 3"),
        ("CORN SYRUP, Red No. 3, CITRIC ACID", "Red No. 3"),
        ("CORN SYRUP, RED 3, YELLOW 5", "RED 3"),
        ("SUGAR, RED 3 POWDER, CARNAUBA WAX", "RED 3 POWDER"),
        ("SUGAR, FD&C RED #3 LAKE, SALT", "FD&C RED #3 LAKE"),
        ("CHERRIES (Red Dye 3), WATER", "Red Dye 3"),
        ("SUGAR, Red Dye #3, CORNSTARCH", "Red Dye #3"),
        ("SUGAR, erythrosine, WATER", "erythrosine"),
        ("SUGAR, ERYTHROSIN, WATER", "ERYTHROSIN"),
        ("NONPAREILS (SUGAR, CORNSTARCH, E127, RED 40)", "E127"),
        ("NONPAREILS (SUGAR, E-127, WATER)", "E-127"),
        ("AZUCAR, ERITROSINA, AGUA", "ERITROSINA"),
        ("SUCRE, ÉRYTHROSINE, EAU", "ÉRYTHROSINE"),
        ("AZUCAR, ROJO 3, AGUA", "ROJO 3"),
        ("AZUCAR, ROJO NO. 3, AGUA", "ROJO NO. 3"),
        ("SUGAR, R3D N0. 3, WATER", "R3D N0. 3"),
        ("SUGAR, FD&C R3D #3, WATER", "FD&C R3D #3"),
        ("SUGAR, 3RYTHR0S1N3, WATER", "3RYTHR0S1N3"),
        ("SUGAR, E1Z7, WATER", "E1Z7"),
        ("SUGAR, El27, WATER", "El27"),
    ],
)
def test_pull_aliases_and_ocr_variants(
    sample_rules: list[Rule], ingredients: str, expected_match: str
) -> None:
    at = datetime(2027, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    sku = _make_sku(ingredients)
    decision = evaluate_sku(sku, sample_rules, state="CA", at=at)

    assert decision.verdict == Verdict.PULL
    assert decision.additive == "RED3"
    assert decision.decided_by == DecidedBy.RULE
    assert decision.rule_ids == ("CA_AB418_RED3",)
    assert decision.match_text == expected_match
    assert decision.match_start is not None
    assert decision.match_end is not None
    assert ingredients[decision.match_start : decision.match_end] == expected_match


@pytest.mark.parametrize(
    "ingredients",
    [
        "CHERRIES, WATER, FD&C RED #40, SULFUR DIOXIDE.",
        "SUGAR, RED 40 LAKE, RED 40, YELLOW 5, BLUE 1.",
        "WATER, D&C RED 33, CITRIC ACID.",
        "WATER, D&C RED NO. 33, GLYCERIN.",
        "WATER, D&C RED NO. 3, GLYCERIN.",
        "EXT. D&C RED NO. 3, WATER.",
        "3 RED APPLES, SUGAR, CINNAMON.",
        "BEEF, 3 RED PEPPERS, GARLIC, ONION.",
        "CONTAINS 3 RED CHERRIES, WATER, SUGAR.",
        "HALVED CHERRIES (COLORED RED WITH CARMINE), ASCORBIC ACID.",
        "SUGAR, VITAMIN D3, ANNATTO, SALT.",
        "CORN SYRUP, RED 40, COLOR ADDED.",
        "ORGANIC WHEAT FLOUR, ORGANIC CANE SUGAR, SALT.",
    ],
)
def test_keep_decoys(sample_rules: list[Rule], ingredients: str) -> None:
    at = datetime(2027, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    sku = _make_sku(ingredients)
    decision = evaluate_sku(sku, sample_rules, state="CA", at=at)

    assert decision.verdict == Verdict.KEEP
    assert decision.additive is None
    assert decision.match_text is None
    assert decision.match_start is None
    assert decision.match_end is None
    assert decision.rule_ids == ()
    assert decision.decided_by == DecidedBy.RULE


def test_effective_time_and_timezone_conversion(sample_rules: list[Rule]) -> None:
    sku = _make_sku("SUGAR, FD&C RED #3, WATER.")

    # 2026-12-31 23:59:59 PST -> before CA_AB418_RED3 effective (2027-01-01 00:00:00 local)
    before_ca = datetime(2026, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("America/Los_Angeles"))
    dec_before = evaluate_sku(sku, sample_rules, state="CA", at=before_ca)
    assert dec_before.verdict == Verdict.KEEP

    # 2027-01-01 06:00:00 UTC is 2026-12-31 22:00:00 PST -> still before effective in CA local time!
    utc_before_pst = datetime(2027, 1, 1, 6, 0, 0, tzinfo=timezone.utc)
    dec_utc_before = evaluate_sku(sku, sample_rules, state="CA", at=utc_before_pst)
    assert dec_utc_before.verdict == Verdict.KEEP

    # 2027-01-01 08:00:00 UTC is 2027-01-01 00:00:00 PST -> effective in CA!
    utc_at_pst = datetime(2027, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    dec_at = evaluate_sku(sku, sample_rules, state="CA", at=utc_at_pst)
    assert dec_at.verdict == Verdict.PULL
    assert dec_at.rule_ids == ("CA_AB418_RED3",)

    # On 2027-01-16 PST, both CA_AB418_RED3 and FDA_RED3_FOOD are effective in CA
    after_fda = datetime(2027, 1, 16, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    dec_both = evaluate_sku(sku, sample_rules, state="CA", at=after_fda)
    assert dec_both.verdict == Verdict.PULL
    assert dec_both.rule_ids == ("CA_AB418_RED3", "FDA_RED3_FOOD")


def test_out_of_scope_jurisdiction_and_product_type(sample_rules: list[Rule]) -> None:
    at_jan2 = datetime(2027, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    sku_food = _make_sku("SUGAR, FD&C RED #3")

    # In NY on Jan 2, 2027: CA rule doesn't apply, and FDA_RED3_FOOD isn't effective until Jan 15
    dec_ny_early = evaluate_sku(sku_food, sample_rules, state="NY", at=at_jan2)
    assert dec_ny_early.verdict == Verdict.KEEP

    # In NY on Jan 16, 2027: FDA_RED3_FOOD (US) applies
    at_jan16 = datetime(2027, 1, 16, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    dec_ny_late = evaluate_sku(sku_food, sample_rules, state="NY", at=at_jan16)
    assert dec_ny_late.verdict == Verdict.PULL
    assert dec_ny_late.rule_ids == ("FDA_RED3_FOOD",)

    # Cosmetic product (neither food nor ingested_drug)
    sku_cosmetic = _make_sku("WATER, FD&C RED #3", is_food=False, is_ingested_drug=False)
    dec_cosmetic = evaluate_sku(sku_cosmetic, sample_rules, state="CA", at=at_jan16)
    assert dec_cosmetic.verdict == Verdict.KEEP

    # Ingested drug in 2027 (before 2028-01-18 effective date)
    sku_drug = _make_sku("ACTIVE: ACETAMINOPHEN. INACTIVE: FD&C RED #3", is_food=False, is_ingested_drug=True)
    dec_drug_2027 = evaluate_sku(sku_drug, sample_rules, state="CA", at=at_jan16)
    assert dec_drug_2027.verdict == Verdict.KEEP

    # Ingested drug in 2028
    at_2028 = datetime(2028, 1, 18, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    dec_drug_2028 = evaluate_sku(sku_drug, sample_rules, state="CA", at=at_2028)
    assert dec_drug_2028.verdict == Verdict.PULL
    assert dec_drug_2028.rule_ids == ("FDA_RED3_DRUG",)


@pytest.mark.parametrize(
    "ingredients",
    [
        "SUGAR, CORN SYRUP, CITRIC ACID, ARTIFICIAL COLOR.",
        "SUGAR, WATER, ARTIFICIAL COLORS ADDED.",
        "SUGAR, NATURAL FLAVOR, COLOR ADDED.",
        "SUGAR, CERTIFIED COLORS.",
        "",
        "   ",
        "[UNREADABLE LABEL]",
        "ILLEGIBLE - SMUDGED INK",
        "???",
        "\ufffd\ufffd\ufffd",
    ],
)
def test_hold_verify_when_vague_or_unreadable(sample_rules: list[Rule], ingredients: str) -> None:
    at = datetime(2027, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    sku = _make_sku(ingredients)
    decision = evaluate_sku(sku, sample_rules, state="CA", at=at)

    assert decision.verdict == Verdict.HOLD_VERIFY
    assert decision.decided_by == DecidedBy.RULE
    assert decision.rule_ids == ("CA_AB418_RED3",)


def test_classifier_called_only_when_rules_cannot_decide(sample_rules: list[Rule]) -> None:
    at = datetime(2027, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
    calls: list[str] = []

    def fake_classifier(sku: Sku, candidates: list[Rule]) -> SkuDecision:
        calls.append(sku.sku_id)
        return SkuDecision(
            sku_id=sku.sku_id,
            verdict=Verdict.HOLD_VERIFY,
            additive="RED3",
            match_text=None,
            match_start=None,
            match_end=None,
            rule_ids=tuple(r.rule_id for r in candidates),
            decided_by=DecidedBy.MODEL,
            rationale="Model fallback used.",
        )

    # Clear PULL -> classifier must NOT be called
    sku_pull = _make_sku("SUGAR, FD&C RED #3", sku_id="SKU_PULL")
    res_pull = evaluate_sku(sku_pull, sample_rules, state="CA", at=at, classifier=fake_classifier)
    assert res_pull.verdict == Verdict.PULL
    assert res_pull.decided_by == DecidedBy.RULE
    assert calls == []

    # Clear KEEP -> classifier must NOT be called
    sku_keep = _make_sku("SUGAR, WATER, RED 40", sku_id="SKU_KEEP")
    res_keep = evaluate_sku(sku_keep, sample_rules, state="CA", at=at, classifier=fake_classifier)
    assert res_keep.verdict == Verdict.KEEP
    assert res_keep.decided_by == DecidedBy.RULE
    assert calls == []

    # Ambiguous "ARTIFICIAL COLOR" -> classifier MUST be called
    sku_ambig = _make_sku("SUGAR, WATER, ARTIFICIAL COLOR.", sku_id="SKU_AMBIG")
    res_ambig = evaluate_sku(sku_ambig, sample_rules, state="CA", at=at, classifier=fake_classifier)
    assert res_ambig.verdict == Verdict.HOLD_VERIFY
    assert res_ambig.decided_by == DecidedBy.MODEL
    assert calls == ["SKU_AMBIG"]
