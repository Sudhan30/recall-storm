"""Unit tests for recallstorm.aliases."""
from __future__ import annotations

import pytest
from recallstorm.aliases import (
    find_additive_match,
    is_unclear_or_generic_color,
    normalize_text,
)

RED3_ALIASES = (
    "FD&C Red No. 3",
    "Red No. 3",
    "Red 3",
    "Red Dye 3",
    "erythrosine",
    "E127",
)


@pytest.mark.parametrize(
    "ingredients,expected_substr",
    [
        ("sugar, corn syrup, FD&C Red No. 3, red 40", "FD&C Red No. 3"),
        ("sugar, FD&C RED #3, red 40", "FD&C RED #3"),
        ("sugar, Red No. 3, citric acid", "Red No. 3"),
        ("sugar, Red No 3, water", "Red No 3"),
        ("sugar, Red Dye 3, natural flavor", "Red Dye 3"),
        ("sugar, Red Dye #3, water", "Red Dye #3"),
        ("castor oil, red 3", "red 3"),
        ("sugar, RED #3, water", "RED #3"),
        ("sugar, erythrosine, water", "erythrosine"),
        ("sugar, erythros1ne, red 40", "erythros1ne"),
        ("water, E127, sugar", "E127"),
        ("water, E-127, sugar", "E-127"),
        ("sugar, Red 3 Lake, corn syrup", "Red 3 Lake"),
    ],
)
def test_detects_all_red3_aliases_and_variants(ingredients: str, expected_substr: str) -> None:
    match = find_additive_match(ingredients, RED3_ALIASES, "RED3")
    assert match is not None
    assert match.match_text == expected_substr
    assert ingredients[match.start : match.end] == expected_substr


@pytest.mark.parametrize(
    "decoy_ingredients",
    [
        "sugar, corn syrup, water, Red 40",
        "sugar, FD&C Red No. 40, citric acid",
        "sugar,FD&C Red #40, yellow 5",
        "water, D&C Red 33, fragrance",
        "water, D&C Red No. 33, glycerin",
        "water, D&C Red No. 3, wax",
        "sugar, corn syrup, 3 red apples",
        "water, red 30, titanium dioxide",
        "water, Red No. 33, sugar",
        "sugar, salt, natural flavor",
    ],
)
def test_rejects_decoys(decoy_ingredients: str) -> None:
    match = find_additive_match(decoy_ingredients, RED3_ALIASES, "RED3")
    assert match is None


@pytest.mark.parametrize(
    "unclear_text",
    [
        "sugar, corn syrup, color added",
        "sugar, artificial color, water",
        "sugar, artificial colors, citric acid",
        "   ",
        "???",
        "[illegible label text]",
    ],
)
def test_detects_unclear_or_generic_color(unclear_text: str) -> None:
    is_unclear, _, _, _ = is_unclear_or_generic_color(unclear_text)
    assert is_unclear is True


def test_normalize_text() -> None:
    assert normalize_text("  FD&C   Red-No. 3 \n ") == "fd&c red no. 3"
