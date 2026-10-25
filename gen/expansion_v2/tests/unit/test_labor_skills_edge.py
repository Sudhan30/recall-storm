"""Edge case tests for recallstorm.labor.skills."""
from contract import Action
from recallstorm.labor.skills import skill_gaps, skills_summary


def test_labor_skills_edge():
    assert skill_gaps([], [Action.PULL]) == ["SHELF_PULL"]
    assert skills_summary([])["associate_count"] == 0
