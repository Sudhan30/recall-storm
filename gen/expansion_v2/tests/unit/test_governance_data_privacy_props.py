"""Property tests for recallstorm.governance.data_privacy."""
import random
from recallstorm.governance.data_privacy import scrub_credit_card_pans_from_pos_scan_logs


def test_pan_scrubbing_removes_all_16_digit_cards():
    rng = random.Random(42)
    for _ in range(20):
        pan = "-".join(f"{rng.randint(1000, 9999)}" for _ in range(4))
        s = scrub_credit_card_pans_from_pos_scan_logs(f"TX {pan} DONE")
        assert pan not in s and "[REDACTED_PAN]" in s
