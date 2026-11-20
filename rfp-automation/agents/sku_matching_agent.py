import os
import csv
import re
import json
import logging
from typing import Dict, Any, List, Optional
from utils.gemini_wrapper import GeminiLLM
from utils.json_parser import parse_json_output
from utils.uom_normalizer import normalize_quantity
from prompts.agent_prompts import SKU_MATCHING_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _tokenize(text: str) -> set:
    """Normalize text into lowercase alphanumeric tokens"""
    clean = re.sub(r"[^\w\s]", " ", (text or "").lower())
    return {w for w in clean.split() if len(w) > 1}


class SKUMatchingAgent:
    def __init__(self, model_name: str = None, catalog_path: str = None):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.llm = GeminiLLM(model_name=self.model_name)
        self.catalog_items = self._load_catalog(catalog_path)
        logger.info(f"SKU Matching Agent initialized with model: {self.model_name}, {len(self.catalog_items)} catalog items")

    def _load_catalog(self, catalog_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load catalog CSV into memory with token sets for fast local matching"""
        candidates = [
            catalog_path,
            "data/sku_catalog.csv",
            "rfp-automation/data/sku_catalog.csv",
            os.path.join(os.path.dirname(__file__), "..", "data", "sku_catalog.csv")
        ]
        
        valid_path = None
        for p in candidates:
            if p and os.path.exists(p):
                valid_path = p
                break
                
        if not valid_path:
            logger.warning("No catalog file found for SKU matching agent local fallback")
            return []

        items = []
        try:
            with open(valid_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("name", "")
                    specs = row.get("specs", "")
                    tokens = _tokenize(f"{name} {specs} {row.get('category', '')}")
                    items.append({
                        "sku_id": row.get("sku_id", ""),
                        "name": name,
                        "category": row.get("category", ""),
                        "specs": specs,
                        "base_cost": float(row.get("base_cost", 0.0) or 0.0),
                        "unit": row.get("unit", "unit"),
                        "gst_pct": float(row.get("gst_pct", 18.0) or 18.0),
                        "pack_size": row.get("pack_size", "standard"),
                        "tokens": tokens
                    })
        except Exception as e:
            logger.error(f"Error loading catalog CSV: {e}")

        return items

    def match_local(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Fast deterministic token-overlap & fuzzy matcher"""
        if not self.catalog_items:
            return []

        q_tokens = _tokenize(query)
        if not q_tokens:
            return []

        scored = []
        for item in self.catalog_items:
            overlap = len(q_tokens.intersection(item["tokens"]))
            if overlap == 0:
                continue

            jaccard = overlap / len(q_tokens.union(item["tokens"]))
            # Bonus for exact brand name matches in query
            brand_bonus = 0.2 if any(brand in query.lower() for brand in ["surf excel", "dove", "sunsilk", "vim", "maggi", "amul", "tata", "colgate", "britannia", "dabur"]) else 0.0
            score = min(1.0, (jaccard * 0.8) + brand_bonus + (overlap * 0.05))

            scored.append({
                "sku_id": item["sku_id"],
                "name": item["name"],
                "category": item["category"],
                "specs": item["specs"],
                "base_cost": item["base_cost"],
                "unit": item["unit"],
                "gst_pct": item["gst_pct"],
                "confidence": round(score, 3)
            })

        scored.sort(key=lambda x: x["confidence"], reverse=True)
        return scored[:top_k]

    async def process_async(self, rfp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Matches extracted line items to Master Catalog using hybrid RAG + Local Matching"""
        import asyncio
        
        line_items = rfp_data.get('line_items', [])
        if not line_items:
            logger.warning("No line items found in RFP data for SKU matching.")
            return {"matches": []}

        print(f"   [SKUAgent] Matching {len(line_items)} items to catalog (Hybrid Async)...")

        # Lazy load embeddings manager if possible
        if not hasattr(self, 'embeddings_manager') or self.embeddings_manager is None:
            try:
                from utils.embeddings import create_embeddings_manager
                self.embeddings_manager = await asyncio.to_thread(create_embeddings_manager, "rfp-automation/data/sku_catalog.csv")
            except Exception as e:
                logger.info(f"Embeddings manager not available ({e}), using local hybrid catalog matcher")
                self.embeddings_manager = None

        matches = []
        batch_size = 10
        tasks = []

        for i in range(0, len(line_items), batch_size):
            batch = line_items[i:i + batch_size]
            tasks.append(self._process_batch_async(batch))

        results = await asyncio.gather(*tasks)
        for batch_matches in results:
            matches.extend(batch_matches)

        print(f"   [SKUAgent] Completed {len(matches)}/{len(line_items)} SKU matches.")
        return {"matches": matches}

    def process(self, rfp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wrapper for compatibility"""
        import asyncio
        return asyncio.run(self.process_async(rfp_data))

    async def _process_batch_async(self, batch: List[Dict]) -> List[Dict]:
        """Process a single batch asynchronously with robust local fallback"""
        batch_matches = []
        batch_prompt = "MATCH THE FOLLOWING ITEMS:\n\n"
        local_candidates_map = {}

        for item in batch:
            raw_desc = item.get('description', '') or item.get('item_name', '')
            query = f"{item.get('item_name', '')} {raw_desc} {item.get('specifications', '')}".strip()

            cands = []
            if self.embeddings_manager:
                try:
                    cands = self.embeddings_manager.search_similar_skus(query, top_k=3)
                except Exception:
                    cands = []

            if not cands:
                cands = self.match_local(query, top_k=3)

            local_candidates_map[str(item.get('id', ''))] = cands

            c_str = "\n".join([f"   - {c.get('sku_id')}: {c.get('name')} ({c.get('specs', '')})" for c in cands])
            batch_prompt += f"ITEM ID: {item.get('id')}\nDESC: {raw_desc}\nCANDIDATES:\n{c_str}\n\n"

        # Try LLM candidate ranking
        parsed = {}
        try:
            final_prompt = f"""{batch_prompt}

For each ITEM ID above, select the best matching candidate SKU.
Return JSON: {{ "matches": [ {{ "line_item_id": "...", "matched_sku_code": "...", "reason": "..." }} ] }}
"""
            resp = await self.llm.generate_content_async(final_prompt, system_instruction=SKU_MATCHING_PROMPT)
            parsed = parse_json_output(resp)
        except Exception as e:
            logger.warning(f"Batch LLM matching error: {e}. Falling back to deterministic matcher.")

        llm_matched_dict = {}
        if isinstance(parsed, dict) and "matches" in parsed and isinstance(parsed["matches"], list):
            for m in parsed["matches"]:
                lid = str(m.get("line_item_id", ""))
                llm_matched_dict[lid] = m

        # Merge LLM match with local metadata
        for item in batch:
            lid = str(item.get("id", ""))
            raw_desc = item.get("description", "") or item.get("item_name", "Item")
            qty_info = normalize_quantity(item.get("quantity", 10), item.get("unit", ""), raw_desc)
            
            cands = local_candidates_map.get(lid, [])
            best_cand = cands[0] if cands else None

            llm_match = llm_matched_dict.get(lid)
            matched_code = llm_match.get("matched_sku_code") if llm_match else None

            # Find candidate info by code if provided
            matched_cand = None
            if matched_code:
                for c in cands:
                    if c.get("sku_id") == matched_code:
                        matched_cand = c
                        break

            chosen = matched_cand or best_cand

            if chosen:
                conf = round(chosen.get("confidence", 0.90), 2)
                reason = (llm_match.get("reason") if llm_match else "") or f"High semantic and spec alignment with {chosen['name']}"
                batch_matches.append({
                    "line_item_id": lid,
                    "original_desc": raw_desc,
                    "matched_sku_code": chosen["sku_id"],
                    "matched_sku_name": chosen["name"],
                    "category": chosen.get("category", "General FMCG"),
                    "matched_sku_details": f"Base Cost: ₹{chosen.get('base_cost', 0)} | Unit: {chosen.get('unit')} | GST: {chosen.get('gst_pct', 18)}%",
                    "match_confidence_score": conf,
                    "quantity": qty_info["normalized_units"],
                    "raw_quantity": qty_info["raw_quantity"],
                    "unit": qty_info["consumer_unit"],
                    "packaging_type": qty_info["packaging_type"],
                    "base_cost": chosen.get("base_cost", 0.0),
                    "gst_pct": chosen.get("gst_pct", 18.0),
                    "reason": reason,
                    "is_ambiguous": conf < 0.65
                })
            else:
                batch_matches.append({
                    "line_item_id": lid,
                    "original_desc": raw_desc,
                    "matched_sku_code": None,
                    "matched_sku_name": "Unmatched FMCG Product",
                    "category": "Uncategorized",
                    "matched_sku_details": "No matching SKU in catalog",
                    "match_confidence_score": 0.0,
                    "quantity": qty_info["normalized_units"],
                    "raw_quantity": qty_info["raw_quantity"],
                    "unit": qty_info["consumer_unit"],
                    "packaging_type": qty_info["packaging_type"],
                    "base_cost": 100.0,
                    "gst_pct": 18.0,
                    "reason": "Item not found in current catalog",
                    "is_ambiguous": True
                })

        return batch_matches
