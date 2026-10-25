"""Edge tests for recallstorm.sim.disruptions."""
import pytest
from recallstorm.sim.disruptions import (
    absent_associate,
    inject_disruption,
    stockout_event,
    truck_delay,
)


def test_disruptions_edge():
    with pytest.raises(ValueError):
        absent_associate("")
    with pytest.raises(ValueError):
        truck_delay("T0", 0)
    with pytest.raises(ValueError):
        stockout_event("", "S1")
    with pytest.raises(TypeError):
        inject_disruption("not_pack", "not_dis")  # type: ignore[arg-type]
