import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from agent import build_prompt, investigate


class AgentTests(unittest.TestCase):
    def test_known_rule_returns_auditable_recommendation(self):
        result = investigate({"incident_id": "x", "rule": "duplicate_record", "evidence": [{"id": "e-1", "fact": "repeated fingerprint"}]})
        self.assertEqual(result["status"], "investigated")
        self.assertTrue(result["requires_human_approval"])
        self.assertEqual(result["evidence_ids"], ["e-1"])

    def test_unknown_rule_escalates(self):
        self.assertEqual(investigate({"rule": "new_rule"})["status"], "escalate")

    def test_prompt_keeps_evidence_as_context(self):
        self.assertIn("[e-1]", build_prompt({"rule": "duplicate_record", "evidence": [{"id": "e-1", "fact": "fact"}]}))
