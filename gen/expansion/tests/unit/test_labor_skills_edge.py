"""Edge tests for recallstorm.labor.skills."""
import pytest
from recallstorm.labor.skills import (
    SkillBook,
    certify_associate,
    skill_for_task,
)


def test_skills_edge():
    with pytest.raises(ValueError):
        skill_for_task("INVALID_ACTION")
    with pytest.raises(ValueError):
        certify_associate(SkillBook(), "", "SKILL")
