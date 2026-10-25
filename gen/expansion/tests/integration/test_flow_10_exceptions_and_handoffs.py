"""Integration test 10: StoreNotes -> Exceptions -> Floater dispatches -> Handoffs -> Invariant checks."""
from contract import load_datapack
from recallstorm.allocate import allocate_substitutes
from recallstorm.core import validate_id_prefix
from recallstorm.ingest import sample_datapack
from recallstorm.labor import dispatch_floater, one_store_per_window
from recallstorm.plan import assemble_plan, build_handoffs, exception_records
from recallstorm.report import run_all_checks
from recallstorm.route import manifest_to_record, pack_returns
from recallstorm.store import exception_kind_for_text


def test_flow_10_exceptions_and_handoffs():
    pack = sample_datapack(load_datapack("data"), max_stores=4, seed=42)
    for n in pack.notes:
        k = exception_kind_for_text(n.text)
        assert k is not None

    trucks_by_id = {t.truck_id: t for t in pack.trucks}

    def _packer(pulled_cases, skus, trucks, stores):
        mnfs = pack_returns(pulled_cases, skus, trucks, stores)
        return mnfs, [manifest_to_record(mnf, trucks_by_id[mnf.truck_id]) for mnf in mnfs]

    scen = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    records = assemble_plan(pack, scen, manifest_packer=_packer)
    rep = run_all_checks(records, pack, scen["deadline"])
    assert rep.passed is True

    excs = [r for r in records if r["type"] == "exception"]
    for e in excs:
        assert validate_id_prefix(e["exc_id"], "EXC")

    floaters = [a for a in pack.associates if a.is_floater]
    if floaters:
        d = dispatch_floater(floaters[0], pack.stores[0].store_id, ["2026-12-30T22:00:00-08:00", "2026-12-31T02:00:00-08:00"], ["TSK-1"])
        assert one_store_per_window([d]) is True
        h = build_handoffs(allocate_substitutes({}, pack.dc_stock, pack.stores), [], [d])
        assert len(h) == 1 and validate_id_prefix(h[0]["handoff_id"], "HND")
    assert len(exception_records(pack.notes[:2], {})) == 2
