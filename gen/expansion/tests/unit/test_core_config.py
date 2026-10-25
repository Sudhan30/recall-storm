"""Unit tests for recallstorm.core.config."""
import json
from datetime import datetime
from recallstorm.core.config import (
    Config,
    config_from_env,
    config_to_dict,
    default_config,
    get_deadline,
    get_scenario_path,
    load_config,
    merge_overrides,
    validate_config,
)


def test_default_and_validate():
    cfg = default_config()
    assert isinstance(cfg, Config)
    assert validate_config(cfg) == []
    assert isinstance(get_deadline(cfg), datetime)


def test_load_config_and_path(tmp_path):
    p = tmp_path / "scenario_ca_red3.json"
    p.write_text(
        json.dumps(
            {
                "scenario_id": "ca_red3",
                "state": "CA",
                "rule_ids": ["CA_AB418_RED3"],
                "as_of": "2026-12-30T18:00:00-08:00",
                "deadline": "2027-01-01T00:00:00-08:00",
                "note": "test note",
            }
        ),
        encoding="utf-8",
    )
    resolved = get_scenario_path(tmp_path, "ca_red3")
    assert resolved == str(p)
    cfg = load_config(resolved)
    assert cfg.scenario_id == "ca_red3"
    assert cfg.extra.get("note") == "test note"


def test_merge_env_and_to_dict():
    cfg = config_from_env("RS_", {"RS_SCENARIO_ID": "test_scen", "RS_STATE": "MN", "RS_RULE_IDS": "R1,R2"})
    assert cfg.scenario_id == "test_scen"
    assert cfg.state == "MN"
    assert cfg.rule_ids == ("R1", "R2")
    merged = merge_overrides(cfg, {"out_dir": "out/custom"})
    d = config_to_dict(merged)
    assert d["out_dir"] == "out/custom"
