"""
Integration test suite for FastAPI backend endpoints using Starlette TestClient
"""

import sys
import os
import unittest
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent / "rfp-automation"))

from fastapi.testclient import TestClient
from server import app


class TestFastAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertGreater(data["catalog_items_loaded"], 50)

    def test_catalog_listing(self):
        resp = self.client.get("/api/catalog")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertGreater(data["total"], 50)
        self.assertIn("Personal Care", data["categories"])

    def test_catalog_search_filtering(self):
        resp = self.client.get("/api/catalog?q=Dove")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(any("dove" in item["name"].lower() for item in data["items"]))

    def test_catalog_item_detail(self):
        resp = self.client.get("/api/catalog/HUL_DOVE_001")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["sku_id"], "HUL_DOVE_001")
        self.assertIn("Dove", data["name"])

    def test_pricing_simulation(self):
        payload = {
            "margin_pct": 20.0,
            "items": [
                {
                    "sku_name": "Sunsilk Black Shine Shampoo 180ml",
                    "quantity": 100,
                    "base_cost": 130.0,
                    "category": "Personal Care",
                    "gst_pct": 18.0
                }
            ]
        }
        resp = self.client.post("/api/pricing/simulate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["grand_total"], 0)
        self.assertEqual(data["margin_pct"], 20.0)

    def test_compliance_validation(self):
        payload = {
            "client_name": "Reliance Retail",
            "deadline": "5 business days",
            "pricing_table": [
                {"sku_name": "Surf Excel Matic 2kg", "qty": 100, "category": "Home Care", "net_unit_price": 450.0}
            ],
            "grand_total": 45000.0
        }
        resp = self.client.post("/api/compliance/validate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["is_compliant"])
        self.assertEqual(data["compliance_score"], 100)

    def test_analytics_kpi(self):
        resp = self.client.get("/api/analytics")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["pipeline_value_inr"], 0)
        self.assertIn("category_distribution", data)

    def test_history_list(self):
        resp = self.client.get("/api/history?limit=5")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)


if __name__ == "__main__":
    unittest.main()
