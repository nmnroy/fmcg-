"""
Unit tests for Currency Converter and Webhook Dispatcher utilities.
"""

import unittest
from unittest.mock import patch, MagicMock
from utils.currency_converter import convert_currency, format_currency_amount, get_supported_currencies
from utils.webhook_dispatcher import prepare_webhook_payload, dispatch_webhook


class TestCurrencyAndWebhooks(unittest.TestCase):
    def test_currency_conversion(self):
        inr = 10000.0
        usd = convert_currency(inr, "USD")
        self.assertEqual(usd, 120.0)
        eur = convert_currency(inr, "EUR")
        self.assertEqual(eur, 110.0)
        self.assertIn("USD", get_supported_currencies())

    def test_currency_formatting(self):
        formatted_inr = format_currency_amount(15500.5, "INR")
        self.assertIn("15,500.50", formatted_inr)
        formatted_usd = format_currency_amount(250.75, "USD")
        self.assertEqual(formatted_usd, "$250.75")

    def test_webhook_payload_preparation(self):
        rfp_mock = {
            "rfp_id": "RFP-TEST-001",
            "customer_name": "Test Supermarket",
            "total_cost": 45000.0,
            "line_items": [{"id": "1"}, {"id": "2"}],
            "status": "SUCCESS"
        }
        payload = prepare_webhook_payload(rfp_mock)
        self.assertEqual(payload["event"], "rfp.completed")
        self.assertEqual(payload["rfp_id"], "RFP-TEST-001")
        self.assertEqual(payload["line_items_count"], 2)

    def test_webhook_dispatch_skipped(self):
        res = dispatch_webhook("", {})
        self.assertEqual(res["status"], "skipped")

    @patch("urllib.request.urlopen")
    def test_webhook_dispatch_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = dispatch_webhook("http://example.com/webhook", {"test": "data"})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["status_code"], 200)


if __name__ == "__main__":
    unittest.main()
