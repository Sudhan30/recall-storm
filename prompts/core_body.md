You are writing the WORKING CORE of Recall Storm, a retailer compliance drill system.
Scenario: California AB 418 bans selling food containing FD&C Red No. 3 from 2027-01-01 00:00 local.
Build a package `recallstorm/` that, given a DataPack (see contract.py), writes plan.jsonl and events.jsonl.

Required packages, in this order:
- recallstorm/aliases/    normalize ingredient text, detect Red No. 3 under every alias in the rules,
                          reject decoys (Red 40, D&C Red 33, "3 red apples"), return the match span
- recallstorm/rules/      evaluate_sku(...) exactly as in contract.py; HOLD_VERIFY when the label says only
                          "artificial color" or the text is unreadable; KEEP when out of scope
- recallstorm/allocate/   allocate_substitutes(...) exactly as in contract.py; never exceed stock
- recallstorm/plan/       join verdicts x facings into shelf_task, evidence, allocation, store_playbook records;
                          assign associates within shifts; every window ends before the deadline
- recallstorm/sim/        replay tasks into events.jsonl (MOVE, PULL, PLACE, DONE) with walking time
- recallstorm/__main__.py CLI: python -m recallstorm run --scenario ID --data DIR --out DIR
- tests/unit/ for each package
