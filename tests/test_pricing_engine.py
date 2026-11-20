"""
Unit tests for FMCG Commercial Pricing Engine
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

from agents.pricing_agent import PricingAgent


class TestPricingEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rules_path = os.path.join(os.path.dirname(__file__), "..", "data", "pricing_rules.json")
        cls.agent = PricingAgent(rules_path=rules_path)

    def test_volume_discount_brackets(self):
        self.assertEqual(self.agent.get_volume_discount_pct(20), 0.0)
        self.assertAlmostEqual(self.agent.get_volume_discount_pct(100), 3.0)
        self.assertAlmostEqual(self.agent.get_volume_discount_pct(250), 6.5)
        self.assertAlmostEqual(self.agent.get_volume_discount_pct(750), 10.0)
        self.assertAlmostEqual(self.agent.get_volume_discount_pct(1500), 14.0)

    def test_category_gst_slabs(self):
        self.assertEqual(self.agent.get_gst_rate("Dairy & Staples"), 5.0)
        self.assertEqual(self.agent.get_gst_rate("Beverages"), 12.0)
        self.assertEqual(self.agent.get_gst_rate("Home Care"), 18.0)
        self.assertEqual(self.agent.get_gst_rate("Personal Care"), 18.0)

    def test_commercial_calculation_accuracy(self):
        rfp_data = {"line_items": []}
        sku_data = {
            "matches": [
                {
                    "matched_sku_name": "Dove Shampoo 340ml",
                    "matched_sku_code": "HUL_DOVE_001",
                    "category": "Personal Care",
                    "quantity": 100,
                    "base_cost": 250.0,
                    "gst_pct": 18.0
                }
            ]
        }
        res = self.agent.process(rfp_data, sku_data)
        self.assertIn("pricing_table", res)
        self.assertIn("summary", res)

        item = res["pricing_table"][0]
        # Base: 250, 100 qty -> 3% discount = 7.50, net rate = 242.50
        self.assertEqual(item["qty"], 100)
        self.assertAlmostEqual(item["discount_pct"], 3.0)
        self.assertAlmostEqual(item["net_unit_price"], 242.50)
        self.assertAlmostEqual(item["line_taxable_price"], 24250.0)
        self.assertAlmostEqual(item["gst_amount"], 4365.0)  # 18% of 24250
        self.assertAlmostEqual(item["line_total_price"], 28615.0)


if __name__ == "__main__":
    unittest.main()
