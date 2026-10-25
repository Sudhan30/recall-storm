"""Unit tests for recallstorm.report.export."""
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


def test_export_artifacts(tmp_path):
    exp = Exporter(str(tmp_path))
    assert exp.out_dir == str(tmp_path)
    recs = [
        {"type": "run", "run_id": "RUN-1", "scenario_id": "ca_red3"},
        {"type": "evidence", "evidence_id": "EVD-1", "sku_id": "S1"},
        {"type": "shelf_task", "task_id": "T1", "store_id": "WM1", "action": "PULL"},
        {"type": "allocation", "alloc_id": "ALC-1", "dc_id": "DC1", "store_id": "WM1"},
        {"type": "route_manifest", "manifest_id": "MNF-1", "dc_id": "DC1", "truck_id": "T0"},
    ]
    assert export_csv(recs, "shelf_task", tmp_path / "tasks.csv") == 1
    assert export_markdown(recs, tmp_path / "summary.md") > 10
    st_files = export_store_packets(recs, tmp_path / "stores")
    assert len(st_files) == 1
    dc_files = export_dc_packets(recs, tmp_path / "dcs")
    assert len(dc_files) == 1
    assert export_evidence(recs, tmp_path / "ev.jsonl") == 1
    assert export_manifests(recs, tmp_path / "mnf.jsonl") == 1
    zp = export_zip(recs, tmp_path / "bundle.zip")
    assert zp.endswith("bundle.zip")
    assert export_index(st_files + dc_files)["file_count"] == 2
