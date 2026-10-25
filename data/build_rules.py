"""OURS. Writes data/rules.jsonl and data/scenario_ca_red3.json from primary legal text.

Rule.effective is a naive ISO wall-clock time, interpreted in each store's local tz.
"""
import json, pathlib

D = pathlib.Path(__file__).parent
ALIASES = ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"]

RULES = [
    {"rule_id": "CA_AB418_RED3", "additive": "RED3", "aliases": ALIASES, "jurisdictions": ["CA"],
     "applies_to": ["food"], "effective": "2027-01-01T00:00:00",
     "clause_ref": "Cal. Health & Safety Code 109025(a)",
     "source_text": "Commencing January 1, 2027, a person or entity shall not manufacture, sell, deliver, "
                    "distribute, hold, or offer for sale, in commerce a food product for human consumption "
                    "that contains any of the following substances: (1) Brominated vegetable oil. "
                    "(2) Potassium bromate. (3) Propylparaben. (4) Red dye 3."},
    {"rule_id": "FDA_RED3_FOOD", "additive": "RED3", "aliases": ALIASES, "jurisdictions": ["US"],
     "applies_to": ["food"], "effective": "2027-01-15T00:00:00",
     "clause_ref": "21 CFR 74.303 (revoked for food, 90 FR 4628)",
     "source_text": "FDA is revoking the authorization for the use of FD&C Red No. 3 in food and ingested "
                    "drugs. Manufacturers who use FD&C Red No. 3 in food have until January 15, 2027 to "
                    "reformulate their products."},
    {"rule_id": "FDA_RED3_DRUG", "additive": "RED3", "aliases": ALIASES, "jurisdictions": ["US"],
     "applies_to": ["ingested_drug"], "effective": "2028-01-18T00:00:00",
     "clause_ref": "21 CFR 74.1303 (revoked for ingested drugs, 90 FR 4628)",
     "source_text": "Manufacturers of ingested drugs have until January 18, 2028 to reformulate."},
]

SCENARIO = {"scenario_id": "ca_red3", "state": "CA", "rule_ids": ["CA_AB418_RED3"],
            "as_of": "2026-12-30T18:00:00-08:00", "deadline": "2027-01-01T00:00:00-08:00",
            "note": "every window must end before 2027-01-01T00:00 local"}

if __name__ == "__main__":
    with open(D / "rules.jsonl", "w") as f:
        for r in RULES:
            f.write(json.dumps(r) + "\n")
    (D / "scenario_ca_red3.json").write_text(json.dumps(SCENARIO, indent=2) + "\n")
    print("wrote rules.jsonl, scenario_ca_red3.json")
