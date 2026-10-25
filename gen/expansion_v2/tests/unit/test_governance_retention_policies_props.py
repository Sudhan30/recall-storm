"""Property tests for recallstorm.governance.retention_policies."""
from recallstorm.governance.retention_policies import track_retention_expiration_disposition_dates


def test_litigation_hold_never_disposed():
    recs = [{"id": f"R{i}", "retain_until": "2020-01-01", "litigation_hold": True} for i in range(15)]
    assert track_retention_expiration_disposition_dates(recs, "2035-01-01") == []
