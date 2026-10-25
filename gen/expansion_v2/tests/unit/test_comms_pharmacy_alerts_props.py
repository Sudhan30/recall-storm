"""Property tests for recallstorm.comms.pharmacy_alerts."""
from recallstorm.comms.pharmacy_alerts import match_recalled_ndc_to_dispensing_log


def test_ndc_matching_exact_props():
    dispenses = [{"rx_id": f"RX{i}", "ndc": f"0000-1111-{i:02d}"} for i in range(15)]
    assert match_recalled_ndc_to_dispensing_log(dispenses, "0000-1111-05") == ["RX5"]
