"""
FMCG Mock Agents for Offline Simulation Mode
Allows running the complete agentic pipeline with zero external API dependencies.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any


class MockIntakeAgent:
    async def process_async(self, rfp_text: str = "", *args, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return self._generate_data(rfp_text)

    def process(self, rfp_text: str = "", *args, **kwargs) -> Dict[str, Any]:
        return self._generate_data(rfp_text)

    def _generate_data(self, rfp_text: str) -> Dict[str, Any]:
        return {
            "client_name": "Metro Cash & Carry Wholesale Hub",
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "deadline": "Within 5 business days",
            "location": "Central Distribution Center, Bhiwandi",
            "line_items": [
                {"id": "1", "item_name": "Surf Excel Matic Top Load 2kg", "description": "Surf Excel Matic Top Load 2kg powder", "quantity": 120, "unit": "packs", "category_hint": "Home Care"},
                {"id": "2", "item_name": "Dove Hair Fall Rescue 340ml", "description": "Dove Hair Fall Rescue Shampoo 340ml", "quantity": 240, "unit": "bottles", "category_hint": "Personal Care"},
                {"id": "3", "item_name": "Vim Dishwash Gel 750ml", "description": "Vim Lemon Dishwash Gel 750ml", "quantity": 300, "unit": "bottles", "category_hint": "Home Care"},
                {"id": "4", "item_name": "Maggi 2-Minute Noodles 560g", "description": "Maggi 2-Minute Masala Instant Noodles 8-Pack", "quantity": 180, "unit": "packs", "category_hint": "Packaged Foods"},
                {"id": "5", "item_name": "Nescafe Classic Coffee Jar 100g", "description": "Nescafe Classic Instant Coffee Jar 100g", "quantity": 150, "unit": "jars", "category_hint": "Beverages"},
                {"id": "6", "item_name": "Aashirvaad Pure Cow Ghee 1L", "description": "Aashirvaad Svasti Pure Cow Ghee 1L Tin", "quantity": 80, "unit": "tins", "category_hint": "Dairy & Staples"}
            ],
            "is_relevant": True,
            "priority_score": 92
        }


class MockSKUMatchingAgent:
    async def process_async(self, rfp_data: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return self._generate_matches(rfp_data)

    def process(self, rfp_data: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        return self._generate_matches(rfp_data)

    def _generate_matches(self, rfp_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "matches": [
                {
                    "line_item_id": "1",
                    "original_desc": "Surf Excel Matic Top Load 2kg powder",
                    "matched_sku_code": "HUL_SURF_001",
                    "matched_sku_name": "Surf Excel Matic Top Load 2kg",
                    "category": "Home Care",
                    "matched_sku_details": "Base Cost: ₹480 | Pack: 2kg | Brand: Surf Excel",
                    "match_confidence_score": 0.98,
                    "quantity": 120,
                    "unit": "packs",
                    "base_cost": 480.0,
                    "gst_pct": 18.0,
                    "reason": "Exact match on brand variant and 2kg pack size",
                    "is_ambiguous": False
                },
                {
                    "line_item_id": "2",
                    "original_desc": "Dove Hair Fall Rescue Shampoo 340ml",
                    "matched_sku_code": "HUL_DOVE_001",
                    "matched_sku_name": "Dove Hair Fall Rescue Shampoo 340ml",
                    "category": "Personal Care",
                    "matched_sku_details": "Base Cost: ₹250 | Volume: 340ml | Brand: Dove",
                    "match_confidence_score": 0.95,
                    "quantity": 240,
                    "unit": "bottles",
                    "base_cost": 250.0,
                    "gst_pct": 18.0,
                    "reason": "Exact match on brand, hair fall rescue formula and 340ml size",
                    "is_ambiguous": False
                },
                {
                    "line_item_id": "3",
                    "original_desc": "Vim Lemon Dishwash Gel 750ml",
                    "matched_sku_code": "HUL_VIM_001",
                    "matched_sku_name": "Vim Dishwash Gel 750ml",
                    "category": "Home Care",
                    "matched_sku_details": "Base Cost: ₹155 | Volume: 750ml | Brand: Vim",
                    "match_confidence_score": 0.96,
                    "quantity": 300,
                    "unit": "bottles",
                    "base_cost": 155.0,
                    "gst_pct": 18.0,
                    "reason": "Exact size and formulation match",
                    "is_ambiguous": False
                },
                {
                    "line_item_id": "4",
                    "original_desc": "Maggi 2-Minute Masala Instant Noodles 8-Pack",
                    "matched_sku_code": "NES_MAG_001",
                    "matched_sku_name": "Maggi 2-Minute Masala Instant Noodles 560g (8-Pack)",
                    "category": "Packaged Foods",
                    "matched_sku_details": "Base Cost: ₹112 | Weight: 560g | Brand: Maggi",
                    "match_confidence_score": 0.94,
                    "quantity": 180,
                    "unit": "packs",
                    "base_cost": 112.0,
                    "gst_pct": 12.0,
                    "reason": "High confidence match for 8-pack masala variant",
                    "is_ambiguous": False
                },
                {
                    "line_item_id": "5",
                    "original_desc": "Nescafe Classic Instant Coffee Jar 100g",
                    "matched_sku_code": "NES_NES_001",
                    "matched_sku_name": "Nescafe Classic Instant Coffee Jar 100g",
                    "category": "Beverages",
                    "matched_sku_details": "Base Cost: ₹330 | Weight: 100g | Brand: Nescafe",
                    "match_confidence_score": 0.95,
                    "quantity": 150,
                    "unit": "jars",
                    "base_cost": 330.0,
                    "gst_pct": 18.0,
                    "reason": "Exact 100g glass jar match",
                    "is_ambiguous": False
                },
                {
                    "line_item_id": "6",
                    "original_desc": "Aashirvaad Svasti Pure Cow Ghee 1L Tin",
                    "matched_sku_code": "ITC_ASH_003",
                    "matched_sku_name": "Aashirvaad Svasti Pure Cow Ghee 1L",
                    "category": "Dairy & Staples",
                    "matched_sku_details": "Base Cost: ₹650 | Volume: 1L | Brand: Aashirvaad",
                    "match_confidence_score": 0.92,
                    "quantity": 80,
                    "unit": "tins",
                    "base_cost": 650.0,
                    "gst_pct": 5.0,
                    "reason": "Cow ghee 1L tin match",
                    "is_ambiguous": False
                }
            ]
        }


class MockPricingAgent:
    async def process_async(self, rfp_data: Dict[str, Any], sku_data: Dict[str, Any] = None, *args, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return self._generate_pricing()

    def process(self, *args, **kwargs) -> Dict[str, Any]:
        return self._generate_pricing()

    def _generate_pricing(self) -> Dict[str, Any]:
        return {
            "pricing_table": [
                {"sku_code": "HUL_SURF_001", "sku_name": "Surf Excel Matic Top Load 2kg", "category": "Home Care", "qty": 120, "unit": "packs", "unit_price_base": 480.0, "discount_pct": 3.0, "net_unit_price": 465.60, "gst_pct": 18.0, "gst_amount": 10056.96, "line_total_price": 65928.96},
                {"sku_code": "HUL_DOVE_001", "sku_name": "Dove Hair Fall Rescue Shampoo 340ml", "category": "Personal Care", "qty": 240, "unit": "bottles", "unit_price_base": 250.0, "discount_pct": 6.5, "net_unit_price": 233.75, "gst_pct": 18.0, "gst_amount": 10098.00, "line_total_price": 66198.00},
                {"sku_code": "HUL_VIM_001", "sku_name": "Vim Dishwash Gel 750ml", "category": "Home Care", "qty": 300, "unit": "bottles", "unit_price_base": 155.0, "discount_pct": 6.5, "net_unit_price": 144.92, "gst_pct": 18.0, "gst_amount": 7825.68, "line_total_price": 51301.68},
                {"sku_code": "NES_MAG_001", "sku_name": "Maggi 2-Minute Masala Instant Noodles 560g", "category": "Packaged Foods", "qty": 180, "unit": "packs", "unit_price_base": 112.0, "discount_pct": 3.0, "net_unit_price": 108.64, "gst_pct": 12.0, "gst_amount": 2346.62, "line_total_price": 21901.82},
                {"sku_code": "NES_NES_001", "sku_name": "Nescafe Classic Instant Coffee Jar 100g", "category": "Beverages", "qty": 150, "unit": "jars", "unit_price_base": 330.0, "discount_pct": 3.0, "net_unit_price": 320.10, "gst_pct": 18.0, "gst_amount": 8642.70, "line_total_price": 56657.70},
                {"sku_code": "ITC_ASH_003", "sku_name": "Aashirvaad Svasti Pure Cow Ghee 1L", "category": "Dairy & Staples", "qty": 80, "unit": "tins", "unit_price_base": 650.0, "discount_pct": 3.0, "net_unit_price": 630.50, "gst_pct": 5.0, "gst_amount": 2522.00, "line_total_price": 52962.00}
            ],
            "summary": {
                "gross_mrp_value": 330760.00,
                "total_discount_amount": 15286.00,
                "subtotal": 315474.00,
                "taxable_value": 315474.00,
                "tax_amount": 41491.96,
                "grand_total": 356965.96,
                "overall_margin_pct": 18.5,
                "savings_percentage": 4.6
            }
        }


class MockSalesInsightsAgent:
    async def process_async(self, *args, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return self._generate_insights()

    def process(self, *args, **kwargs) -> Dict[str, Any]:
        return self._generate_insights()

    def _generate_insights(self) -> Dict[str, Any]:
        return {
            "win_probability_pct": 84,
            "confidence_level": "High",
            "risk_level": "Low",
            "risks": [
                {
                    "type": "supply_chain",
                    "description": "High quantity of Cow Ghee (80 tins) requires cold-chain certified transport",
                    "severity": "low",
                    "mitigation": "Dispatch via temperature-monitored refrigerated vehicle"
                }
            ],
            "competitors": ["P&G Distribution", "ITC Direct Trade", "Nestlé Direct", "Dabur Network"],
            "strengths": [
                "Full category catalog match across Home, Personal & Foods",
                "Tier-2 volume discount applied (saving client ₹15,286)",
                "Guaranteed >85% shelf life on all consumables",
                "Express 48-hour delivery SLA"
            ],
            "recommendations": [
                "Recommend bundling Dove conditioner with the 240 shampoo units for +8% margin",
                "Offer 2% additional prompt payment rebate for Net 15 days settlement"
            ],
            "deal_scorecard": {
                "catalog_fit_score": 96,
                "commercial_viability_score": 88,
                "fulfillment_speed_score": 92,
                "overall_deal_grade": "A"
            }
        }


class MockBestProposalAgent:
    async def process_async(self, *args, **kwargs) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return {"content": self._generate_markdown()}

    def process(self, *args, **kwargs) -> Dict[str, Any]:
        return {"content": self._generate_markdown()}

    def _generate_markdown(self) -> str:
        return """# FMCG Commercial Supply Proposal & Quotation

