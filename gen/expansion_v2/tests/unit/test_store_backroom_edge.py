"""Edge case tests for recallstorm.store.backroom."""
import pytest
from recallstorm.store.backroom import backroom_capacity_left, backroom_pull_task, stage_returns, staging_area


def test_store_backroom_edge():
    with pytest.raises(ValueError):
        staging_area("")
    with pytest.raises(ValueError):
        backroom_pull_task("WM1", "S1", -1)
    with pytest.raises(ValueError):
        stage_returns("WM1", -5)
    assert backroom_capacity_left(600, 500) == 0
