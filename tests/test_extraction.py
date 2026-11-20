"""
Unit tests for RFP Text Extraction & Order Parsing
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

class TestExtraction(unittest.TestCase):
    def test_mock_intake_extraction(self):
        from agents.mock_agents import MockIntakeAgent
        agent = MockIntakeAgent()
        result = agent.process("Sample Order Text")
        
        self.assertIn("line_items", result)
        self.assertTrue(len(result["line_items"]) >= 4)
        self.assertEqual(result["client_name"], "Simulated Client Ltd")
        self.assertTrue(result["is_relevant"])

    def test_line_item_structure(self):
        from agents.mock_agents import MockIntakeAgent
        agent = MockIntakeAgent()
        result = agent.process("Sample Order Text")
        item = result["line_items"][0]
        
        self.assertIn("description", item)
        self.assertIn("quantity", item)
        self.assertGreater(item["quantity"], 0)


if __name__ == "__main__":
    unittest.main()
