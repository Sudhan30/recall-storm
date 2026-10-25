"""Property tests for recallstorm.governance.access_logs."""
from recallstorm.governance.access_logs import revoke_terminated_associate_drill_credentials


def test_revoke_credentials_disjoint_from_active():
    active = {f"A{i}" for i in range(10)}
    holders = {f"A{i}" for i in range(5, 15)}
    revoked = set(revoke_terminated_associate_drill_credentials(active, holders))
    assert revoked.isdisjoint(active)
    assert len(revoked) == 5
