import os
import json
import logging
from typing import Dict, Any
from utils.gemini_wrapper import GeminiLLM
from utils.json_parser import parse_json_output
from prompts.agent_prompts import PRICING_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PricingAgent:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.llm = GeminiLLM(model_name=self.model_name)
        logger.info(f"FMCG Pricing Agent initialized with model: {self.model_name}")
    
    async def process_async(self, rfp_data: Dict[str, Any], sku_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculates pricing for the matched SKUs in batches (Async/Parallel).
        """
        import asyncio
        print(f"   [PricingAgent] Calculating Quote (Batched/Async)...")

        matches = sku_data.get('matches', []) if sku_data else []
        if not matches and rfp_data and rfp_data.get('line_items'):
             matches = []
             for li in rfp_data.get('line_items', []):
                 matches.append({
                     "matched_sku_name": li.get('description'), 
                     "matched_sku_code": "PENDING",
                     "quantity": li.get('quantity', 10)
                 })

        all_pricing_rows = []
        batch_size = 10
        tasks = []
        
        for i in range(0, len(matches), batch_size):
            batch = matches[i:i+batch_size]
            tasks.append(self._process_batch_async(batch))
            
        results = await asyncio.gather(*tasks)
        for r in results:
            all_pricing_rows.extend(r)
        
        # Recalculate Totals Locally
        grand_subtotal = 0.0
        for row in all_pricing_rows:
            grand_subtotal += row.get('line_total_price', 0)
            
        total_tax = grand_subtotal * 0.18
        final_total = grand_subtotal + total_tax

        return {
            "pricing_table": all_pricing_rows,
            "summary": {
                "subtotal": grand_subtotal,
                "total_discount_amount": 0,
                "tax_amount": total_tax,
                "grand_total": final_total,
                "overall_margin_pct": 20  # Simulated margin for insights
            }
        }
        
    def process(self, rfp_data: Dict[str, Any], sku_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sync wrapper"""
        import asyncio
        return asyncio.run(self.process_async(rfp_data, sku_data))

    async def _process_batch_async(self, batch: list) -> list:
        rows = []
        items_context = ""
        
        for item in batch:
            name = item.get('matched_sku_name')
            if not name: name = item.get('original_desc', 'Unknown')
            code = item.get('matched_sku_code', 'N/A')
            qty = item.get('quantity')
            if not qty: qty = 10
            
            items_context += f"- SKU: {code} | Name: {name} | Qty: {qty}\n"

        prompt = f"""You are the FMCG Pricing Agent.
        
        INPUT BATCH:
        {items_context}
        
        Calculate the Invoice for these items using the PRICING LOGIC.
        Return ONLY a JSON Array of objects. Do not wrap in a 'pricing_table' key.
        Example:
        [
          {{ "sku_name": "...", "qty": 10, "unit_price_base": 100, "net_unit_price": 95, "line_total_price": 950 }}
        ]
        """
        try:
            # print(f"   [DEBUG] Sending batch of {len(batch)} items to Pricing Model...")
            response_text = await self.llm.generate_content_async(prompt, system_instruction=PRICING_PROMPT)
            parsed = parse_json_output(response_text)
            
            if isinstance(parsed, list):
                rows.extend(parsed)
            elif isinstance(parsed, dict):
                if "pricing_table" in parsed:
                    rows.extend(parsed["pricing_table"])
                elif "items" in parsed: 
                    rows.extend(parsed["items"])
                else:
                    # heuristic extract
                    for k, v in parsed.items():
                        if isinstance(v, list):
                            rows.extend(v)
                            break
                    if not rows and ("sku_name" in parsed or "unit_price" in parsed):
                        rows.append(parsed)
            
        except Exception as e:
            logger.error(f"Pricing batch failed: {e}")
            
        return rows