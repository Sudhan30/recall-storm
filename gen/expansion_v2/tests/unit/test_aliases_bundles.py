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


def test_bundles():
    sample = (
        "KIT CONTAINS: Frosted Pretzels: SUGAR, RED 3 POWDER, SALT. | "
        "Maraschino Cherries: CHERRIES, WATER, RED 40."
    )
    assert is_bundle(sample, "seasonal kits") is True
    assert len(kit_keywords()) >= 3
    comps = split_bundle(sample)
    assert len(comps) == 2
    assert bundle_components(sample) == ["Frosted Pretzels", "Maraschino Cherries"]
    assert "RED 3 POWDER" in component_ingredients(sample)["Frosted Pretzels"]
    assert bundle_contains(sample, ("Red 3",), "RED3") is True
    path = bundle_match_path(sample, ("Red 3",), "RED3")
    assert path is not None
    comp_name, match = path
    assert comp_name == "Frosted Pretzels"
    assert sample[match.start : match.end] == match.match_text
    assert bundle_summary(sample)["component_count"] == 2
    assert "CHERRIES" in flatten_bundle(sample)
