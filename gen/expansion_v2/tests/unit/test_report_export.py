"""Unit tests for recallstorm.report.export."""
from recallstorm.plan.assemble import assemble_plan
from recallstorm.report.export import (
    Exporter,
    export_csv,
    export_dc_packets,
    export_evidence,
    export_index,
    export_manifests,
    export_markdown,
    export_store_packets,
    export_zip,
)
from tests.unit.test_plan_assemble import _sample_pack


def test_report_export(tmp_path):
    pack = _sample_pack()
    sc = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    recs = assemble_plan(pack, sc)
    assert export_csv([{"a": 1, "b": 2}], str(tmp_path / "t.csv")) == 1
    assert "# Recall Storm" in export_markdown(recs, str(tmp_path / "summary.md"))
    assert export_evidence(recs, str(tmp_path / "ev.jsonl")) == 1
    assert export_manifests(recs, str(tmp_path / "mnf.jsonl")) == 0
    st_p = export_store_packets(recs, str(tmp_path / "stores"))
    assert "WM1563" in st_p
    dc_p = export_dc_packets(recs, str(tmp_path / "dcs"))
    assert "DC_CENTRAL" in dc_p
    assert export_index(recs)["total_records"] == len(recs)
    zpath = export_zip(recs, str(tmp_path / "bundle.zip"))
    assert zpath.endswith("bundle.zip")
    assert Exporter(str(tmp_path)).out_dir == str(tmp_path)
