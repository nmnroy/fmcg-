import time

class MockIntakeAgent:
    def process(self, *args, **kwargs):
        time.sleep(1) # Simulate processing
        return {
            "client_name": "Simulated Client Ltd",
            "order_date": "2025-12-25",
            "line_items": [
                {"id": "1", "description": "Sunsilk Black Shine Shampoo (180ml)", "quantity": 100, "unit": "units"},
                {"id": "2", "description": "Dove Intense Repair (340ml)", "quantity": 50, "unit": "units"},
                {"id": "3", "description": "Vim Liquid Gel (750ml)", "quantity": 200, "unit": "bottles"},
                {"id": "4", "description": "Surf Excel Matic (2kg)", "quantity": 20, "unit": "packs"}
            ],
            "is_relevant": True
        }

class MockSKUMatchingAgent:
    def process(self, rfp_data, *args, **kwargs):
        time.sleep(1)
        return {
            "matches": [
                {
                    "original_desc": "Sunsilk Black Shine Shampoo (180ml)",
                    "matched_sku_name": "Sunsilk Black Shine Shampoo (180ml)",
                    "match_confidence_score": 0.95,
                    "reason": "Exact match found in catalog",
                    "is_ambiguous": False
                },
                {
                    "original_desc": "Dove Intense Repair (340ml)",
                    "matched_sku_name": "Dove Intense Repair Shampoo (340ml)",
                    "match_confidence_score": 0.92,
                    "reason": "High confidence variant match",
                    "is_ambiguous": False
                },
                {
                    "original_desc": "Vim Liquid Gel (750ml)",
                    "matched_sku_name": "Vim Liquid Gel (750ml)",
                    "match_confidence_score": 0.98,
                    "reason": "Exact size and brand match",
                    "is_ambiguous": False
                },
                 {
                    "original_desc": "Surf Excel Matic (2kg)",
                    "matched_sku_name": "Surf Excel Matic Top Load (2kg)",
                    "match_confidence_score": 0.88,
                    "reason": "Variant inferred as Top Load",
                    "is_ambiguous": True
                }
            ]
        }

class MockPricingAgent:
    def process(self, *args, **kwargs):
        time.sleep(1)
        return {
            "pricing_table": [
                {"sku_name": "Sunsilk Black Shine Shampoo (180ml)", "qty": 100, "net_unit_price": 120, "line_total_price": 12000},
                {"sku_name": "Dove Intense Repair Shampoo (340ml)", "qty": 50, "net_unit_price": 240, "line_total_price": 12000},
                {"sku_name": "Vim Liquid Gel (750ml)", "qty": 200, "net_unit_price": 105, "line_total_price": 21000},
                {"sku_name": "Surf Excel Matic Top Load (2kg)", "qty": 20, "net_unit_price": 450, "line_total_price": 9000}
            ],
            "summary": {
                "subtotal": 54000,
                "tax_amount": 9720,
                "grand_total": 63720,
                "overall_margin_pct": 15.5
            }
        }

class MockSalesInsightsAgent:
    def process(self, *args, **kwargs):
        time.sleep(1)
        return {
            "risk_level": "Low",
            "win_probability_pct": 85,
            "competitor_analysis": [
                {"competitor_name": "P&G", "threat": "Aggressive discount on Ariel", "counter_strategy": "Bundle Surf Excel with Comfort"},
                {"competitor_name": "Dabur", "threat": "New organic shampoo launch", "counter_strategy": "Highlight chemical-free benefits of our premium range"}
            ]
        }

class MockBestProposalAgent:
    def process(self, *args, **kwargs):
        time.sleep(1)
        return {
            "content": """# Sales Proposal (SIMULATION)

**Client:** Simulated Client Ltd
**Date:** 2025-12-25
**Valid Until:** 2026-01-25

## Commercial Summary
We are pleased to offer the following commercial terms for your restocking request.

| Item | Qty | Unit Price | Total |
|------|-----|------------|-------|
| Sunsilk Black Shine | 100 | ₹120 | ₹12,000 |
| Dove Intense Repair | 50 | ₹240 | ₹12,000 |
| Vim Liquid Gel | 200 | ₹105 | ₹21,000 |
| Surf Excel Matic | 20 | ₹450 | ₹9,000 |

**Subtotal:** ₹54,000
**GST (18%):** ₹9,720
**Grand Total:** ₹63,720

## Next Steps
Please sign and return this document to process the dispatch immediately.
"""
        }
