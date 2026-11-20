"""
Unit tests for the FMCG Python SDK Client.
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import json
from sdk.fmcg_client import FMCGClient


class TestFMCGClient(unittest.TestCase):
    def setUp(self):
        self.client = FMCGClient(base_url="http://mock-fmcg-server:8000")

    @patch("urllib.request.urlopen")
    def test_check_health(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status": "healthy", "catalog_size": 101}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.check_health()
        self.assertEqual(res.get("status"), "healthy")
        self.assertEqual(res.get("catalog_size"), 101)

    @patch("urllib.request.urlopen")
    def test_search_catalog(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "total_matches": 1,
            "items": [{"sku_id": "SKU-BEV-001", "sku_name": "Premium Tea 500g"}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.search_catalog(query="Tea")
        self.assertEqual(res.get("total_matches"), 1)
        self.assertEqual(res["items"][0]["sku_id"], "SKU-BEV-001")

    @patch("urllib.request.urlopen")
    def test_simulate_pricing(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "sku_id": "SKU-STA-001",
            "quantity": 100,
            "final_payable_inr": 8500.0,
            "gst_amount": 425.0
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = self.client.simulate_pricing("SKU-STA-001", 100)
        self.assertEqual(res["final_payable_inr"], 8500.0)


if __name__ == "__main__":
    unittest.main()
