"""Property tests for recallstorm.governance.training_certification."""
from recallstorm.governance.training_certification import score_simulated_drill_assessment_quizzes


def test_quiz_pass_threshold_props():
    for c in range(0, 11):
        res = score_simulated_drill_assessment_quizzes(c, 10)
        assert res["passed"] == (c >= 8)
