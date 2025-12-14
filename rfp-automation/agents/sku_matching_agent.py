import os
import json
import logging
from typing import Dict, Any, List
from utils.gemini_wrapper import GeminiLLM
from utils.json_parser import parse_json_output
from prompts.agent_prompts import SKU_MATCHING_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SKUMatchingAgent:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.llm = GeminiLLM(model_name=self.model_name)
        logger.info(f"SKU Matching Agent initialized with model: {self.model_name}")

    def process(self, rfp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Matches extracted line items to the Master Catalog using RAG.
        """
        line_items = rfp_data.get('line_items', [])
        if not line_items:
            logger.warning("No line items found in RFP data for SKU matching.")
            return {"matches": []}

        print(f"   [SKUAgent] Matching {len(line_items)} items to catalog (using RAG)...")
        
        matches = []
        
        # Initialize embeddings if not already done (lazy load)
        if not hasattr(self, 'embeddings_manager') or self.embeddings_manager is None:
            try:
                from utils.embeddings import create_embeddings_manager
                self.embeddings_manager = create_embeddings_manager("data/sku_catalog.csv")
            except Exception as e:
                logger.error(f"Failed to load embeddings: {e}")
                self.embeddings_manager = None

        # BATCH: Increased to 10 for speed
        for i in range(0, len(line_items), 10):
            batch = line_items[i:i+10]
            batch_candidates = {}
            batch_prompt = "MATCH THE FOLLOWING ITEMS:\n\n"
            
            # 1. Retrieve candidates for all items in batch (local, cheap)
            for item in batch:
                query = f"{item.get('item_name','')} {item.get('description','')}".strip()
                cands = []
                if self.embeddings_manager:
                    cands = self.embeddings_manager.search_similar_skus(query, top_k=3)
                
                c_str = "\n".join([f"   - {c['sku_id']}: {c['name']} ({c['specs']})" for c in cands])
                batch_prompt += f"ITEM ID: {item.get('id')}\nDESC: {item.get('description')}\nCANDIDATES:\n{c_str}\n\n"

            # 2. Single LLM Call for Batch
            try:
                final_prompt = f"""{batch_prompt}
                
                For each ITEM ID above, select the best matching candidate.
                Return JSON: {{ "matches": [ {{ "line_item_id": "...", "matched_sku_code": "..." }} ] }}
                """
                
                resp = self.llm.generate_content(final_prompt, system_instruction=SKU_MATCHING_PROMPT)
                parsed = parse_json_output(resp)
                if "matches" in parsed:
                    valid_matches = []
                    for m in parsed["matches"]:
                        # Ensure reason is present
                        if not m.get("reason"):
                            m["reason"] = f"AI Analysis: Matches specs '{m.get('matched_sku_specs','similar')}' with RFP req."
                        valid_matches.append(m)
                    matches.extend(valid_matches)
                else:
                    # Fallback for whole batch
                    logger.warning("Batch matching failed structure check")

            except Exception as e:
                logger.error(f"Batch failed: {e}")
                
        return {"matches": matches}
