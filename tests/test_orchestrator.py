"""
Unit tests for Pipeline Orchestrator
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

from agents.orchestrator import run_sequential_pipeline


class TestOrchestrator(unittest.TestCase):
    def test_mock_pipeline_execution(self):
        result = run_sequential_pipeline("Order 100 bottles of shampoo", use_mock=True)
        self.assertEqual(result["status"], "COMPLETED")
        self.assertIn("rfp_id", result)
        self.assertIn("pricing", result)
        self.assertIn("compliance", result)
        self.assertIn("timing", result)
        self.assertTrue(result["timing"]["total_pipeline_seconds"] >= 0)


if __name__ == "__main__":
    unittest.main()
