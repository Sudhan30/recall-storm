"""Property tests for recallstorm.labor.skills."""
from datetime import datetime
from contract import Action, Associate
from recallstorm.labor.skills import can_handle_action


def test_every_associate_can_handle_all_standard_actions():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    a = Associate("A1", "WM1", "D01", False, t0, t1)
    for act in Action:
        assert can_handle_action(a, act) is True
