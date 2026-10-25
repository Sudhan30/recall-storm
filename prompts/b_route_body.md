You are writing ONE package of Recall Storm, a retailer compliance drill system: recallstorm/route/.
Scenario: California AB 418 bans selling food containing FD&C Red No. 3 from 2027-01-01 00:00 local.
Pulled cases go back from stores to their distribution center (DC) on return trucks.

Write only:
- recallstorm/__init__.py (empty docstring module)
- recallstorm/route/  pack_returns(pulled_cases, skus, trucks, stores) exactly as in contract.py.
                      pulled_cases maps (store_id, sku_id) -> cases. Each store's cases ride trucks of its
                      own DC (Store.dc_id). Cube and weight per case come from Sku.case_cube_ft3 and
                      Sku.case_weight_lb. Every manifest stays within its truck's cube_ft3 and weight_lb;
                      every pulled case is on exactly one stop; a store's load may be split across trucks
                      when it does not fit on one; no empty manifests; each truck used at most once.
                      Deterministic. Raise a clear error if a DC lacks capacity for its returns.
- tests/unit/test_route_*.py
Write nothing else. No other package exists.
