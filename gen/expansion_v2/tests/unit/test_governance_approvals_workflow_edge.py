"""Edge case tests for recallstorm.governance.approvals_workflow."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.approvals_workflow import (
    enforce_dual_control_on_chainwide_pulls,
    track_approval_turnaround_bottlenecks,
)


def test_approvals_workflow_edge():
    with pytest.raises(DataValidationError):
        enforce_dual_control_on_chainwide_pulls("QA1", "QA1")
    with pytest.raises(DataValidationError):
        track_approval_turnaround_bottlenecks({})
