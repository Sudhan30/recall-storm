"""Property tests for recallstorm.comms.call_center_scripts."""
from recallstorm.comms.call_center_scripts import route_adverse_event_to_nurse_line


def test_symptom_routing_partition_props():
    assert route_adverse_event_to_nurse_line("T1", True)["queue"] == "NURSE_TOXICOLOGY_LINE"
    assert route_adverse_event_to_nurse_line("T1", False)["queue"] == "GENERAL_REFUND_QUEUE"
