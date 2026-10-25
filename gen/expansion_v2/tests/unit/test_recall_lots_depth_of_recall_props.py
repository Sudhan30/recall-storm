"""Property tests for recallstorm.recall_lots.depth_of_recall."""
from recallstorm.recall_lots.depth_of_recall import generate_depth_execution_matrix


def test_depth_urgency_ordering():
    m1 = generate_depth_execution_matrix("Class I")
    m2 = generate_depth_execution_matrix("Class II")
    m3 = generate_depth_execution_matrix("Class III")
    assert m1["urgency"] < m2["urgency"] < m3["urgency"]
