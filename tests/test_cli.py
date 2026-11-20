"""
Unit tests for the FMCG RFP CLI tool.
"""

import os
import subprocess
import sys
import unittest


class TestFMCGCLI(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.cli_path = os.path.join(self.root_dir, "cli.py")
        self.sample_order = os.path.join(self.root_dir, "data", "sample_supermarket_monthly_restock.txt")

    def test_cli_help(self):
        result = subprocess.run([sys.executable, self.cli_path, "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("FMCG Intelligent RFP Automation CLI", result.stdout)
        self.assertIn("process", result.stdout)
        self.assertIn("catalog", result.stdout)

    def test_cli_catalog_search(self):
        result = subprocess.run(
            [sys.executable, self.cli_path, "catalog", "-q", "soap", "-n", "5"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Showing top", result.stdout)
        self.assertIn("Personal Care", result.stdout)

    def test_cli_process_mock(self):
        result = subprocess.run(
            [sys.executable, self.cli_path, "process", self.sample_order, "--mock"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("RFP Processing Complete", result.stdout)
        self.assertIn("total_cost", result.stdout)

    def test_cli_verify(self):
        result = subprocess.run(
            [sys.executable, self.cli_path, "verify"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("ALL 9 SYSTEM CHECKS PASSED", result.stdout)


if __name__ == "__main__":
    unittest.main()
