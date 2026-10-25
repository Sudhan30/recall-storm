"""Integration test 11: Full CLI run -> read plan.jsonl & events.jsonl -> Reports, exports, and checks."""
from contract import load_datapack
from recallstorm.cli import main
from recallstorm.core import load_config, read_jsonl
from recallstorm.plan import validate_plan_refs
from recallstorm.report import (
    drill_summary,
    export_dc_packets,
    export_store_packets,
    export_zip,
    run_all_checks,
)
from recallstorm.rules import decision_counts
from recallstorm.sim import replay_summary


def test_flow_11_cli_to_reports(tmp_path):
    out_dir = tmp_path / "cli_run"
    rc = main(["run", "--scenario", "ca_red3", "--data", "data", "--out", str(out_dir)])
    assert rc == 0

    cfg = load_config("data/scenario_ca_red3.json")
    pack = load_datapack("data")
    plan_recs = read_jsonl(out_dir / "plan.jsonl")
    event_recs = read_jsonl(out_dir / "events.jsonl")

    assert validate_plan_refs(plan_recs) == []
    check_rep = run_all_checks(plan_recs, pack, cfg.deadline)
    assert check_rep.passed is True

    summary = drill_summary(plan_recs)
    assert summary["stores"] == len(pack.stores)
    assert summary["verdicts"]["PULL"] > 0
    assert summary["manifests"] > 0

    ev_sum = replay_summary(event_recs)
    assert ev_sum["by_kind"]["DONE"] > 0
    assert decision_counts([])["PULL"] == 0

    st_packets = export_store_packets(plan_recs, tmp_path / "packets/stores")
    dc_packets = export_dc_packets(plan_recs, tmp_path / "packets/dcs")
    zpath = export_zip(plan_recs, tmp_path / "packets/bundle.zip")
    assert len(st_packets) == len(pack.stores)
    assert len(dc_packets) == 3
    assert zpath.endswith("bundle.zip")
