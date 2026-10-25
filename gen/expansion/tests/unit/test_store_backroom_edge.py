"""Edge tests for recallstorm.store.backroom."""
import pytest
from recallstorm.store.backroom import (
    backroom_locations,
    backroom_pull_task,
    staging_area,
)


def test_backroom_edge():
    with pytest.raises(ValueError):
        staging_area("")
    with pytest.raises(ValueError):
        backroom_locations("")
    with pytest.raises(ValueError):
        backroom_pull_task("WM1", "S1", 0)
