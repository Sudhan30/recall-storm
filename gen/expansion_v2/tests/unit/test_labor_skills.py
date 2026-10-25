"""Unit tests for recallstorm.labor.skills."""
from datetime import datetime
from contract import Action, Associate
from recallstorm.labor.skills import (
    SkillBook,
    associate_skills,
    can_handle_action,
    certify_associate,
    skill_for_task,
    skill_gaps,
    skill_matrix,
    skills_summary,
    train_plan,
)


def test_labor_skills():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    a = Associate("A1", "WM1", "D01", True, t0, t1)
    assert skill_for_task(Action.PULL) == "SHELF_PULL"
    assert "FLOATER_RAPID_RESPONSE" in associate_skills(a)
    assert can_handle_action(a, Action.PULL) is True
    sb = certify_associate("A1", "FORKLIFT")
    assert isinstance(sb, SkillBook) and "FORKLIFT" in sb.by_assoc["A1"]
    assert "A1" in skill_matrix([a])
    assert skill_gaps([a], [Action.PULL, Action.PLACE_SUB]) == []
    assert len(train_plan(["HAZMAT"])) == 1
    assert skills_summary([a])["floater_count"] == 1
