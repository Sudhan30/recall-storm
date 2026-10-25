You are writing ONE package of Recall Storm, a retailer compliance drill system: recallstorm/rules/.
Scenario: California AB 418 bans selling food containing FD&C Red No. 3 from 2027-01-01 00:00 local.

Write only:
- recallstorm/__init__.py (empty docstring module)
- recallstorm/rules/  evaluate_sku(...) exactly as in contract.py. Normalize ingredient text and detect
                      Red No. 3 under every alias in the rules (including spacing, punctuation, "#", OCR
                      digit-for-letter noise, and non-English names such as eritrosina); reject decoys
                      (Red 40, D&C Red 33, "3 red apples"); return the match span in the original text.
                      HOLD_VERIFY when the label says only "artificial color" or the text is unreadable;
                      KEEP when out of scope (wrong product type, jurisdiction, or before the effective time).
                      With a classifier, call it only for items the rules cannot decide.
- tests/unit/test_rules_*.py
Write nothing else. No other package exists.
