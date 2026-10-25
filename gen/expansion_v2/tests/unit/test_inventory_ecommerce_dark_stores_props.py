"""Property tests for recallstorm.inventory.ecommerce_dark_stores."""
import random
from recallstorm.inventory.ecommerce_dark_stores import process_automatic_digital_refunds


def test_digital_refunds_linear_props():
    rng = random.Random(42)
    for n in range(1, 20):
        price = round(rng.uniform(1.0, 25.0), 2)
        orders = [f"O{i}" for i in range(n)]
        assert process_automatic_digital_refunds(orders, price) == round(n * price, 2)
