"""Unit tests for recallstorm.core.config."""
import json
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


def test_config_lifecycle(tmp_path, monkeypatch):
    cfg = default_config()
    assert isinstance(cfg, Config)
    assert validate_config(cfg) == []
    assert get_deadline(cfg) == "2027-01-01T00:00:00-08:00"
    assert get_scenario_path("data", "ca_red3").endswith("scenario_ca_red3.json")

    sc_file = tmp_path / "scenario_test.json"
    sc_file.write_text(
        json.dumps({"scenario_id": "test", "state": "NY", "rule_ids": ["R1"]}),
        encoding="utf-8",
    )
    loaded = load_config(str(sc_file))
    assert loaded.scenario_id == "test"
    assert loaded.state == "NY"
    assert loaded.rule_ids == ("R1",)

    merged = merge_overrides(loaded, {"seed": 99})
    assert merged.seed == 99
    as_dict = config_to_dict(merged)
    assert as_dict["seed"] == 99

    monkeypatch.setenv("RECALLSTORM_STATE", "MN")
    env_cfg = config_from_env()
    assert env_cfg.state == "MN"
