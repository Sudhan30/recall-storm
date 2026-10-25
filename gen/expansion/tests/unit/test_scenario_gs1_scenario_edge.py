"""Edge tests for recallstorm.scenario_gs1.scenario."""
import pytest
from recallstorm.scenario_gs1.scenario import load_gs1_scenario


def test_scenario_gs1_edge():
    s = load_gs1_scenario({"scenario_id": "custom", "lot_codes": ["L1"]})
    assert s.scenario_id == "custom"
    with pytest.raises(TypeError):
        load_gs1_scenario(123)  # type: ignore[arg-type]
