"""
Unit tests for FMCG Order Compliance & Guardrails Checker
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

from utils.compliance_checker import validate_order_compliance


class TestComplianceChecker(unittest.TestCase):
    def test_compliant_large_order(self):
        rfp_data = {"client_name": "Supermarket Ltd", "deadline": "7 business days"}
        pricing_data = {
            "pricing_table": [
                {"sku_name": "Dove Shampoo 340ml", "qty": 50, "category": "Personal Care", "net_unit_price": 200.0},
                {"sku_name": "Surf Excel 2kg", "qty": 40, "category": "Home Care", "net_unit_price": 450.0}
            ],
            "summary": {"grand_total": 35000.0}
        }
        res = validate_order_compliance(rfp_data, pricing_data)
        self.assertTrue(res["is_compliant"])
        self.assertEqual(res["compliance_score"], 100)
        self.assertEqual(len(res["violations"]), 0)
        self.assertEqual(len(res["warnings"]), 0)

    def test_low_order_value_warning(self):
        rfp_data = {"client_name": "Small Corner Store"}
        pricing_data = {
            "pricing_table": [
                {"sku_name": "Vim Bar 500g", "qty": 10, "category": "Home Care", "net_unit_price": 40.0}
            ],
            "summary": {"grand_total": 450.0}
        }
        res = validate_order_compliance(rfp_data, pricing_data)
        self.assertTrue(any("freight-free threshold" in w for w in res["warnings"]))
        self.assertLess(res["compliance_score"], 100)

    def test_cold_chain_detection(self):
        rfp_data = {"client_name": "Grocery Express"}
        pricing_data = {
            "pricing_table": [
                {"sku_name": "Amul Table Butter 500g", "qty": 30, "category": "Dairy & Staples", "net_unit_price": 260.0}
            ],
            "summary": {"grand_total": 7800.0}
        }
        res = validate_order_compliance(rfp_data, pricing_data)
        self.assertTrue(any("Temperature-Controlled" in tag for tag in res["special_handling_tags"]))


if __name__ == "__main__":
    unittest.main()
