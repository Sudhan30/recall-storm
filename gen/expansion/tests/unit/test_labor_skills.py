"""Unit tests for recallstorm.labor.skills."""
from datetime import datetime, timezone
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


def test_skills_functions():
    dt = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    assoc = Associate("A1", "WM1", "D01", False, dt, dt)
    assert skill_for_task(Action.PULL) == "SHELF_PULL"
    assert len(associate_skills(assoc)) == 4
    assert can_handle_action(assoc, Action.PLACE_SUB) is True
    sb = SkillBook()
    certify_associate(sb, "A1", "FORKLIFT")
    assert "FORKLIFT" in sb.certifications["A1"]
    assert skill_gaps([assoc], [Action.PULL, Action.TAG_FLASH]) == []
    assert skill_gaps([], [Action.PULL]) == ["SHELF_PULL"]
    assert "A1" in skill_matrix([assoc])
    assert len(train_plan(["SHELF_PULL"])) == 1
    assert skills_summary([assoc])["full_coverage"] is True
