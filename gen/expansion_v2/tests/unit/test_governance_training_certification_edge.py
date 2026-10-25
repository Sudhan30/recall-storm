"""Edge case tests for recallstorm.governance.training_certification."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.training_certification import (
    assign_mandatory_recall_drill_microlearning,
    score_simulated_drill_assessment_quizzes,
)


def test_training_certification_edge():
    with pytest.raises(DataValidationError):
        assign_mandatory_recall_drill_microlearning([])
    with pytest.raises(DataValidationError):
        score_simulated_drill_assessment_quizzes(12, 10)
