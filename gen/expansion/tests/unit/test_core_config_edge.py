"""Edge tests for recallstorm.core.config."""
import pytest
from recallstorm.core.config import (
    Config,
    get_deadline,
    get_scenario_path,
    load_config,
    merge_overrides,
    validate_config,
)
from recallstorm.core.errors import ScenarioError


def test_validate_invalid_config():
    bad = Config(
        scenario_id="",
        state="CALIFORNIA",
        rule_ids=(),
        as_of="2027-01-02T00:00:00-08:00",
        deadline="2027-01-01T00:00:00-08:00",
    )
    issues = validate_config(bad)
    assert len(issues) >= 4


def test_missing_or_corrupt_scenario(tmp_path):
    with pytest.raises(ScenarioError):
        load_config(tmp_path / "missing.json")
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not json", encoding="utf-8")
    with pytest.raises(ScenarioError):
        load_config(bad_file)


def test_edge_errors():
    with pytest.raises(ScenarioError):
        get_scenario_path("data", "")
    with pytest.raises(ScenarioError):
        get_deadline(Config(deadline="not-a-date"))
    with pytest.raises(TypeError):
        merge_overrides("not_cfg", {})  # type: ignore[arg-type]
