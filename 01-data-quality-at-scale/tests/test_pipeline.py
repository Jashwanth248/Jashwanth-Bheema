import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from pipeline import run, validate


class PipelineTests(unittest.TestCase):
    def test_validation_collects_multiple_failures(self):
        errors = validate({"transaction_id": "", "partner_code": "NOPE", "amount": "-1", "received_at": "bad"}, set())
        self.assertEqual(set(errors), {"missing_transaction_id", "invalid_partner_code", "amount_must_be_positive", "invalid_received_at"})

    def test_run_quarantines_duplicate_and_invalid_rows(self):
        root = Path(__file__).parents[1]
        with tempfile.TemporaryDirectory() as directory:
            report = run(root / "data/sample_transactions.csv", Path(directory), date(2026, 2, 1))
        self.assertEqual(report["records_valid"], 2)
        self.assertEqual(report["records_quarantined"], 3)
        self.assertEqual(report["failure_counts"]["duplicate_record"], 1)
