"""Edge tests for recallstorm.plan.deadline."""
import pytest
from recallstorm.plan.deadline import (
    deadline_slack_minutes,
    window_before_deadline,
)


def test_deadline_edge():
    assert window_before_deadline(["only_one"], "2027-01-01T00:00:00-08:00") is False
    with pytest.raises(ValueError):
        deadline_slack_minutes(["only_one"], "2027-01-01T00:00:00-08:00")
