import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from monitor import fit, score


class MonitoringTests(unittest.TestCase):
    def test_extreme_record_is_flagged_with_contributions(self):
        reference = [{"record_id": str(index), "amount": value, "processing_minutes": 5} for index, value in enumerate((98, 99, 100, 101, 102))]
        result = score({"record_id": "outlier", "amount": 900, "processing_minutes": 5}, fit(reference))
        self.assertTrue(result["is_anomaly"])
        self.assertGreater(result["feature_contributions"]["amount"], 3.5)

    def test_fit_requires_sufficient_reference_data(self):
        with self.assertRaises(ValueError):
            fit([{"amount": 1, "processing_minutes": 1}] * 2)
