import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from data_sentinel import clean, cosine_similarity, schema_agent, validate


class DataSentinelTests(unittest.TestCase):
    def test_semantic_schema_mapping(self):
        mapping = schema_agent(["hours_per_week"])[0]
        self.assertEqual(mapping["canonical_field"], "hours_per_week")
        self.assertEqual(mapping["confidence"], 1.0)
        self.assertGreater(cosine_similarity("weekly hours", "hours per week"), 0.3)

    def test_cleaning_and_validation(self):
        value, confidence, action = clean(" ? ")
        self.assertIsNone(value)
        self.assertEqual(confidence, 1.0)
        self.assertEqual(action, "normalized_missing_marker")
        failures = validate({"age": "-1", "workclass": "Private", "education_num": "9", "capital_gain": "0", "hours_per_week": "40", "income": "invalid"})
        self.assertIn("negative_age", failures)
        self.assertIn("invalid_income_label", failures)


if __name__ == "__main__":
    unittest.main()
