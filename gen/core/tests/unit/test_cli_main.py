"""Tests for recallstorm.__main__ CLI."""
from __future__ import annotations

import json
from pathlib import Path
import pytest
from recallstorm.__main__ import main


def test_cli_run_end_to_end(tmp_path: Path) -> None:
    data_dir = Path("data")
    if not data_dir.exists() or not (data_dir / "scenario_ca_red3.json").exists():
        pytest.skip("Repository data/ directory not present in test environment")

    out_dir = tmp_path / "out_ca_red3"
    rc = main(["run", "--scenario", "ca_red3", "--data", str(data_dir), "--out", str(out_dir)])
    assert rc == 0

    plan_path = out_dir / "plan.jsonl"
    events_path = out_dir / "events.jsonl"
    assert plan_path.exists()
    assert events_path.exists()

    plan_lines = [json.loads(line) for line in plan_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    event_lines = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert len(plan_lines) > 0
    assert len(event_lines) > 0
    assert plan_lines[0]["type"] == "run"
    assert plan_lines[0]["scenario_id"] == "ca_red3"
