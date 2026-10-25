"""Integration test 04: Store layout & facings -> Labor shifts & assignment -> Plan tasks & playbook."""
from datetime import datetime
from contract import load_datapack
from recallstorm.adjudicate import link_evidence
from recallstorm.core import is_before_deadline
from recallstorm.ingest import sample_datapack
from recallstorm.labor import assign_tasks, assignment_conflicts, store_minutes
from recallstorm.plan import build_playbook, build_shelf_tasks
from recallstorm.rules import evaluate_pack
from recallstorm.store import build_layout, facings_for_store


def test_flow_04_store_labor_and_playbook():
    pack = sample_datapack(load_datapack("data"), max_stores=2, seed=11)
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    decisions = evaluate_pack(pack, "CA", dl)
    rules_by_id = {r.rule_id: r for r in pack.rules}
    skus_by_id = {s.sku_id: s for s in pack.skus}
    ev_by_sku = link_evidence(decisions, rules_by_id, skus_by_id)

    store = pack.stores[0]
    st_facings = facings_for_store(pack.facings, store.store_id)
    layout = build_layout(store, st_facings)
    assert len(layout.locations) == len(st_facings)

    tasks = build_shelf_tasks(store, st_facings, decisions, ev_by_sku, {}, {}, pack.associates, dl)
    reassigned = assign_tasks(tasks, pack.associates, store, dl)
    assert assignment_conflicts(reassigned, dl) == []
    assert store_minutes(reassigned) >= 0.0

    pb = build_playbook(store, reassigned, [], [], dl)
    for w in pb["windows"]:
        assert is_before_deadline(w[1], dl) is True
