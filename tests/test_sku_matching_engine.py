"""
Unit tests for SKU Matching Engine
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

from agents.sku_matching_agent import SKUMatchingAgent


class TestSKUMatchingEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog_path = os.path.join(os.path.dirname(__file__), "..", "data", "sku_catalog.csv")
        cls.agent = SKUMatchingAgent(catalog_path=catalog_path)

    def test_catalog_loaded(self):
        self.assertGreater(len(self.agent.catalog_items), 50)

    def test_exact_brand_match_sunsilk(self):
        matches = self.agent.match_local("Sunsilk Black Shine Shampoo 180ml", top_k=1)
        self.assertTrue(len(matches) > 0)
        self.assertEqual(matches[0]["sku_id"], "HUL_SUN_001")
        self.assertGreater(matches[0]["confidence"], 0.70)

    def test_fuzzy_match_maggi(self):
        matches = self.agent.match_local("Maggi noodles 8-pack", top_k=1)
        self.assertTrue(len(matches) > 0)
        self.assertEqual(matches[0]["sku_id"], "NES_MAG_001")

    def test_fuzzy_match_surf_excel(self):
        matches = self.agent.match_local("Surf Excel Matic Top Load", top_k=1)
        self.assertTrue(len(matches) > 0)
        self.assertEqual(matches[0]["sku_id"], "HUL_SURF_001")


if __name__ == "__main__":
    unittest.main()
