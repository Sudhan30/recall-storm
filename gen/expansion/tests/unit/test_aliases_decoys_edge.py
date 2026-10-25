"""Edge tests for recallstorm.aliases.decoys."""
import pytest
from recallstorm.aliases.decoys import (
    classify_red_mention,
    is_quantity_phrase,
    is_red40,
    near_miss_report,
)


def test_decoys_edge():
    assert classify_red_mention("3 RED BELL PEPPERS") == "NONE"
    with pytest.raises(TypeError):
        is_red40(None, 0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        is_quantity_phrase(None, 0, 1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        near_miss_report(123)  # type: ignore[arg-type]
