"""Unit tests for recallstorm.aliases.bundles."""
from recallstorm.aliases.bundles import (
    bundle_components,
    bundle_contains,
    bundle_match_path,
    bundle_summary,
    component_ingredients,
    flatten_bundle,
    is_bundle,
    kit_keywords,
    split_bundle,
)


def test_bundle_parsing():
    kit_text = (
        "KIT CONTAINS: Frosted Pretzels: SUGAR, RED 3 POWDER, SALT. "
        "| Maraschino Cherries: CHERRIES, WATER, RED 40."
    )
    assert len(kit_keywords()) >= 3
    assert is_bundle(kit_text, "seasonal kits") is True
    parts = split_bundle(kit_text)
    assert len(parts) == 2
    assert bundle_components(kit_text) == ["Frosted Pretzels", "Maraschino Cherries"]
    assert "RED 3 POWDER" in component_ingredients(kit_text, "Frosted Pretzels")
    assert bundle_contains(kit_text, "RED3") is True
    path = bundle_match_path(kit_text, "RED3")
    assert path is not None
    assert path[0] == "Frosted Pretzels"
    assert kit_text[path[1].start:path[1].end] == "RED 3 POWDER"
    assert "CHERRIES" in flatten_bundle(kit_text)
    assert bundle_summary(kit_text)["component_count"] == 2
