"""Property tests for recallstorm.ingest.cpsc."""
import random
from recallstorm.ingest.cpsc import cpsc_to_recall


def test_cpsc_to_recall_props():
    rng = random.Random(42)
    for i in range(25):
        num = f"26-{100 + i}"
        units = rng.randint(100, 50000)
        rec = cpsc_to_recall(
            {
                "RecallNumber": num,
                "Products": [{"Name": "Baby Bottle", "NumberOfUnits": str(units)}],
                "UPCs": [str(rng.randint(10**11, 10**12 - 1))],
            }
        )
        assert rec["recall_id"] == f"CPSC-{num}"
        assert rec["is_food_contact"] is True
