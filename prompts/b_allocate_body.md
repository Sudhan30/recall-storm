You are writing ONE package of Recall Storm, a retailer compliance drill system: recallstorm/allocate/.
Scenario: California AB 418 bans selling food containing FD&C Red No. 3 from 2027-01-01 00:00 local.
Stores pull affected SKUs and need compliant substitutes shipped from their distribution center (DC).

Write only:
- recallstorm/__init__.py (empty docstring module)
- recallstorm/allocate/  allocate_substitutes(demand, stock, stores) exactly as in contract.py.
                         demand maps (store_id, sub_sku_id) -> cases wanted; each store draws only from
                         its own DC (Store.dc_id). Never exceed DcStock.cases; integer cases only; when
                         stock is short, split it fairly and deterministically, breaking ties by store_id.
                         Return one Allocation per (store, sub_sku) that receives cases > 0, with
                         dc_balance_after = the DC's remaining cases of that SKU after that allocation,
                         in a deterministic order. Validate inputs (negative demand, unknown store or DC).
- tests/unit/test_allocate_*.py
Write nothing else. No other package exists.
