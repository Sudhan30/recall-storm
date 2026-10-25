"""Edge case tests for recallstorm.core.config."""
import pytest
from recallstorm.core.config import (
    Config,
    get_deadline,
    get_scenario_path,
    load_config,
    validate_config,
)
from recallstorm.core.errors import ScenarioError


def test_config_invalid_inputs(tmp_path):
    with pytest.raises(ScenarioError):
        load_config(str(tmp_path / "missing.json"))
    bad = tmp_path / "bad.json"
    bad.write_text("{not_json", encoding="utf-8")
    with pytest.raises(ScenarioError):
        load_config(str(bad))

    empty_cfg = Config(scenario_id="", state="", data_dir="", out_dir="", deadline="", rule_ids=())
    issues = validate_config(empty_cfg)
    assert len(issues) == 6
    with pytest.raises(ScenarioError):
        get_deadline(empty_cfg)
    with pytest.raises(ScenarioError):
        get_scenario_path("", "ca_red3")