**Client:** Metro Cash & Carry Wholesale Hub  
**Quotation Ref:** `FMCG-SIM-2026-001`  
**Date:** March 2026  
**Status:** Authorized Wholesale Rate Card  

---

## Executive Summary
We are pleased to present our official distributor quotation for your bulk replenishment order. All products are guaranteed 100% genuine, directly sourced from manufacturers with full warranty and minimum **>85% remaining shelf life**.

---

## Commercial Pricing Table

| SKU Name | Category | Qty | Net Unit Rate | GST | Line Total |
|:---|:---|:---:|:---:|:---:|:---:|
| Surf Excel Matic Top Load 2kg | Home Care | 120 packs | ₹465.60 | 18% | ₹65,928.96 |
| Dove Hair Fall Rescue Shampoo 340ml | Personal Care | 240 bottles | ₹233.75 | 18% | ₹66,198.00 |
| Vim Dishwash Gel 750ml | Home Care | 300 bottles | ₹144.92 | 18% | ₹51,301.68 |
| Maggi 2-Minute Noodles 560g | Packaged Foods | 180 packs | ₹108.64 | 12% | ₹21,901.82 |
| Nescafe Classic Coffee Jar 100g | Beverages | 150 jars | ₹320.10 | 18% | ₹56,657.70 |
| Aashirvaad Pure Cow Ghee 1L | Dairy & Staples | 80 tins | ₹630.50 | 5% | ₹52,962.00 |

---

## Financial Summary
- **Gross Order Value (List Price):** ₹330,760.00
- **Volume Discount Applied:** -₹15,286.00 (Tier 2 Volume Slab)
- **Taxable Order Subtotal:** ₹315,474.00
- **GST (CGST + SGST):** ₹41,491.96
- **Final Payable Amount:** **₹356,965.96**

---

## Key Terms
- **Payment:** Net 30 Days via RTGS / NEFT.
- **Dispatch:** Within 48 business hours post-PO confirmation.
- **Freight:** Free shipping threshold reached (>₹50,000).
- **Transit Insurance:** Fully insured by distributor.
"""
