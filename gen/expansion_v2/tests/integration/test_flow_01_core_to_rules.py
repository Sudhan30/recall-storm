"""Integration test 01: core -> ingest -> aliases -> rules -> adjudicate."""
from datetime import datetime
from contract import Verdict
from recallstorm.adjudicate.evidence import build_evidence, validate_evidence
from recallstorm.aliases.detect import find_first_match
from recallstorm.core.clock import to_local
from recallstorm.core.ids import validate_id_prefix
from recallstorm.ingest.usda_fdc import fdc_to_sku
from recallstorm.rules import evaluate_sku
from recallstorm.rules.red3 import red3_rules


def test_flow_core_ingest_aliases_rules_adjudicate():
    sku = fdc_to_sku(
        {
            "fdcId": 1034191,
            "gtinUpc": "07502264930572",
            "description": "Rainbow Sprinkles",
            "brandOwner": "Nayarit",
            "brandedFoodCategory": "Baking Decorations",
            "ingredients": "SUGAR, CORN SYRUP, FD&C RED #3, FD&C RED #40, SALT.",
        }
    )
    rules = red3_rules()
    m = find_first_match(sku.ingredients, rules[0].aliases, "RED3")
    assert m is not None

    at = to_local(datetime.fromisoformat("2027-01-01T00:00:00-08:00"), "America/Los_Angeles")
    dec = evaluate_sku(sku, rules, "CA", at)
    assert dec.verdict == Verdict.PULL
    ev = build_evidence(sku, dec, rules[0])
    assert validate_id_prefix(ev["evidence_id"], "EVD")
    assert validate_evidence(ev) == []
