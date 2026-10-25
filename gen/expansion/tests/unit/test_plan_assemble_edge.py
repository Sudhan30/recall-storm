"""Edge tests for recallstorm.plan.assemble."""
from recallstorm.plan.assemble import validate_plan_refs


def test_validate_plan_refs_detects_broken_links():
    bad = [
        {
            "type": "sku_verdict",
            "sku_id": "S1",
            "gtin": "00012345678905",
            "verdict": "PULL",
            "additive": "RED3",
            "match": None,
            "rule_ids": ["R1"],
            "jurisdictions": ["CA"],
            "decided_by": "RULE",
            "evidence_id": "EVD-MISSING",
            "src": "test.py",
        }
    ]
    issues = validate_plan_refs(bad)
    assert any("missing evidence_id" in i for i in issues)
