import os
import json
import logging
from typing import Dict, Any, List
from utils.gemini_wrapper import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default FMCG Volume Discount Tiers
DEFAULT_DISCOUNT_TIERS = [
    (5000, 0.18),
    (1000, 0.14),
    (500, 0.10),
    (200, 0.065),
    (50, 0.030),
    (0, 0.000)
]

# Category GST slabs
CATEGORY_GST_SLABS = {
    "Dairy & Staples": 5.0,
    "Beverages": 12.0,
    "Packaged Foods": 12.0,
    "Home Care": 18.0,
    "Personal Care": 18.0,
    "Oral Care": 18.0,
    "Stationery": 12.0
}


class PricingAgent:
    def __init__(self, model_name: str = None, rules_path: str = None):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.llm = GeminiLLM(model_name=self.model_name)
        self.rules = self._load_rules(rules_path)
        logger.info(f"FMCG Pricing Agent initialized with model: {self.model_name}")

    def _load_rules(self, rules_path: str = None) -> Dict[str, Any]:
        candidates = [
            rules_path,
            "data/pricing_rules.json",
            "rfp-automation/data/pricing_rules.json",
            os.path.join(os.path.dirname(__file__), "..", "data", "pricing_rules.json")
        ]
        for p in candidates:
            if p and os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Error loading pricing rules from {p}: {e}")
        return {}

    def get_volume_discount_pct(self, quantity: int) -> float:
        """Calculate volume discount percentage based on order quantity"""
        tiers = self.rules.get("volume_discount_tiers", [])
        if tiers:
            for t in sorted(tiers, key=lambda x: x.get("min_units", 0), reverse=True):
                if quantity >= t.get("min_units", 0):
                    return float(t.get("discount_pct", 0.0))
        
        for min_q, disc in DEFAULT_DISCOUNT_TIERS:
            if quantity >= min_q:
                return disc * 100.0
        return 0.0

    def get_gst_rate(self, category: str) -> float:
        """Get GST rate by product category"""
        slabs = self.rules.get("gst_category_slabs", {})
        if category in slabs:
            return float(slabs[category].get("gst_pct", 18.0))
        return CATEGORY_GST_SLABS.get(category, 18.0)

    async def process_async(self, rfp_data: Dict[str, Any], sku_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculates FMCG commercial quote with tiered volume discounts and category GST.
        """
        print("   [PricingAgent] Calculating FMCG Commercial Quote...")

        matches = []
        if sku_data and isinstance(sku_data, dict):
            matches = sku_data.get("matches", [])
        
        if not matches and rfp_data and rfp_data.get("line_items"):
            for li in rfp_data.get("line_items", []):
                matches.append({
                    "matched_sku_name": li.get("description") or li.get("item_name", "FMCG Item"),
                    "matched_sku_code": "PENDING",
                    "category": li.get("category_hint", "General FMCG"),
                    "quantity": li.get("quantity", 24),
                    "base_cost": 120.0,
                    "gst_pct": 18.0
                })

        pricing_table = []
        total_gross_mrp = 0.0
        total_discount_amount = 0.0
        total_taxable_subtotal = 0.0
        total_gst_amount = 0.0

        for match in matches:
            sku_name = match.get("matched_sku_name") or match.get("original_desc", "Item")
            sku_code = match.get("matched_sku_code", "GEN-001")
            category = match.get("category", "Personal Care")
            qty = max(1, int(match.get("quantity", 10)))
            base_cost = float(match.get("base_cost", 100.0) or 100.0)

            # 1. Base unit list price (Distributor rate)
            discount_pct = self.get_volume_discount_pct(qty)
            unit_discount = base_cost * (discount_pct / 100.0)
            net_unit_price = round(base_cost - unit_discount, 2)
            line_subtotal = round(net_unit_price * qty, 2)

            # 2. Category GST
            gst_pct = float(match.get("gst_pct") or self.get_gst_rate(category))
            line_gst = round(line_subtotal * (gst_pct / 100.0), 2)
            line_total = round(line_subtotal + line_gst, 2)

            line_gross = round(base_cost * qty, 2)
            line_discount = round(unit_discount * qty, 2)

            total_gross_mrp += line_gross
            total_discount_amount += line_discount
            total_taxable_subtotal += line_subtotal
            total_gst_amount += line_gst

            pricing_table.append({
                "sku_code": sku_code,
                "sku_name": sku_name,
                "category": category,
                "qty": qty,
                "unit": match.get("unit", "units"),
                "unit_price_base": base_cost,
                "discount_pct": discount_pct,
                "discount_amount": line_discount,
                "net_unit_price": net_unit_price,
                "gst_pct": gst_pct,
                "gst_amount": line_gst,
                "line_taxable_price": line_subtotal,
                "line_total_price": line_total
            })

        grand_total = round(total_taxable_subtotal + total_gst_amount, 2)
        overall_margin_pct = 18.5  # Standard distributor margin baseline

        summary = {
            "gross_mrp_value": round(total_gross_mrp, 2),
            "total_discount_amount": round(total_discount_amount, 2),
            "subtotal": round(total_taxable_subtotal, 2),
            "taxable_value": round(total_taxable_subtotal, 2),
            "cgst_amount": round(total_gst_amount / 2, 2),
            "sgst_amount": round(total_gst_amount / 2, 2),
            "tax_amount": round(total_gst_amount, 2),
            "grand_total": grand_total,
            "overall_margin_pct": overall_margin_pct,
            "savings_percentage": round((total_discount_amount / total_gross_mrp * 100), 1) if total_gross_mrp > 0 else 0.0
        }

        return {
            "pricing_table": pricing_table,
            "summary": summary
        }

    def process(self, rfp_data: Dict[str, Any], sku_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sync wrapper for compatibility"""
        import asyncio
        return asyncio.run(self.process_async(rfp_data, sku_data))
